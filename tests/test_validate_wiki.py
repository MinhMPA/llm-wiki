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


def write_relation_record(wiki, filename, text):
    path = wiki / "wiki_records" / "relations" / filename
    path.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")
    return path


def write_source_page(wiki, path, record_id, title, body="Summary."):
    page = wiki / path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        f"""---
record_id: {record_id}
page_type: source_summary
title: {title}
aliases: []
tags:
  - source
---

# {title}

{body}
""",
        encoding="utf-8",
    )
    return page


def write_processed_source(wiki, record_id, title, page_slug, status="active", duplicate_of="", superseded_by=""):
    write_source_record(
        wiki,
        f"{record_id}.yaml",
        f"""
        record_id: {record_id}
        record_type: source
        status: {status}
        duplicate_of: {duplicate_of}
        superseded_by: {superseded_by}
        source_storage: external
        source_url: https://example.com/{record_id.lower()}
        page_path: wiki_pages/sources/{page_slug}.md
        source_type: paper
        source_format: pdf
        title: {title}
        authors: []
        added_date: 2026-05-11
        processed_date: 2026-05-11
        published_date:
        content_fingerprint:
        """,
    )
    write_source_page(wiki, f"wiki_pages/sources/{page_slug}.md", record_id, title)


def write_valid_relation(wiki, relation_id="REL-0001", relation_type="cites", status="active"):
    write_relation_record(
        wiki,
        f"{relation_id}.yaml",
        f"""
        record_id: {relation_id}
        record_type: relation
        status: {status}
        source_record_id: SRC-0001
        target_record_id: SRC-0002
        relation_type: {relation_type}
        direction: source_to_target
        evidence: []
        created_date: 2026-05-16
        reviewed_date:
        confidence: high
        """,
    )


