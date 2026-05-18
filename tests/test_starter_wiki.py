import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / "llm-wiki" / "core" / "assets" / "starter-wiki"


def parse_backtick_values(text, prefix):
    for line in text.splitlines():
        if line.startswith(prefix):
            return [part.split("`", 1)[0] for part in line.split("`")[1::2]]
    raise AssertionError(f"Missing line starting with {prefix!r}")


def fenced_yaml_after(text, marker):
    marker_index = text.index(marker)
    yaml_start = text.index("```yaml", marker_index) + len("```yaml")
    yaml_end = text.index("```", yaml_start)
    return text[yaml_start:yaml_end].strip()


def yaml_keys(yaml_text):
    keys = []
    for line in yaml_text.splitlines():
        if line and not line.startswith(" ") and ":" in line:
            keys.append(line.split(":", 1)[0])
    return keys


def section_between(text, start_heading, end_heading):
    start = text.index(start_heading)
    end = text.index(end_heading, start)
    return text[start:end]


def markdown_section(text, heading):
    start = text.index(heading)
    next_heading = text.find("\n## ", start + len(heading))
    if next_heading == -1:
        return text[start:]
    return text[start:next_heading]


class TestStarterWiki(unittest.TestCase):
    def test_required_paths_exist(self):
        required = [
            "WIKI_SCHEMA.md",
            "WIKI_SCHEMA_PROPOSALS.md",
            "AGENTS.md",
            "CLAUDE.md",
            "raw/.gitkeep",
            "wiki_records/sources/.gitkeep",
            "wiki_records/relations/.gitkeep",
            "wiki_records/bibtex/.gitkeep",
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
        source_yaml = fenced_yaml_after(schema, "A v1 source record uses this YAML contract:")
        self.assertEqual(
            yaml_keys(source_yaml),
            [
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
                "arxiv_id",
                "doi",
                "bibtex_key",
            ],
        )

        required_contract_terms = [
            "Source record files live under `wiki_records/sources/` as `.yaml` files.",
            "Source-summary pages live under `wiki_pages/sources/` as `.md` files.",
            "Tags are for `wiki_pages/` only and do not belong in canonical record YAML.",
            "[^SRC-0001]: `SRC-0001` - [[sources/example]]",
        ]
        for term in required_contract_terms:
            self.assertIn(term, schema)

    def test_schema_defines_bibliography_contract(self):
        schema = (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8")
        source_yaml = fenced_yaml_after(schema, "A v1 source record uses this YAML contract:")
        self.assertEqual(
            yaml_keys(source_yaml),
            [
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
                "arxiv_id",
                "doi",
                "bibtex_key",
            ],
        )
        self.assertIn("wiki_records/bibtex/", schema)
        self.assertIn("Bibliography workflow", schema)
        self.assertIn("record_type: bibtex", schema)

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
            parse_backtick_values(schema, "Controlled `status` values"),
            ["status", "active", "archived", "superseded", "duplicate"],
        )

        self.assertEqual(
            parse_backtick_values(schema, "Controlled `source_storage` values"),
            ["source_storage", "local", "external"],
        )

        self.assertEqual(
            parse_backtick_values(schema, "Controlled `source_type` values"),
            [
                "source_type",
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
            ],
        )

        self.assertEqual(
            parse_backtick_values(schema, "Controlled `source_format` values"),
            [
                "source_format",
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
            ],
        )

    def test_schema_defines_source_record_conditional_rules(self):
        schema = (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8")
        naming = markdown_section(schema, "## Naming Conventions")
        required_rules = [
            "`record_type` must be `source`",
            "`raw_path` is required when `source_storage` is `local`",
            "under `raw/`",
            "`source_url` is required when `source_storage` is `external`",
            "`processed_date` is required once `page_path` points to an existing source summary",
            "`duplicate_of` is required when `status` is `duplicate`",
            "`superseded_by` is required when `status` is `superseded`",
            "`content_fingerprint` may be blank",
            "`sha256:`",
            "`authors` is a list and may be empty",
        ]
        for rule in required_rules:
            self.assertIn(rule, naming)

    def test_schema_defines_page_contract(self):
        schema = (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8")
        page_yaml = fenced_yaml_after(schema, "Readable pages use minimal Obsidian-compatible frontmatter:")
        self.assertEqual(
            yaml_keys(page_yaml),
            ["record_id", "page_type", "title", "aliases", "tags"],
        )
        self.assertEqual(
            parse_backtick_values(schema, "Allowed page frontmatter fields are only "),
            ["record_id", "page_type", "title", "aliases", "tags"],
        )
        self.assertEqual(
            parse_backtick_values(schema, "Allowed `page_type` values"),
            [
                "page_type",
                "source_summary",
                "entity",
                "concept",
                "synthesis",
                "index",
                "log",
                "questions",
            ],
        )

    def test_schema_proposals_define_machine_checkable_block(self):
        text = (STARTER / "WIKI_SCHEMA_PROPOSALS.md").read_text(encoding="utf-8")
        lines = text.splitlines()
        pending = section_between(text, "## Pending", "## Approved")
        self.assertIn("No pending schema proposals.", pending)
        self.assertNotIn("### P-0001:", pending)
        self.assertNotIn("Status: Pending", pending)

        template = markdown_section(text, "## Proposal Template")
        self.assertIn("### P-NNNN:", template)
        self.assertNotIn("### P-0001:", template)
        for line in [
            "Status:",
            "Proposed by:",
            "Date:",
            "Change type:",
            "Affected schema sections:",
            "Human approval required:",
        ]:
            self.assertTrue(
                any(existing == line or existing.startswith(f"{line} ") for existing in template.splitlines()),
                line,
            )

        headings = {line for line in template.splitlines() if line.startswith("#### ")}
        self.assertEqual(
            headings,
            {
                "#### Proposed change",
                "#### Reason",
                "#### Why this is generic",
                "#### Approval notes",
            },
        )

    def test_schema_proposals_queue_exists(self):
        text = (STARTER / "WIKI_SCHEMA_PROPOSALS.md").read_text(encoding="utf-8")
        self.assertIn("# Wiki Schema Proposals", text)
        self.assertIn("## Pending", text)
        self.assertIn("## Approved", text)
        self.assertIn("## Rejected", text)
        self.assertIn("## Proposal Template", text)

    def test_schema_rejects_entry_specific_exception_rules(self):
        schema = (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8")
        evolution = markdown_section(schema, "## Schema Evolution")
        self.assertIn("Schema rules and subsections must stay generic.", evolution)
        self.assertIn(
            "Entry-specific exception rules do not belong in the schema.",
            evolution,
        )
        self.assertIn(
            "route it to human review as a question or schema proposal",
            evolution,
        )

    def test_forbidden_legacy_starter_paths_do_not_exist(self):
        forbidden = [
            "WIKI.md",
            "wiki",
        ]
        for path in forbidden:
            self.assertFalse((STARTER / path).exists(), path)
