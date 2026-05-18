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

