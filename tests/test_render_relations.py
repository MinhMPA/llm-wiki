import subprocess
import sys
import unittest
from pathlib import Path

from tests.test_validate_wiki import initialized_wiki, setup_related_sources, write_processed_source, write_relation_record, write_valid_relation


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "llm-wiki" / "core" / "scripts" / "render_relations.py"
VALIDATOR = ROOT / "llm-wiki" / "core" / "scripts" / "validate_wiki.py"


def run_renderer(wiki, *args):
    return subprocess.run(
        [sys.executable, str(RENDERER), str(wiki), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def run_validator(wiki):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(wiki)],
        capture_output=True,
        text=True,
        check=False,
    )


class TestRenderRelations(unittest.TestCase):
    def test_dry_run_reports_missing_section_and_does_not_edit(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(wiki)
            write_valid_relation(wiki)
            page = wiki / "wiki_pages" / "sources" / "field-level-inference.md"
            original = page.read_text(encoding="utf-8")

            result = run_renderer(wiki)

            self.assertEqual(result.returncode, 1)
            self.assertIn("would update: wiki_pages/sources/field-level-inference.md", result.stderr)
            self.assertEqual(page.read_text(encoding="utf-8"), original)

    def test_apply_inserts_grouped_managed_section(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(wiki)
            write_valid_relation(wiki)

            result = run_renderer(wiki, "--apply")

            self.assertEqual(result.returncode, 0, result.stderr)
            page = wiki / "wiki_pages" / "sources" / "field-level-inference.md"
            self.assertIn(
                """## Related sources

### Cites
- [[sources/survey-data-release|Survey Data Release]] (`REL-0001`)
""",
                page.read_text(encoding="utf-8"),
            )
            self.assertEqual(run_validator(wiki).returncode, 0)

    def test_apply_updates_stale_managed_section(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(
                wiki,
                """Summary.

## Related sources

### Cites
- [[sources/wrong|Wrong Label]] (`REL-9999`)
""",
            )
            write_valid_relation(wiki)

            result = run_renderer(wiki, "--apply")

            self.assertEqual(result.returncode, 0, result.stderr)
            page = wiki / "wiki_pages" / "sources" / "field-level-inference.md"
            text = page.read_text(encoding="utf-8")
            self.assertIn("[[sources/survey-data-release|Survey Data Release]] (`REL-0001`)", text)
            self.assertNotIn("REL-9999", text)

    def test_apply_removes_stale_section_when_no_active_relations_remain(self):
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

            result = run_renderer(wiki, "--apply")

            self.assertEqual(result.returncode, 0, result.stderr)
            page = wiki / "wiki_pages" / "sources" / "field-level-inference.md"
            self.assertNotIn("## Related sources", page.read_text(encoding="utf-8"))

    def test_groups_and_bullets_render_in_deterministic_order(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_processed_source(wiki, "SRC-0001", "Main Paper", "main-paper")
            write_processed_source(wiki, "SRC-0002", "Zeta Dataset", "zeta-dataset")
            write_processed_source(wiki, "SRC-0003", "Alpha Dataset", "alpha-dataset")
            write_relation_record(
                wiki,
                "REL-0002.yaml",
                """
                record_id: REL-0002
                record_type: relation
                status: active
                source_record_id: SRC-0001
                target_record_id: SRC-0002
                relation_type: uses_dataset
                direction: source_to_target
                evidence: []
                created_date: 2026-05-16
                reviewed_date:
                confidence: high
                """,
            )
            write_relation_record(
                wiki,
                "REL-0001.yaml",
                """
                record_id: REL-0001
                record_type: relation
                status: active
                source_record_id: SRC-0001
                target_record_id: SRC-0003
                relation_type: uses_dataset
                direction: source_to_target
                evidence: []
                created_date: 2026-05-16
                reviewed_date:
                confidence: high
                """,
            )

            result = run_renderer(wiki, "--apply")

            self.assertEqual(result.returncode, 0, result.stderr)
            text = (wiki / "wiki_pages" / "sources" / "main-paper.md").read_text(encoding="utf-8")
            self.assertLess(text.index("Alpha Dataset"), text.index("Zeta Dataset"))

    def test_refuses_unmanaged_prose_inside_existing_section(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            setup_related_sources(
                wiki,
                """Summary.

## Related sources

Manual prose.
""",
            )
            write_valid_relation(wiki)

            result = run_renderer(wiki, "--apply")

            self.assertEqual(result.returncode, 2)
            self.assertIn("unmanaged content is not allowed", result.stderr)


if __name__ == "__main__":
    unittest.main()