def setup_related_sources(wiki, body=None):
    write_processed_source(wiki, "SRC-0001", "Field Level Inference", "field-level-inference")
    write_processed_source(wiki, "SRC-0002", "Survey Data Release", "survey-data-release")
    if body is not None:
        write_source_page(wiki, "wiki_pages/sources/field-level-inference.md", "SRC-0001", "Field Level Inference", body)


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

    def test_source_record_unknown_field_fails(self):
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
                source_type: article
                title: Source With Tags
                authors: []
                added_date: 2026-05-11
                tags: []
                """,
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported source record field: tags", result.stderr)

    def test_source_record_accepts_bibliography_identifier_fields(self):
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
                source_url: https://arxiv.org/abs/1808.02002v2
                source_type: paper
                title: Example Paper
                authors: []
                added_date: 2026-05-18
                arxiv_id: 1808.02002v2
                doi: 10.1234/example
                bibtex_key: Example:2018
                """,
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 0, result.stderr)

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

    def test_wiki_page_without_frontmatter_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            page = wiki / "wiki_pages" / "concepts" / "missing-frontmatter.md"
            page.write_text("# Missing Frontmatter\n\nBody.\n", encoding="utf-8")

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("frontmatter is required", result.stderr)

    def test_source_record_page_path_must_point_to_source_summary_file(self):
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
                page_path: wiki_pages/sources
                source_type: article
                title: Directory Page Path
                authors: []
                added_date: 2026-05-11
                processed_date: 2026-05-11
                """,
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("page_path must point to a file", result.stderr)

    def test_source_record_page_path_must_be_source_summary(self):
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
                page_path: wiki_pages/concepts/not-summary.md
                source_type: article
                title: Wrong Page Type
                authors: []
                added_date: 2026-05-11
                processed_date: 2026-05-11
                """,
            )
            page = wiki / "wiki_pages" / "concepts" / "not-summary.md"
            page.write_text(
                """---
page_type: concept
title: Wrong Page Type
aliases: []
tags: []
---

Body.
""",
                encoding="utf-8",
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("page_path must point to a source_summary page", result.stderr)

    def test_source_record_page_path_frontmatter_record_id_must_match(self):
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
                page_path: wiki_pages/sources/wrong-id.md
                source_type: article
                title: Wrong ID
                authors: []
                added_date: 2026-05-11
                processed_date: 2026-05-11
                """,
            )
            write_source_page(wiki, "wiki_pages/sources/wrong-id.md", "SRC-9999", "Wrong ID")

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("page_path frontmatter record_id must match", result.stderr)

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

    def test_valid_relation_record_with_matching_managed_link_passes(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(
                wiki,
                """Summary.

## Related sources

### Cites
- [[sources/survey-data-release|Survey Data Release]] (`REL-0001`)
""",
            )
            write_valid_relation(wiki)

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_relation_record_unknown_field_notes_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(
                wiki,
                """Summary.

## Related sources

### Cites
- [[sources/survey-data-release|Survey Data Release]] (`REL-0001`)
""",
            )
            write_valid_relation(wiki)
            relation = wiki / "wiki_records" / "relations" / "REL-0001.yaml"
            relation.write_text(relation.read_text(encoding="utf-8") + "notes: no prose here\n", encoding="utf-8")

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported relation record field: notes", result.stderr)

    def test_relation_record_evidence_scalar_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(wiki)
            write_valid_relation(wiki)
            relation = wiki / "wiki_records" / "relations" / "REL-0001.yaml"
            relation.write_text(relation.read_text(encoding="utf-8").replace("evidence: []", "evidence: scalar"), encoding="utf-8")

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("evidence must be a list", result.stderr)

    def test_relation_record_controlled_values_fail(self):
        cases = [
            ("status: active", "status: pending", "status must be one of"),
            ("relation_type: cites", "relation_type: unclear", "relation_type must be one of"),
            ("direction: source_to_target", "direction: target_to_source", "direction must be source_to_target"),
            ("confidence: high", "confidence: certain", "confidence must be one of"),
            ("created_date: 2026-05-16", "created_date: 2026-02-31", "created_date must be YYYY-MM-DD"),
            ("reviewed_date:", "reviewed_date: 2026-02-31", "reviewed_date must be YYYY-MM-DD"),
        ]
        for old, new, expected in cases:
            with self.subTest(new=new):
                temp_dir, wiki = initialized_wiki()
                with temp_dir:
                    setup_related_sources(
                        wiki,
                        """Summary.

## Related sources

### Cites
- [[sources/survey-data-release|Survey Data Release]] (`REL-0001`)
""",
                    )
                    write_valid_relation(wiki)
                    relation = wiki / "wiki_records" / "relations" / "REL-0001.yaml"
                    relation.write_text(relation.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

                    result = run_validator(wiki)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn(expected, result.stderr)

    def test_relation_record_endpoint_rules_fail(self):
        cases = [
            ("target_record_id: SRC-0002", "target_record_id: SRC-9999", "target_record_id points to unknown source record"),
            ("source_record_id: SRC-0001", "source_record_id: SRC-9999", "source_record_id points to unknown source record"),
            ("target_record_id: SRC-0002", "target_record_id: SRC-0001", "source_record_id must not equal target_record_id"),
        ]
        for old, new, expected in cases:
            with self.subTest(new=new):
                temp_dir, wiki = initialized_wiki()
                with temp_dir:
                    setup_related_sources(wiki)
                    write_valid_relation(wiki)
                    relation = wiki / "wiki_records" / "relations" / "REL-0001.yaml"
                    relation.write_text(relation.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

                    result = run_validator(wiki)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn(expected, result.stderr)

    def test_active_relation_requires_source_and_target_pages(self):
        cases = [
            ("page_path: wiki_pages/sources/field-level-inference.md", "page_path:", "active relation source page is missing"),
            ("page_path: wiki_pages/sources/survey-data-release.md", "page_path:", "active relation target page is missing"),
        ]
        for old, new, expected in cases:
            with self.subTest(expected=expected):
                temp_dir, wiki = initialized_wiki()
                with temp_dir:
                    setup_related_sources(wiki)
                    write_valid_relation(wiki)
                    source_file = wiki / "wiki_records" / "sources" / ("SRC-0001.yaml" if "source" in expected else "SRC-0002.yaml")
                    source_file.write_text(source_file.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

                    result = run_validator(wiki)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn(expected, result.stderr)

    def test_managed_section_without_record_id_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_page(
                wiki,
                "wiki_pages/sources/orphan.md",
                "",
                "Orphan Source",
                """Summary.

## Related sources

### Cites
- [[sources/orphan|Orphan Source]] (`REL-9999`)
""",
            )
            page = wiki / "wiki_pages" / "sources" / "orphan.md"
            page.write_text(page.read_text(encoding="utf-8").replace("record_id: \n", ""), encoding="utf-8")

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Related sources section requires source_summary record_id", result.stderr)

    def test_active_relation_rejects_unrenderable_target_title(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(wiki)
            source = wiki / "wiki_records" / "sources" / "SRC-0002.yaml"
            source.write_text(source.read_text(encoding="utf-8").replace("title: Survey Data Release", "title: Survey ] Data"), encoding="utf-8")
            page = wiki / "wiki_pages" / "sources" / "survey-data-release.md"
            page.write_text(page.read_text(encoding="utf-8").replace("title: Survey Data Release", "title: Survey ] Data"), encoding="utf-8")
            write_valid_relation(wiki)

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("target title cannot render", result.stderr)

    def test_active_relation_missing_from_managed_section_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(wiki)
            write_valid_relation(wiki)

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing Related sources section", result.stderr)

    def test_managed_link_without_relation_record_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(
                wiki,
                """Summary.

## Related sources

### Cites
- [[sources/survey-data-release|Survey Data Release]] (`REL-9999`)
""",
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("no active relation record", result.stderr)

    def test_archived_relation_rendered_in_managed_section_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(
                wiki,
                """Summary.

## Related sources

### Cites
- [[sources/survey-data-release|Survey Data Release]] (`REL-0001`)
""",
            )
            write_valid_relation(wiki, status="archived")

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("archived relation is rendered", result.stderr)

    def test_managed_section_prose_fails(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(
                wiki,
                """Summary.

## Related sources

This prose is not managed.
""",
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("unmanaged content is not allowed", result.stderr)

    def test_processed_duplicate_requires_active_duplicates_relation(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_processed_source(wiki, "SRC-0001", "Duplicate Paper", "duplicate-paper", status="duplicate", duplicate_of="SRC-0002")
            write_processed_source(wiki, "SRC-0002", "Canonical Paper", "canonical-paper")

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("requires an active duplicates relation", result.stderr)

    def test_unprocessed_duplicate_without_relation_passes(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: duplicate
                duplicate_of: SRC-0002
                superseded_by:
                source_storage: external
                source_url: https://example.com/duplicate
                source_type: paper
                title: Duplicate Paper
                authors: []
                added_date: 2026-05-11
                """,
            )
            write_source_record(
                wiki,
                "SRC-0002.yaml",
                """
                record_id: SRC-0002
                record_type: source
                status: active
                source_storage: external
                source_url: https://example.com/canonical
                source_type: paper
                title: Canonical Paper
                authors: []
                added_date: 2026-05-11
                """,
            )

            result = run_validator(wiki)

            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
