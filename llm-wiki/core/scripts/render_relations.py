#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from validate_wiki import (
    RelationRecord,
    SourceRecord,
    active_renderable_relations,
    load_relation_records,
    load_source_records,
    managed_section_bounds,
    parse_frontmatter,
    parse_managed_relation_links,
    read_text,
    relative_path,
    render_managed_section,
    scalar_value,
    source_page_file,
    validate_relation_records,
    validate_source_records,
)


def source_summary_pages(root: Path, source_records: dict[str, SourceRecord]) -> dict[Path, str]:
    pages: dict[Path, str] = {}
    for record_id, record in source_records.items():
        page = source_page_file(root, record)
        if page is not None:
            pages[page] = record_id
    return pages


def validate_render_inputs(
    root: Path,
    source_records: dict[str, SourceRecord],
    relation_records: dict[str, RelationRecord],
) -> list[str]:
    errors: list[str] = []
    validate_source_records(root, source_records, errors)
    validate_relation_records(root, relation_records, source_records, errors)

    for relation_id, relation in sorted(relation_records.items()):
        if scalar_value(relation.data, "status") != "active":
            continue
        location = relative_path(root, relation.path)
        source = source_records.get(scalar_value(relation.data, "source_record_id"))
        target = source_records.get(scalar_value(relation.data, "target_record_id"))
        if source is None or target is None:
            continue
        if source_page_file(root, source) is None:
            errors.append(f"{location}: active relation source page is missing for {relation_id}")
        if source_page_file(root, target) is None:
            errors.append(f"{location}: active relation target page is missing for {relation_id}")

    for page, record_id in sorted(source_summary_pages(root, source_records).items()):
        location = relative_path(root, page)
        text = read_text(page, errors, location)
        frontmatter, parse_errors = parse_frontmatter(text, location)
        errors.extend(parse_errors)
        if frontmatter is None:
            errors.append(f"{location}: frontmatter is required")
            continue
        if scalar_value(frontmatter, "record_id") != record_id:
            errors.append(f"{location}: frontmatter record_id does not match source record page_path")
        parse_managed_relation_links(text.splitlines(), location, errors)

    return errors


def desired_section_for_source(
    root: Path,
    source_record_id: str,
    source_records: dict[str, SourceRecord],
    relation_records: dict[str, RelationRecord],
) -> list[str]:
    relations = [
        relation
        for relation in active_renderable_relations(root, relation_records, source_records)
        if scalar_value(relation.data, "source_record_id") == source_record_id
    ]
    return render_managed_section(root, relations, source_records)


def strip_trailing_blank_lines(lines: list[str]) -> list[str]:
    result = list(lines)
    while result and result[-1] == "":
        result.pop()
    return result


def find_insertion_index(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if line.startswith("[^"):
            while index > 0 and lines[index - 1] == "":
                index -= 1
            return index
    return len(strip_trailing_blank_lines(lines))


def replace_managed_section(lines: list[str], desired_section: list[str]) -> list[str]:
    bounds = managed_section_bounds(lines)
    if bounds is None:
        if not desired_section:
            return lines
        insert_at = find_insertion_index(lines)
        prefix = strip_trailing_blank_lines(lines[:insert_at])
        suffix = lines[insert_at:]
        inserted = prefix + ["", *desired_section]
        if suffix:
            inserted.extend(["", *suffix])
        return inserted

    start, end = bounds
    if desired_section:
        return lines[:start] + desired_section + lines[end:]

    prefix = strip_trailing_blank_lines(lines[:start])
    suffix = list(lines[end:])
    while suffix and suffix[0] == "":
        suffix.pop(0)
    if prefix and suffix:
        return prefix + [""] + suffix
    return prefix + suffix


def render_page(
    root: Path,
    page: Path,
    source_record_id: str,
    source_records: dict[str, SourceRecord],
    relation_records: dict[str, RelationRecord],
) -> str:
    text = page.read_text(encoding="utf-8")
    lines = text.splitlines()
    desired = desired_section_for_source(root, source_record_id, source_records, relation_records)
    rendered = replace_managed_section(lines, desired)
    return "\n".join(rendered).rstrip() + "\n"


def render_relations(root: Path, apply: bool) -> tuple[int, list[str]]:
    errors: list[str] = []
    source_records = load_source_records(root, errors)
    relation_records = load_relation_records(root, errors)
    errors.extend(validate_render_inputs(root, source_records, relation_records))
    if errors:
        return 2, errors

    changed: list[str] = []
    for page, source_record_id in sorted(source_summary_pages(root, source_records).items()):
        original = page.read_text(encoding="utf-8")
        rendered = render_page(root, page, source_record_id, source_records, relation_records)
        if rendered != original:
            changed.append(relative_path(root, page))
            if apply:
                page.write_text(rendered, encoding="utf-8")

    if changed:
        prefix = "updated" if apply else "would update"
        return 1 if not apply else 0, [f"{prefix}: {path}" for path in changed]
    return 0, [f"relations current: {root}"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render managed source relation sections in an LLM Wiki.")
    parser.add_argument("wiki_root", type=Path, help="Path to the wiki root.")
    parser.add_argument("--apply", action="store_true", help="Rewrite managed Related sources sections.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.wiki_root.is_dir():
        print(f"wiki root is not a directory: {args.wiki_root}", file=sys.stderr)
        return 2

    exit_code, messages = render_relations(args.wiki_root, args.apply)
    stream = sys.stdout if exit_code == 0 else sys.stderr
    for message in messages:
        print(message, file=stream)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
