import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / "llm-wiki" / "core" / "assets" / "starter-wiki"


class TestStarterWiki(unittest.TestCase):
    def test_required_paths_exist(self):
        required = [
            "WIKI_SCHEMA.md",
            "WIKI_SCHEMA_PROPOSALS.md",
            "AGENTS.md",
            "CLAUDE.md",
            "raw/.gitkeep",
            "wiki_records/sources/.gitkeep",
            "wiki_pages/index.md",
            "wiki_pages/log.md",
            "wiki_pages/questions.md",
            "wiki_pages/sources/.gitkeep",
            "wiki_pages/entities/.gitkeep",
            "wiki_pages/concepts/.gitkeep",
            "wiki_pages/synthesis/.gitkeep",
        ]
        for path in required:
            self.assertTrue((STARTER / path).exists(), path)

    def test_schema_has_fixed_top_level_sections(self):
        schema = (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8")
        headings = [line for line in schema.splitlines() if line.startswith("## ")]
        self.assertEqual(
            headings,
            [
                "## Purpose",
                "## Directory Layout",
                "## Page Types",
                "## Evidence And Citations",
                "## Ingest Workflow",
                "## Query Workflow",
                "## Lint Workflow",
                "## Naming Conventions",
                "## Review Policy",
                "## User Preferences",
                "## Schema Evolution",
            ],
        )

    def test_pointer_files_point_to_schema(self):
        for name in ["AGENTS.md", "CLAUDE.md"]:
            text = (STARTER / name).read_text(encoding="utf-8")
            self.assertIn("WIKI_SCHEMA.md", text)
            self.assertIn("source of truth", text)

    def test_schema_proposals_queue_exists(self):
        text = (STARTER / "WIKI_SCHEMA_PROPOSALS.md").read_text(encoding="utf-8")
        self.assertIn("# Wiki Schema Proposals", text)
        self.assertIn("## Pending", text)
        self.assertIn("## Approved", text)
        self.assertIn("## Rejected", text)
