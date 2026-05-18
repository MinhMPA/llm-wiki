import contextlib
import importlib.util
import io
import json
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
VALIDATOR = ROOT / "llm-wiki" / "core" / "scripts" / "validate_wiki.py"


def load_fetch_module():
    scripts_dir = str(FETCH_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
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


def prepared_wiki_with_arxiv_and_doi_source():
    wiki_context = PreparedWiki()
    record = wiki_context.path / "wiki_records" / "sources" / "SRC-0001.yaml"
    text = record.read_text(encoding="utf-8")
    record.write_text(text.replace("doi:\n", "doi: 10.1234/example\n"), encoding="utf-8")
    return wiki_context


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


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload.encode("utf-8")


class TestFetchBibtex(unittest.TestCase):
    def test_single_source_dry_run_reports_inspire_match(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            result = run_fetch_with_fake_provider(wiki, "SRC-0001", "@article{Example:2018,\n  title={Example}\n}\n")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("would write", result.stdout)
            self.assertFalse((wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").exists())

    def test_apply_writes_bib_and_sidecar_for_inspire_result(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            result = run_fetch_with_fake_provider(
                wiki,
                "SRC-0001",
                "@article{Example:2018,\n  title={Example}\n}\n",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").exists())
            sidecar = (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").read_text(encoding="utf-8")
            self.assertIn("provider: inspire", sidecar)
            self.assertIn("providers_tried:\n  - inspire", sidecar)

    def test_fetch_uses_ads_when_inspire_misses_and_token_exists(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            env = os.environ.copy()
            env["ADS_API_TOKEN"] = "token"
            result = run_fetch_with_provider_sequence(
                wiki,
                "SRC-0001",
                [None, "@article{AdsKey,\n  title={Example}\n}\n"],
                "--apply",
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            sidecar = (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").read_text(encoding="utf-8")
            self.assertIn("provider: ads", sidecar)
            self.assertIn("  - inspire\n  - ads", sidecar)

    def test_ads_provider_searches_bibcode_then_exports_bibtex(self):
        module = load_fetch_module()
        calls = []

        def fake_urlopen(request, timeout):
            calls.append(request)
            url = request.full_url
            if "/v1/search/query" in url:
                return FakeResponse(json.dumps({"response": {"docs": [{"bibcode": "2019JCAP...01..042S"}]}}))
            if "/v1/export/bibtex" in url:
                self.assertEqual(json.loads(request.data.decode("utf-8")), {"bibcode": ["2019JCAP...01..042S"]})
                return FakeResponse(json.dumps({"export": "@article{AdsKey,\n  title={Example}\n}\n"}))
            raise AssertionError(url)

        with mock.patch.object(module.urllib.request, "urlopen", side_effect=fake_urlopen):
            result = module.fetch_from_ads("arxiv:1808.02002", "token")

        self.assertEqual(result, "@article{AdsKey,\n  title={Example}\n}\n")
        self.assertEqual(len(calls), 2)
        self.assertIn("/v1/search/query", calls[0].full_url)
        self.assertIn("/v1/export/bibtex", calls[1].full_url)

    def test_missing_ads_token_skips_ads_and_reports_unresolved(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            env = os.environ.copy()
            env.pop("ADS_API_TOKEN", None)
            result = run_fetch_with_provider_sequence(wiki, "SRC-0001", [None], "--apply", env=env)
            self.assertEqual(result.returncode, 1)
            sidecar = (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").read_text(encoding="utf-8")
            self.assertIn("status: unresolved", sidecar)
            self.assertIn("providers_tried:\n  - inspire", sidecar)
            self.assertNotIn("  - ads", sidecar)

    def test_multi_identifier_retry_writes_validator_clean_provider_list(self):
        with prepared_wiki_with_arxiv_and_doi_source() as wiki:
            module = load_fetch_module()
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch.object(
                    module,
                    "fetch_from_inspire",
                    side_effect=[None, "@article{DoiKey,\n  title={Example}\n}\n"],
                ):
                    result = call_main(module, [str(wiki), "SRC-0001", "--apply"])
            self.assertEqual(result.returncode, 0, result.stderr)
            sidecar = (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").read_text(encoding="utf-8")
            self.assertEqual(sidecar.count("  - inspire"), 1)

            validate = subprocess.run(
                [sys.executable, str(VALIDATOR), str(wiki)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stderr)

    def test_missing_mode_skips_existing_sidecars_without_retry(self):
        with prepared_wiki_with_unresolved_sidecar() as wiki:
            result = run_fetch(wiki, "--missing")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("skipped unresolved", result.stdout)

    def test_retry_unresolved_retries_unresolved_sidecar(self):
        with prepared_wiki_with_unresolved_sidecar() as wiki:
            result = run_fetch_with_fake_provider(
                wiki,
                "--missing",
                "--retry-unresolved",
                "@article{Retry:2018,\n  title={Example}\n}\n",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "Retry:2018",
                (wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").read_text(encoding="utf-8"),
            )

    def test_manual_orphan_bib_file_is_reported_but_not_inferred(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            (wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").write_text(
                "@article{Manual:2018,\n  title={Manual}\n}\n",
                encoding="utf-8",
            )
            result = run_fetch(wiki, "SRC-0001", "--apply")
            self.assertEqual(result.returncode, 1)
            self.assertIn("orphan BibTeX file", result.stderr)
            self.assertFalse((wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").exists())

    def test_bibtex_key_override_rewrites_entry_key(self):
        with prepared_wiki_with_active_arxiv_source(bibtex_key="PreferredKey") as wiki:
            result = run_fetch_with_fake_provider(
                wiki,
                "SRC-0001",
                "@article{ProviderKey,\n  title={Example}\n}\n",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "@article{PreferredKey,",
                (wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").read_text(encoding="utf-8"),
            )

    def test_provider_failure_reports_error_without_traceback(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            module = load_fetch_module()
            with mock.patch.object(module, "fetch_from_inspire", side_effect=OSError("network down")):
                result = call_main(module, [str(wiki), "SRC-0001"])

            self.assertEqual(result.returncode, 1)
            self.assertIn("fetch failed", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_all_mode_continues_after_provider_failure(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            record = wiki / "wiki_records" / "sources" / "SRC-0002.yaml"
            record.write_text(
                (wiki / "wiki_records" / "sources" / "SRC-0001.yaml")
                .read_text(encoding="utf-8")
                .replace("SRC-0001", "SRC-0002")
                .replace("1808.02002", "2401.01234"),
                encoding="utf-8",
            )
            module = load_fetch_module()
            with mock.patch.object(
                module,
                "fetch_from_inspire",
                side_effect=[OSError("network down"), "@article{SecondKey,\n  title={Second}\n}\n"],
            ):
                result = call_main(module, [str(wiki), "--all", "--apply"])

            self.assertEqual(result.returncode, 1)
            self.assertIn("SRC-0001: fetch failed", result.stderr)
            self.assertTrue((wiki / "wiki_records" / "bibtex" / "SRC-0002.bib").exists())
