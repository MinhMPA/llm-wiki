#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from bibtex_support import extract_bibtex_key, normalize_bibtex_entry
from validate_wiki import parse_simple_yaml, scalar_value


def read_yaml_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data, errors = parse_simple_yaml(text, path.as_posix())
    if errors:
        raise ValueError("; ".join(errors))
    return data


def load_records(directory: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    if not directory.is_dir():
        return records
    for path in sorted(directory.glob("*.yaml"), key=lambda item: item.name):
        data = read_yaml_file(path)
        record_id = scalar_value(data, "record_id")
        if record_id:
            records[record_id] = data
    return records


def export_entries(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    source_records = load_records(root / "wiki_records" / "sources")
    sidecars = load_records(root / "wiki_records" / "bibtex")
    entries: list[tuple[str, str, str]] = []
    seen_keys: dict[str, str] = {}

    for record_id in sorted(sidecars):
        sidecar = sidecars[record_id]
        source = source_records.get(record_id)
        if source is None:
            continue
        if scalar_value(source, "status") != "active":
            continue
        if scalar_value(sidecar, "status") != "active":
            continue

        bib_path = root / scalar_value(sidecar, "source_bib_path")
        if not bib_path.is_file():
            errors.append(f"{record_id}: missing BibTeX file: {scalar_value(sidecar, 'source_bib_path')}")
            continue
        entry = normalize_bibtex_entry(bib_path.read_text(encoding="utf-8"))
        key = extract_bibtex_key(entry)
        if key in seen_keys:
            errors.append(f"duplicate BibTeX key: {key} ({seen_keys[key]}, {record_id})")
            continue
        seen_keys[key] = record_id
        entries.append((record_id, key, entry))

    if errors:
        return [], errors
    return [entry for _record_id, _key, entry in sorted(entries, key=lambda item: item[0])], []


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export aggregate BibTeX for an LLM Wiki.")
    parser.add_argument("wiki_root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output = args.output or args.wiki_root / "wiki_records" / "bibtex" / "references.bib"
    entries, errors = export_entries(args.wiki_root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    content = "\n".join(entry.rstrip() for entry in entries)
    if content:
        content += "\n"

    if not args.apply:
        print(f"would write {len(entries)} entries to {output}")
        return 0

    if not output.parent.is_dir():
        print(f"output parent does not exist: {output.parent}", file=sys.stderr)
        return 1
    output.write_text(content, encoding="utf-8")
    print(f"wrote {len(entries)} entries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
