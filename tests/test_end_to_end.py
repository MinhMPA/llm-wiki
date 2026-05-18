import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "init_llm_wiki.py"
VALIDATE_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "validate_wiki.py"
RENDER_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "render_relations.py"
EXPORT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "export_bibtex.py"


class TestEndToEnd(unittest.TestCase):
    def test_init_add_source_record_summary_and_validate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            init_result = subprocess.run(
                [sys.executable, str(INIT_SCRIPT), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            raw = target / "raw" / "example.md"
            raw.write_text("Example source text.", encoding="utf-8")

            record = target / "wiki_records" / "sources" / "SRC-0001.yaml"
            record.write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: source",
                        "status: active",
                        "duplicate_of:",
                        "superseded_by:",
                        "source_storage: local",
                        "raw_path: raw/example.md",
                        "source_url:",
                        "page_path: wiki_pages/sources/example.md",
                        "source_type: article",
                        "source_format: markdown",
                        "title: Example Source",
                        "authors: []",
                        "added_date: 2026-05-11",
                        "processed_date: 2026-05-11",
                        "published_date:",
                        "content_fingerprint:",
                    ]
                ),
                encoding="utf-8",
            )

            page = target / "wiki_pages" / "sources" / "example.md"
            page.write_text(
                "\n".join(
                    [
                        "---",
                        "record_id: SRC-0001",
                        "page_type: source_summary",
                        "title: Example Source",
                        "aliases: []",
                        "tags:",
                        "  - source",
                        "---",
                        "",
                        "# Example Source",
                        "",
                        "This source demonstrates a processed source summary.[^SRC-0001]",
                        "",
                        "[^SRC-0001]: `SRC-0001` - [[sources/example]]",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            index = target / "wiki_pages" / "index.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "No source summaries exist.",
                    "- [[sources/example]] - Example Source.",
                ),
                encoding="utf-8",
            )

            validate_result = subprocess.run(
                [sys.executable, str(VALIDATE_SCRIPT), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)

    def test_init_add_relation_render_and_validate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            init_result = subprocess.run(
                [sys.executable, str(INIT_SCRIPT), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            for record_id, title, slug in [
                ("SRC-0001", "Safe Sleep Guidance", "safe-sleep-guidance"),
                ("SRC-0002", "Hospital Discharge Checklist", "hospital-discharge-checklist"),
            ]:
                record = target / "wiki_records" / "sources" / f"{record_id}.yaml"
                record.write_text(
                    "\n".join(
                        [
                            f"record_id: {record_id}",
                            "record_type: source",
                            "status: active",
                            "duplicate_of:",
                            "superseded_by:",
                            "source_storage: external",
                            f"source_url: https://example.com/{slug}",
                            f"page_path: wiki_pages/sources/{slug}.md",
                            "source_type: documentation",
                            "source_format: html",
                            f"title: {title}",
                            "authors: []",
                            "added_date: 2026-05-16",
                            "processed_date: 2026-05-16",
                            "published_date:",
                            "content_fingerprint:",
                        ]
                    ),
                    encoding="utf-8",
                )
                page = target / "wiki_pages" / "sources" / f"{slug}.md"
                page.write_text(
                    "\n".join(
                        [
                            "---",
                            f"record_id: {record_id}",
                            "page_type: source_summary",
                            f"title: {title}",
                            "aliases: []",
                            "tags:",
                            "  - source",
                            "---",
                            "",
                            f"# {title}",
                            "",
                            "Summary.",
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )

            relation = target / "wiki_records" / "relations" / "REL-0001.yaml"
            relation.write_text(
                "\n".join(
                    [
                        "record_id: REL-0001",
                        "record_type: relation",
                        "status: active",
                        "source_record_id: SRC-0001",
                        "target_record_id: SRC-0002",
                        "relation_type: background_for",
                        "direction: source_to_target",
                        "evidence: []",
                        "created_date: 2026-05-16",
                        "reviewed_date:",
                        "confidence: high",
                    ]
                ),
                encoding="utf-8",
            )

            dry_run = subprocess.run(
                [sys.executable, str(RENDER_SCRIPT), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(dry_run.returncode, 1)
            self.assertIn("would update", dry_run.stderr)

            apply_result = subprocess.run(
                [sys.executable, str(RENDER_SCRIPT), str(target), "--apply"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            validate_result = subprocess.run(
                [sys.executable, str(VALIDATE_SCRIPT), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)

    def test_init_add_manual_bibtex_export_and_validate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            init_result = subprocess.run(
                [sys.executable, str(INIT_SCRIPT), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            record = target / "wiki_records" / "sources" / "SRC-0001.yaml"
            record.write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: source",
                        "status: active",
                        "duplicate_of:",
                        "superseded_by:",
                        "source_storage: external",
                        "source_url: https://arxiv.org/abs/1808.02002",
                        "page_path:",
                        "source_type: paper",
                        "source_format: pdf",
                        "title: Example Paper",
                        "authors: []",
                        "added_date: 2026-05-18",
                        "processed_date:",
                        "published_date:",
                        "content_fingerprint:",
                        "arxiv_id: 1808.02002",
                        "doi:",
                        "bibtex_key:",
                    ]
                ),
                encoding="utf-8",
            )
            (target / "wiki_records" / "bibtex" / "SRC-0001.bib").write_text(
                "@article{Example:2018,\n  title={Example}\n}\n",
                encoding="utf-8",
            )
            (target / "wiki_records" / "bibtex" / "SRC-0001.yaml").write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: bibtex",
                        "status: active",
                        "provider: manual",
                        "provider_priority:",
                        "providers_tried: []",
                        "lookup_id:",
                        "bibtex_key: Example:2018",
                        "fetched_date: 2026-05-18",
                        "source_bib_path: wiki_records/bibtex/SRC-0001.bib",
                    ]
                ),
                encoding="utf-8",
            )

            export_result = subprocess.run(
                [sys.executable, str(EXPORT_SCRIPT), str(target), "--apply"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(export_result.returncode, 0, export_result.stderr)

            validate_result = subprocess.run(
                [sys.executable, str(VALIDATE_SCRIPT), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
