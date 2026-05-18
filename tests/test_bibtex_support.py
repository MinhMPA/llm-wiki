from pathlib import Path
import importlib.util
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "llm-wiki" / "core" / "scripts" / "bibtex_support.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bibtex_support", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestBibtexSupport(unittest.TestCase):
    def test_normalize_arxiv_id_strips_version_suffix(self):
        module = load_module()
        self.assertEqual(module.normalize_arxiv_id("1808.02002v2"), "1808.02002")

    def test_source_identifier_candidates_prioritize_explicit_arxiv_then_doi(self):
        module = load_module()
        candidates = module.source_identifier_candidates(
            {
                "arxiv_id": "1808.02002v3",
                "doi": "10.1234/example",
                "source_url": "https://arxiv.org/abs/1808.02002v2",
            }
        )
        self.assertEqual(candidates, ["arxiv:1808.02002", "doi:10.1234/example"])

    def test_source_identifier_candidates_parse_arxiv_from_url_and_raw_path(self):
        module = load_module()
        candidates = module.source_identifier_candidates(
            {
                "source_url": "https://arxiv.org/pdf/2401.01234v1",
                "raw_path": "raw/SRC-0001/2401.01234v2.pdf",
            }
        )
        self.assertEqual(candidates, ["arxiv:2401.01234"])

    def test_extract_bibtex_key_reads_single_entry_key(self):
        module = load_module()
        key = module.extract_bibtex_key("@article{Schmidt:2018,\n  title={Example}\n}\n")
        self.assertEqual(key, "Schmidt:2018")

    def test_normalize_bibtex_entry_trims_and_ensures_final_newline(self):
        module = load_module()
        self.assertEqual(module.normalize_bibtex_entry("\n@article{A,\n}\n\n"), "@article{A,\n}\n")

    def test_rewrite_bibtex_key_replaces_only_entry_key(self):
        module = load_module()
        entry = "@article{ProviderKey,\n  title={ProviderKey appears here}\n}\n"
        self.assertEqual(
            module.rewrite_bibtex_key(entry, "PreferredKey"),
            "@article{PreferredKey,\n  title={ProviderKey appears here}\n}\n",
        )

    def test_is_eligible_source_requires_active_paper_with_identifier(self):
        module = load_module()
        self.assertTrue(
            module.is_eligible_bibtex_source(
                {"status": "active", "source_type": "paper", "arxiv_id": "1808.02002"}
            )
        )
        self.assertFalse(
            module.is_eligible_bibtex_source(
                {"status": "archived", "source_type": "paper", "arxiv_id": "1808.02002"}
            )
        )
        self.assertFalse(
            module.is_eligible_bibtex_source(
                {"status": "active", "source_type": "article", "arxiv_id": "1808.02002"}
            )
        )
        self.assertFalse(module.is_eligible_bibtex_source({"status": "active", "source_type": "paper"}))
