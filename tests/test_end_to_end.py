import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "init_llm_wiki.py"
VALIDATE_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "validate_wiki.py"


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
