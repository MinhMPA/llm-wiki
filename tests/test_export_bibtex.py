import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "init_llm_wiki.py"
EXPORT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "export_bibtex.py"


def source_record(record_id, title, status="active"):
    return "\n".join(
        [
            f"record_id: {record_id}",
            "record_type: source",
            f"status: {status}",
            "duplicate_of:",
            "superseded_by:",
            "source_storage: external",
            "source_url: https://arxiv.org/abs/1808.02002",
            "page_path:",
            "source_type: paper",
            "source_format: pdf",
            f"title: {title}",
            "authors: []",
            "added_date: 2026-05-18",
            "processed_date:",
            "published_date:",
            "content_fingerprint:",
            "arxiv_id: 1808.02002",
            "doi:",
            "bibtex_key:",
            "",
        ]
    )


def active_sidecar(record_id, bibtex_key):
    return "\n".join(
        [
            f"record_id: {record_id}",
            "record_type: bibtex",
            "status: active",
            "provider: manual",
            "provider_priority:",
            "providers_tried: []",
            "lookup_id:",
            f"bibtex_key: {bibtex_key}",
            "fetched_date: 2026-05-18",
            f"source_bib_path: wiki_records/bibtex/{record_id}.bib",
            "",
        ]
    )


def unresolved_sidecar(record_id):
    return "\n".join(
        [
            f"record_id: {record_id}",
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
    )


class PreparedExportWiki:
    def __init__(self, status_1="active", status_2="active", key_1="AKey", key_2="BKey", unresolved=False):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "wiki"
        subprocess.run([sys.executable, str(INIT_SCRIPT), str(self.path)], check=True, capture_output=True, text=True)
        sources = self.path / "wiki_records" / "sources"
        bibtex = self.path / "wiki_records" / "bibtex"
        sources.joinpath("SRC-0001.yaml").write_text(source_record("SRC-0001", "A", status=status_1), encoding="utf-8")
        sources.joinpath("SRC-0002.yaml").write_text(source_record("SRC-0002", "B", status=status_2), encoding="utf-8")
        if unresolved:
            bibtex.joinpath("SRC-0001.yaml").write_text(unresolved_sidecar("SRC-0001"), encoding="utf-8")
        else:
            bibtex.joinpath("SRC-0001.bib").write_text(f"@article{{{key_1},\n  title={{A}}\n}}\n", encoding="utf-8")
            bibtex.joinpath("SRC-0001.yaml").write_text(active_sidecar("SRC-0001", key_1), encoding="utf-8")
            bibtex.joinpath("SRC-0002.bib").write_text(f"@article{{{key_2},\n  title={{B}}\n}}\n", encoding="utf-8")
            bibtex.joinpath("SRC-0002.yaml").write_text(active_sidecar("SRC-0002", key_2), encoding="utf-8")

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type, exc, tb):
        self.temp_dir.cleanup()


def prepared_wiki_with_two_active_bibtex_entries(key_1="AKey", key_2="BKey"):
    return PreparedExportWiki(key_1=key_1, key_2=key_2)


def prepared_wiki_with_unresolved_bibtex_sidecar():
    return PreparedExportWiki(unresolved=True)


def prepared_wiki_with_bibtex_for_archived_source():
    return PreparedExportWiki(status_1="archived", status_2="archived", key_1="AKey", key_2="BKey")


def run_export(wiki, *args):
    return subprocess.run([sys.executable, str(EXPORT_SCRIPT), str(wiki), *args], capture_output=True, text=True, check=False)


class TestExportBibtex(unittest.TestCase):
    def test_dry_run_reports_references_export_ordered_by_record_id(self):
        with prepared_wiki_with_two_active_bibtex_entries() as wiki:
            result = run_export(wiki)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("would write", result.stdout)
            self.assertIn("2 entries", result.stdout)

    def test_apply_writes_references_bib(self):
        with prepared_wiki_with_two_active_bibtex_entries() as wiki:
            result = run_export(wiki, "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            references = (wiki / "wiki_records" / "bibtex" / "references.bib").read_text(encoding="utf-8")
            self.assertLess(references.index("@article{AKey,"), references.index("@article{BKey,"))

    def test_export_rejects_duplicate_keys(self):
        with prepared_wiki_with_two_active_bibtex_entries(key_1="SameKey", key_2="SameKey") as wiki:
            result = run_export(wiki)
            self.assertEqual(result.returncode, 1)
            self.assertIn("duplicate BibTeX key", result.stderr)

    def test_export_skips_unresolved_sidecars(self):
        with prepared_wiki_with_unresolved_bibtex_sidecar() as wiki:
            result = run_export(wiki)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("0 entries", result.stdout)

    def test_export_skips_nonactive_sources(self):
        with prepared_wiki_with_bibtex_for_archived_source() as wiki:
            result = run_export(wiki)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("0 entries", result.stdout)

    def test_external_output_path_writes_only_requested_file(self):
        with prepared_wiki_with_two_active_bibtex_entries() as wiki:
            external = wiki.parent / "draft" / "references.bib"
            external.parent.mkdir()
            result = run_export(wiki, "--output", str(external), "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(external.exists())
            self.assertFalse((wiki / "wiki_records" / "bibtex" / "references.bib").exists())
