import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "init_llm_wiki.py"
VALIDATOR = ROOT / "llm-wiki" / "core" / "scripts" / "validate_wiki.py"


def run_init(target):
    return subprocess.run(
        [sys.executable, str(INIT_SCRIPT), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )


def run_validator(target):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )


def initialized_wiki():
    temp_dir = tempfile.TemporaryDirectory()
    wiki = Path(temp_dir.name) / "wiki"
    result = run_init(wiki)
    if result.returncode != 0:
        temp_dir.cleanup()
        raise AssertionError(result.stderr)
    return temp_dir, wiki


def write_source_record(wiki, filename, text):
    path = wiki / "wiki_records" / "sources" / filename
    path.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")
    return path


class TestValidateWiki(unittest.TestCase):
    def test_starter_wiki_is_valid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki = Path(temp_dir) / "wiki"
            init_result = run_init(wiki)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("valid", result.stdout)

    def test_schema_heading_order_is_enforced(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            schema = wiki / "WIKI_SCHEMA.md"
            text = schema.read_text(encoding="utf-8")
            schema.write_text(
                text.replace("## Directory Layout", "## Directory Layout Changed", 1),
                encoding="utf-8",
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Schema headings do not match", result.stderr)

    def test_invalid_source_record_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: local
                source_type: paper
                title: Missing Raw Path
                authors: []
                added_date: 2026-05-11
                """,
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("raw_path is required", result.stderr)

    def test_source_record_without_record_id_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_type: source
                status: active
                source_storage: external
                source_url: https://example.com/source
                source_type: article
                title: Missing Record ID
                authors: []
                added_date: 2026-05-11
                """,
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("record_id is required", result.stderr)

    def test_page_mirror_must_match_record(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://example.com/source
                page_path: wiki_pages/sources/SRC-0001-source.md
                source_type: article
                title: Canonical Title
                authors: []
                added_date: 2026-05-11
                processed_date: 2026-05-11
                """,
            )
            page = wiki / "wiki_pages" / "sources" / "SRC-0001-source.md"
            page.write_text(
                """---
record_id: SRC-0001
page_type: source_summary
title: Wrong Title
aliases: []
tags: []
---

Summary.
""",
                encoding="utf-8",
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("mirrored title", result.stderr)

    def test_source_record_citation_must_resolve(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            page = wiki / "wiki_pages" / "concepts" / "citation-test.md"
            page.write_text(
                """---
page_type: concept
title: Citation Test
aliases: []
tags: []
---

This cites a missing source.[^SRC-9999]

[^SRC-9999]: `SRC-9999` - [[sources/missing]]
""",
                encoding="utf-8",
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown source record citation", result.stderr)

    def test_missing_proposal_template_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            proposals = wiki / "WIKI_SCHEMA_PROPOSALS.md"
            text = proposals.read_text(encoding="utf-8")
            proposals.write_text(text.split("\n## Proposal Template", 1)[0] + "\n", encoding="utf-8")

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Proposal template is missing", result.stderr)

    def test_missing_proposal_template_label_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            proposals = wiki / "WIKI_SCHEMA_PROPOSALS.md"
            text = proposals.read_text(encoding="utf-8")
            proposals.write_text(text.replace("Change type:\n", "", 1), encoding="utf-8")

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Proposal template missing label: Change type:", result.stderr)

    def test_record_id_filename_mismatch_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0002.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://example.com/source
                source_type: article
                title: Mismatched Source
                authors: []
                added_date: 2026-05-11
                """,
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("record_id must match filename stem", result.stderr)

    def test_aliases_or_tags_scalar_frontmatter_fails(self):
        for field in ["aliases", "tags"]:
            with self.subTest(field=field):
                temp_dir, wiki = initialized_wiki()
                with temp_dir:
                    page = wiki / "wiki_pages" / "concepts" / f"{field}-scalar.md"
                    aliases = "scalar" if field == "aliases" else "[]"
                    tags = "scalar" if field == "tags" else "[]"
                    page.write_text(
                        f"""---
page_type: concept
title: Scalar {field}
aliases: {aliases}
tags: {tags}
---

Body.
""",
                        encoding="utf-8",
                    )

                    result = run_validator(wiki)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn(f"{field} must be a list", result.stderr)


if __name__ == "__main__":
    unittest.main()
