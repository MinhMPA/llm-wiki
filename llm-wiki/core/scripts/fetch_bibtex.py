#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

from bibtex_support import (
    extract_bibtex_key,
    is_eligible_bibtex_source,
    normalize_bibtex_entry,
    rewrite_bibtex_key,
    source_identifier_candidates,
)
from validate_wiki import parse_simple_yaml, scalar_value


def read_yaml_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data, errors = parse_simple_yaml(text, path.as_posix())
    if errors:
        raise ValueError("; ".join(errors))
    return data


def load_source_records(root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "wiki_records" / "sources").glob("*.yaml"), key=lambda item: item.name):
        data = read_yaml_file(path)
        record_id = scalar_value(data, "record_id")
        if record_id:
            records[record_id] = data
    return records


def load_sidecar(root: Path, record_id: str) -> dict[str, Any] | None:
    path = root / "wiki_records" / "bibtex" / f"{record_id}.yaml"
    if not path.is_file():
        return None
    return read_yaml_file(path)


def inspire_bibtex_url(lookup_id: str) -> str:
    query = urllib.parse.urlencode({"q": lookup_id, "format": "bibtex"})
    return f"https://inspirehep.net/api/literature?{query}"


def ads_bibtex_url(lookup_id: str) -> str:
    query = urllib.parse.urlencode({"q": lookup_id, "fl": "bibcode"})
    return f"https://api.adsabs.harvard.edu/v1/search/query?{query}"


def fetch_from_inspire(lookup_id: str) -> str | None:
    with urllib.request.urlopen(inspire_bibtex_url(lookup_id), timeout=30) as response:
        text = response.read().decode("utf-8")
    return normalize_bibtex_entry(text) if text.strip() else None


def fetch_from_ads(lookup_id: str, token: str) -> str | None:
    request = urllib.request.Request(ads_bibtex_url(lookup_id), headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        text = response.read().decode("utf-8")
    return normalize_bibtex_entry(text) if text.strip() else None


def selected_record_ids(root: Path, records: dict[str, dict[str, Any]], args: argparse.Namespace) -> list[str]:
    if args.record_id:
        return [args.record_id]
    if args.all or args.missing:
        selected = []
        for record_id, data in sorted(records.items()):
            if not is_eligible_bibtex_source(data):
                continue
            sidecar = load_sidecar(root, record_id)
            if args.missing and sidecar is not None:
                if scalar_value(sidecar, "status") == "unresolved" and args.retry_unresolved:
                    selected.append(record_id)
                continue
            selected.append(record_id)
        return selected
    raise ValueError("provide a source record ID, --all, or --missing")


def sidecar_text(
    record_id: str,
    status: str,
    provider: str,
    provider_priority: str,
    providers_tried: list[str],
    lookup_id: str,
    bibtex_key: str,
    source_bib_path: str,
) -> str:
    lines = [
        f"record_id: {record_id}",
        "record_type: bibtex",
        f"status: {status}",
        f"provider: {provider}",
        f"provider_priority: {provider_priority}",
        "providers_tried:",
    ]
    lines.extend(f"  - {provider_name}" for provider_name in providers_tried)
    lines.extend(
        [
            f"lookup_id: {lookup_id}",
            f"bibtex_key: {bibtex_key}",
            f"fetched_date: {date.today().isoformat()}",
            f"source_bib_path: {source_bib_path}",
            "",
        ]
    )
    return "\n".join(lines)


def fetch_for_source(root: Path, record_id: str, data: dict[str, Any], apply: bool) -> tuple[int, str, str]:
    bibtex_dir = root / "wiki_records" / "bibtex"
    bib_path = bibtex_dir / f"{record_id}.bib"
    sidecar_path = bibtex_dir / f"{record_id}.yaml"
    if bib_path.exists() and not sidecar_path.exists():
        return 1, "", f"{record_id}: orphan BibTeX file has no sidecar record\n"
    if not is_eligible_bibtex_source(data):
        return 0, f"{record_id}: skipped; source is not an active paper with an identifier\n", ""

    candidates = source_identifier_candidates(data)
    providers_tried: list[str] = []
    ads_token = os.environ.get("ADS_API_TOKEN", "")
    for lookup_id in candidates:
        providers_tried.append("inspire")
        bibtex_entry = fetch_from_inspire(lookup_id)
        if bibtex_entry:
            return write_or_report(root, record_id, data, "inspire", "1", providers_tried, lookup_id, bibtex_entry, apply)
        if ads_token:
            providers_tried.append("ads")
            bibtex_entry = fetch_from_ads(lookup_id, ads_token)
            if bibtex_entry:
                return write_or_report(root, record_id, data, "ads", "2", providers_tried, lookup_id, bibtex_entry, apply)

    unresolved = sidecar_text(record_id, "unresolved", "", "", providers_tried, candidates[0] if candidates else "", "", "")
    if apply:
        sidecar_path.write_text(unresolved, encoding="utf-8")
        return 1, "", f"{record_id}: unresolved\n"
    return 1, "", f"{record_id}: unresolved\n"


def write_or_report(
    root: Path,
    record_id: str,
    data: dict[str, Any],
    provider: str,
    provider_priority: str,
    providers_tried: list[str],
    lookup_id: str,
    bibtex_entry: str,
    apply: bool,
) -> tuple[int, str, str]:
    bibtex_key = scalar_value(data, "bibtex_key") or extract_bibtex_key(bibtex_entry)
    if scalar_value(data, "bibtex_key"):
        bibtex_entry = rewrite_bibtex_key(bibtex_entry, bibtex_key)
    else:
        bibtex_entry = normalize_bibtex_entry(bibtex_entry)
    source_bib_path = f"wiki_records/bibtex/{record_id}.bib"
    sidecar = sidecar_text(record_id, "active", provider, provider_priority, providers_tried, lookup_id, bibtex_key, source_bib_path)

    if not apply:
        return 0, f"{record_id}: would write {source_bib_path} from {provider}\n", ""

    bibtex_dir = root / "wiki_records" / "bibtex"
    bibtex_dir.mkdir(parents=True, exist_ok=True)
    (bibtex_dir / f"{record_id}.bib").write_text(bibtex_entry, encoding="utf-8")
    (bibtex_dir / f"{record_id}.yaml").write_text(sidecar, encoding="utf-8")
    return 0, f"{record_id}: wrote {source_bib_path} from {provider}\n", ""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch canonical BibTeX entries for LLM Wiki paper sources.")
    parser.add_argument("wiki_root", type=Path)
    parser.add_argument("record_id", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--missing", action="store_true")
    parser.add_argument("--retry-unresolved", action="store_true")
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        records = load_source_records(args.wiki_root)
        record_ids = selected_record_ids(args.wiki_root, records, args)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.missing and not args.retry_unresolved:
        for record_id, data in sorted(records.items()):
            if not is_eligible_bibtex_source(data):
                continue
            sidecar = load_sidecar(args.wiki_root, record_id)
            if sidecar is not None and scalar_value(sidecar, "status") == "unresolved":
                print(f"{record_id}: skipped unresolved")

    exit_code = 0
    for record_id in record_ids:
        data = records.get(record_id)
        if data is None:
            print(f"{record_id}: unknown source record", file=sys.stderr)
            exit_code = 1
            continue
        code, stdout, stderr = fetch_for_source(args.wiki_root, record_id, data, args.apply)
        if stdout:
            print(stdout, end="")
        if stderr:
            print(stderr, end="", file=sys.stderr)
        exit_code = max(exit_code, code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
