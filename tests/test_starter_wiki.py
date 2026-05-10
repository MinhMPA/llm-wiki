import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / "llm-wiki" / "core" / "assets" / "starter-wiki"


def parse_backtick_values(text, prefix):
    for line in text.splitlines():
        if line.startswith(prefix):
            return [part.split("`", 1)[0] for part in line.split("`")[1::2]]
    raise AssertionError(f"Missing line starting with {prefix!r}")


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

    def test_schema_defines_operational_source_contract(self):
        schema = (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8")
        yaml_fields = [
            "record_id",
            "record_type",
            "status",
            "duplicate_of",
            "superseded_by",
            "source_storage",
            "raw_path",
            "source_url",
            "page_path",
            "source_type",
            "source_format",
            "title",
            "authors",
            "added_date",
            "processed_date",
            "published_date",
            "content_fingerprint",
        ]
        for field in yaml_fields:
            self.assertIn(field, schema)

        required_contract_terms = [
            "`record_type` must be `source` for source records.",
            "Controlled `status` values are exactly `active`, `archived`, `superseded`, and `duplicate`.",
            "Controlled `source_storage` values are `local` and `external`.",
            "`local` source storage requires `raw_path` under `raw/`.",
            "`external` source storage requires `source_url`.",
            "Source record files live under `wiki_records/sources/` as `.yaml` files.",
            "Source-summary pages live under `wiki_pages/sources/` as `.md` files.",
            "Allowed page frontmatter fields are only `record_id`, `page_type`, `title`, `aliases`, and `tags`.",
            "Tags are for `wiki_pages/` only and do not belong in canonical record YAML.",
            "[^SRC-0001]: `SRC-0001` - [[sources/example]]",
            "Schema rules and subsections must stay generic.",
            "Entry-specific exception rules require human review and approval.",
        ]
        for term in required_contract_terms:
            self.assertIn(term, schema)

        self.assertEqual(
            parse_backtick_values(schema, "Required source record fields are "),
            [
                "record_id",
                "record_type",
                "status",
                "source_storage",
                "source_type",
                "title",
                "authors",
                "added_date",
            ],
        )

        self.assertEqual(
            parse_backtick_values(schema, "Allowed page frontmatter fields are only "),
            ["record_id", "page_type", "title", "aliases", "tags"],
        )

        for source_type in [
            "article",
            "paper",
            "book",
            "chapter",
            "transcript",
            "note",
            "image",
            "dataset",
            "video",
            "audio",
            "report",
            "documentation",
            "other",
        ]:
            self.assertIn(f"`{source_type}`", schema)

        for source_format in [
            "markdown",
            "pdf",
            "html",
            "text",
            "image",
            "audio",
            "video",
            "csv",
            "spreadsheet",
            "json",
            "yaml",
            "other",
        ]:
            self.assertIn(f"`{source_format}`", schema)

    def test_schema_defines_page_contract(self):
        schema = (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8")
        required_terms = [
            "record_id",
            "page_type",
            "title",
            "aliases",
            "tags",
            "`source_summary`",
            "`entity`",
            "`concept`",
            "`synthesis`",
            "`index`",
            "`log`",
            "`questions`",
        ]
        for term in required_terms:
            self.assertIn(term, schema)

    def test_schema_proposals_define_machine_checkable_block(self):
        text = (STARTER / "WIKI_SCHEMA_PROPOSALS.md").read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertTrue(any(line.startswith("### P-0001:") for line in lines))
        for line in [
            "Status:",
            "Proposed by:",
            "Date:",
            "Change type:",
            "Affected schema sections:",
            "Human approval required:",
        ]:
            self.assertTrue(
                any(existing == line or existing.startswith(f"{line} ") for existing in lines),
                line,
            )

        headings = [line for line in lines if line.startswith("#### ")]
        self.assertEqual(
            headings,
            [
                "#### Proposed change",
                "#### Reason",
                "#### Why this is generic",
                "#### Approval notes",
            ],
        )

    def test_schema_proposals_queue_exists(self):
        text = (STARTER / "WIKI_SCHEMA_PROPOSALS.md").read_text(encoding="utf-8")
        self.assertIn("# Wiki Schema Proposals", text)
        self.assertIn("## Pending", text)
        self.assertIn("## Approved", text)
        self.assertIn("## Rejected", text)

    def test_forbidden_legacy_starter_paths_do_not_exist(self):
        forbidden = [
            "WIKI.md",
            "wiki",
        ]
        for path in forbidden:
            self.assertFalse((STARTER / path).exists(), path)
