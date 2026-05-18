import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import textwrap
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
FETCH_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "fetch_bibtex.py"
INIT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "init_llm_wiki.py"


def load_fetch_module():
    spec = importlib.util.spec_from_file_location("fetch_bibtex", FETCH_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PreparedWiki:
    def __init__(self, bibtex_key=""):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "wiki"
        subprocess.run([sys.executable, str(INIT_SCRIPT), str(self.path)], check=True, capture_output=True, text=True)
        record = self.path / "wiki_records" / "sources" / "SRC-0001.yaml"
        record.write_text(
            textwrap.dedent(
                f"""
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://arxiv.org/abs/1808.02002v2
                page_path:
                source_type: paper
                source_format: pdf
                title: Example Paper
                authors: []
                added_date: 2026-05-18
                processed_date:
                published_date:
                content_fingerprint:
                arxiv_id: 1808.02002v2
                doi:
                bibtex_key: {bibtex_key}
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type, exc, tb):
        self.temp_dir.cleanup()


def prepared_wiki_with_active_arxiv_source(bibtex_key=""):
    return PreparedWiki(bibtex_key=bibtex_key)


def prepared_wiki_with_unresolved_sidecar():
    wiki_context = PreparedWiki()
    wiki = wiki_context.path
    sidecar = wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml"
    sidecar.write_text(
        "\n".join(
            [
                "record_id: SRC-0001",
                "record_type: bibtex",
                "status: unresolved",
                "provider:",
                "provider_priority:",
                "providers_tried:",
                "  - inspire",
                "lookup_id: arxiv:1808.02002",
                "bibtex_key:",
                "fetched_date: 2026-05-18",
                "source_bib_path:",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return wiki_context


def call_main(module, args):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        returncode = module.main(list(args))
    return types.SimpleNamespace(returncode=returncode, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def run_fetch_with_fake_provider(wiki, *args):
    module = load_fetch_module()
    bibtex_entry = next(arg for arg in args if isinstance(arg, str) and arg.startswith("@"))
    cli_args = [str(wiki), *[arg for arg in args if not (isinstance(arg, str) and arg.startswith("@"))]]
    with mock.patch.object(module, "fetch_from_inspire", return_value=bibtex_entry):
        return call_main(module, cli_args)


def run_fetch_with_provider_sequence(wiki, record_id, provider_results, *args, env=None):
    module = load_fetch_module()
    cli_args = [str(wiki), record_id, *args]
    with mock.patch.dict(os.environ, env or {}, clear=False):
        with mock.patch.object(module, "fetch_from_inspire", return_value=provider_results[0]):
            ads_result = provider_results[1] if len(provider_results) > 1 else None
            with mock.patch.object(module, "fetch_from_ads", return_value=ads_result):
                return call_main(module, cli_args)


def run_fetch(wiki, *args):
    module = load_fetch_module()
    return call_main(module, [str(wiki), *args])


class TestFetchBibtex(unittest.TestCase):
    def test_single_source_dry_run_reports_inspire_match(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            result = run_fetch_with_fake_provider(wiki, "SRC-0001", "@article{Example:2018,\n  title={Example}\n}\n")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("would write", result.stdout)
            self.assertFalse((wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").exists())

