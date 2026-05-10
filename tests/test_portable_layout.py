import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestPortableLayout(unittest.TestCase):
    def test_core_files_exist(self):
        required = [
            "llm-wiki/core/README.md",
            "llm-wiki/core/references/workflows.md",
            "llm-wiki/core/references/page-contracts.md",
            "llm-wiki/core/references/record-contracts.md",
            "llm-wiki/core/references/validation.md",
            "llm-wiki/core/references/advanced-workflows.md",
        ]
        for path in required:
            self.assertTrue((ROOT / path).exists(), path)

    def test_adapters_are_thin_and_point_to_core(self):
        for path in [
            "llm-wiki/adapters/codex/SKILL.md",
            "llm-wiki/adapters/claude/SKILL.md",
        ]:
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("llm-wiki", text)
            self.assertIn("../../core/README.md", text)
            self.assertIn("../../core/references/workflows.md", text)
            self.assertNotIn("WIKI_SCHEMA_PROPOSALS.md is optional", text)

    def test_core_documents_define_required_concepts(self):
        readme = (ROOT / "llm-wiki/core/README.md").read_text(encoding="utf-8")
        records = (ROOT / "llm-wiki/core/references/record-contracts.md").read_text(encoding="utf-8")
        pages = (ROOT / "llm-wiki/core/references/page-contracts.md").read_text(encoding="utf-8")

        self.assertIn("WIKI_SCHEMA.md", readme)
        self.assertIn("wiki_records/", readme)
        self.assertIn("record_id", records)
        self.assertIn("source_type", records)
        self.assertIn("Source Record Citations", pages)

    def test_core_contract_quality_constraints(self):
        records = (ROOT / "llm-wiki/core/references/record-contracts.md").read_text(encoding="utf-8")
        advanced = (ROOT / "llm-wiki/core/references/advanced-workflows.md").read_text(encoding="utf-8")

        self.assertIn("`raw_path` is required when `source_storage` is `local` and must point under `raw/`.", records)
        self.assertNotIn("Future plugin packaging", advanced)
        self.assertNotIn("plugin packaging", advanced)
