#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA_HEADINGS = [
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
]

REQUIRED_FILES = [
    "WIKI_SCHEMA.md",
    "WIKI_SCHEMA_PROPOSALS.md",
    "AGENTS.md",
    "CLAUDE.md",
    "wiki_pages/index.md",
    "wiki_pages/log.md",
    "wiki_pages/questions.md",
]

REQUIRED_DIRS = [
    "raw",
    "wiki_records/sources",
    "wiki_pages/sources",
    "wiki_pages/entities",
    "wiki_pages/concepts",
    "wiki_pages/synthesis",
]

PROPOSAL_QUEUE_SECTIONS = [
    "## Pending",
    "## Approved",
    "## Rejected",
]

PROPOSAL_METADATA_LABELS = [
    "Status:",
    "Proposed by:",
    "Date:",
    "Change type:",
    "Affected schema sections:",
    "Human approval required:",
]

PROPOSAL_SUBSECTION_LABELS = [
    "#### Proposed change",
    "#### Reason",
    "#### Why this is generic",
    "#### Approval notes",
]

REQUIRED_SOURCE_FIELDS = [
    "record_id",
    "record_type",
    "status",
    "source_storage",
    "source_type",
    "title",
    "authors",
    "added_date",
]

SOURCE_STATUSES = {"active", "archived", "superseded", "duplicate"}
SOURCE_STORAGES = {"local", "external"}
SOURCE_TYPES = {
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
}
SOURCE_FORMATS = {
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
}

PAGE_FRONTMATTER_FIELDS = {"record_id", "page_type", "title", "aliases", "tags"}
PAGE_TYPES = {
    "source_summary",
    "entity",
    "concept",
    "synthesis",
    "index",
    "log",
    "questions",
}

RECORD_ID_RE = re.compile(r"^SRC-\d{4}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FINGERPRINT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]*:.+$")
OBSIDIAN_LINK_RE = re.compile(r"\[\[([^\]\n]+)\]\]")
SOURCE_CITATION_RE = re.compile(r"\[\^(SRC-\d{4})\]")


@dataclass(frozen=True)
class SourceRecord:
    path: Path
    data: dict[str, Any]


def relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path, errors: list[str], location: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"{location}: cannot read file: {error}")
        return ""


def strip_simple_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_simple_yaml(text: str, location: str) -> tuple[dict[str, Any], list[str]]:
    data: dict[str, Any] = {}
    errors: list[str] = []
    current_key: str | None = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue

        if raw_line.startswith("  - "):
            if current_key is None:
                errors.append(f"{location}:{line_number}: list item has no key")
                continue

            current_value = data[current_key]
            if current_value == "":
                data[current_key] = []
                current_value = data[current_key]
            if not isinstance(current_value, list):
                errors.append(f"{location}:{line_number}: list item follows non-list field: {current_key}")
                continue
            current_value.append(strip_simple_quotes(raw_line[4:].strip()))
            continue

        if raw_line.startswith(" "):
            errors.append(f"{location}:{line_number}: unsupported YAML indentation")
            current_key = None
            continue

        if ":" not in raw_line:
            errors.append(f"{location}:{line_number}: expected key: value")
            current_key = None
            continue

        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        if not key:
            errors.append(f"{location}:{line_number}: missing key")
            current_key = None
            continue
        if key in data:
            errors.append(f"{location}:{line_number}: duplicate key: {key}")
            current_key = None
            continue

        value = raw_value.strip()
        if value == "[]":
            data[key] = []
        else:
            data[key] = strip_simple_quotes(value)
        current_key = key

    return data, errors


def scalar_value(data: dict[str, Any], key: str) -> str:
    value = data.get(key, "")
    if isinstance(value, list):
        return ""
    return str(value)


def has_nonempty_scalar(data: dict[str, Any], key: str) -> bool:
    return key in data and not isinstance(data[key], list) and str(data[key]) != ""


def is_valid_date(value: str) -> bool:
    if not DATE_RE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def path_is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def validate_required_paths(root: Path, errors: list[str]) -> None:
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            errors.append(f"missing required file: {relative}")
        elif not path.is_file():
            errors.append(f"required file is not a file: {relative}")

    for relative in REQUIRED_DIRS:
        path = root / relative
        if not path.exists():
            errors.append(f"missing required directory: {relative}")
        elif not path.is_dir():
            errors.append(f"required directory is not a directory: {relative}")


def validate_schema(root: Path, errors: list[str]) -> None:
    path = root / "WIKI_SCHEMA.md"
    if not path.is_file():
        return

    text = read_text(path, errors, "WIKI_SCHEMA.md")
    headings = [line.rstrip() for line in text.splitlines() if line.startswith("## ")]
    if headings != EXPECTED_SCHEMA_HEADINGS:
        errors.append("WIKI_SCHEMA.md: Schema headings do not match expected top-level heading order")


def markdown_section(text: str, heading: str) -> list[str] | None:
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return None

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return lines[start:end]


def validate_proposals(root: Path, errors: list[str]) -> None:
    path = root / "WIKI_SCHEMA_PROPOSALS.md"
    if not path.is_file():
        return

    text = read_text(path, errors, "WIKI_SCHEMA_PROPOSALS.md")
    lines = text.splitlines()
    top_level_headings = {line for line in lines if line.startswith("## ")}

    for heading in PROPOSAL_QUEUE_SECTIONS:
        if heading not in top_level_headings:
            errors.append(f"WIKI_SCHEMA_PROPOSALS.md: Proposal queue missing section: {heading}")

    template = markdown_section(text, "## Proposal Template")
    if template is None:
        errors.append("WIKI_SCHEMA_PROPOSALS.md: Proposal template is missing")
        return

    if not any(line.startswith("### P-NNNN:") for line in template):
        errors.append("WIKI_SCHEMA_PROPOSALS.md: Proposal template missing heading: ### P-NNNN:")

    for label in PROPOSAL_METADATA_LABELS:
        if not any(line == label or line.startswith(f"{label} ") for line in template):
            errors.append(f"WIKI_SCHEMA_PROPOSALS.md: Proposal template missing label: {label}")

    for label in PROPOSAL_SUBSECTION_LABELS:
        if label not in template:
            errors.append(f"WIKI_SCHEMA_PROPOSALS.md: Proposal template missing subsection: {label}")


def load_source_records(root: Path, errors: list[str]) -> dict[str, SourceRecord]:
    records: dict[str, SourceRecord] = {}
    sources_dir = root / "wiki_records" / "sources"
    if not sources_dir.is_dir():
        return records

    for path in sorted(sources_dir.glob("*.yaml"), key=lambda item: item.name):
        location = relative_path(root, path)
        text = read_text(path, errors, location)
        data, parse_errors = parse_simple_yaml(text, location)
        errors.extend(parse_errors)

        record_id = scalar_value(data, "record_id")
        if record_id:
            if record_id in records:
                errors.append(f"{location}: duplicate record_id: {record_id}")
            else:
                records[record_id] = SourceRecord(path=path, data=data)

    return records


def validate_source_records(root: Path, records: dict[str, SourceRecord], errors: list[str]) -> None:
    for record_id in sorted(records):
        record = records[record_id]
        data = record.data
        location = relative_path(root, record.path)

        for field in REQUIRED_SOURCE_FIELDS:
            if field not in data:
                errors.append(f"{location}: {field} is required")
            elif field != "authors" and isinstance(data[field], list):
                errors.append(f"{location}: {field} must be a scalar")
            elif field != "authors" and str(data[field]) == "":
                errors.append(f"{location}: {field} is required")

        if "authors" in data and not isinstance(data["authors"], list):
            errors.append(f"{location}: authors must be a list")

        if record_id and not RECORD_ID_RE.fullmatch(record_id):
            errors.append(f"{location}: record_id must look like SRC-0001")
        if record_id and record_id != record.path.stem:
            errors.append(f"{location}: record_id must match filename stem")

        record_type = scalar_value(data, "record_type")
        if record_type and record_type != "source":
            errors.append(f"{location}: record_type must be source")

        status = scalar_value(data, "status")
        if status and status not in SOURCE_STATUSES:
            errors.append(f"{location}: status must be one of {', '.join(sorted(SOURCE_STATUSES))}")

        source_storage = scalar_value(data, "source_storage")
        if source_storage and source_storage not in SOURCE_STORAGES:
            errors.append(f"{location}: source_storage must be one of {', '.join(sorted(SOURCE_STORAGES))}")

        source_type = scalar_value(data, "source_type")
        if source_type and source_type not in SOURCE_TYPES:
            errors.append(f"{location}: source_type must be one of {', '.join(sorted(SOURCE_TYPES))}")

        if "source_format" in data:
            source_format = scalar_value(data, "source_format")
            if source_format and source_format not in SOURCE_FORMATS:
                errors.append(f"{location}: source_format must be blank or one of {', '.join(sorted(SOURCE_FORMATS))}")

        validate_source_storage(root, data, location, errors)
        validate_source_relationships(data, records, location, errors)
        validate_source_dates(data, location, errors)
        validate_source_page_path(root, data, location, errors)
        validate_content_fingerprint(data, location, errors)


def validate_source_storage(root: Path, data: dict[str, Any], location: str, errors: list[str]) -> None:
    source_storage = scalar_value(data, "source_storage")
    if source_storage == "local":
        raw_path = scalar_value(data, "raw_path")
        if not raw_path:
            errors.append(f"{location}: raw_path is required for local source_storage")
            return
        if not raw_path.startswith("raw/"):
            errors.append(f"{location}: raw_path must start with raw/")
            return
        raw_file = root / raw_path
        if not path_is_under(raw_file, root / "raw"):
            errors.append(f"{location}: raw_path must point under raw/")
        elif not raw_file.exists():
            errors.append(f"{location}: raw_path does not exist: {raw_path}")

    if source_storage == "external" and not has_nonempty_scalar(data, "source_url"):
        errors.append(f"{location}: source_url is required for external source_storage")


def validate_source_relationships(
    data: dict[str, Any],
    records: dict[str, SourceRecord],
    location: str,
    errors: list[str],
) -> None:
    status = scalar_value(data, "status")
    duplicate_of = scalar_value(data, "duplicate_of")
    superseded_by = scalar_value(data, "superseded_by")

    if status == "duplicate" and not duplicate_of:
        errors.append(f"{location}: duplicate_of is required for duplicate status")
    if status == "superseded" and not superseded_by:
        errors.append(f"{location}: superseded_by is required for superseded status")
    if duplicate_of and duplicate_of not in records:
        errors.append(f"{location}: duplicate_of points to unknown source record: {duplicate_of}")
    if superseded_by and superseded_by not in records:
        errors.append(f"{location}: superseded_by points to unknown source record: {superseded_by}")


def validate_source_dates(data: dict[str, Any], location: str, errors: list[str]) -> None:
    for field in ["added_date", "processed_date", "published_date"]:
        if field not in data:
            continue
        value = scalar_value(data, field)
        if value and not is_valid_date(value):
            errors.append(f"{location}: {field} must be YYYY-MM-DD")


def validate_source_page_path(root: Path, data: dict[str, Any], location: str, errors: list[str]) -> None:
    if "page_path" not in data:
        return

    page_path = scalar_value(data, "page_path")
    if not page_path:
        return
    if not page_path.startswith("wiki_pages/"):
        errors.append(f"{location}: page_path must point under wiki_pages/")
        return

    page_file = root / page_path
    if not path_is_under(page_file, root / "wiki_pages"):
        errors.append(f"{location}: page_path must point under wiki_pages/")
        return

    if page_file.exists() and not has_nonempty_scalar(data, "processed_date"):
        errors.append(f"{location}: processed_date is required when page_path points to an existing page")


def validate_content_fingerprint(data: dict[str, Any], location: str, errors: list[str]) -> None:
    if "content_fingerprint" not in data:
        return

    fingerprint = scalar_value(data, "content_fingerprint")
    if fingerprint and not FINGERPRINT_RE.fullmatch(fingerprint):
        errors.append(f"{location}: content_fingerprint must include an algorithm prefix")


def parse_frontmatter(text: str, location: str) -> tuple[dict[str, Any] | None, list[str]]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None, []

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index] == "---":
            closing_index = index
            break

    if closing_index is None:
        return None, [f"{location}: frontmatter is missing closing ---"]

    yaml_text = "\n".join(lines[1:closing_index])
    data, errors = parse_simple_yaml(yaml_text, f"{location} frontmatter")
    return data, errors


def validate_pages(root: Path, records: dict[str, SourceRecord], errors: list[str]) -> None:
    pages_root = root / "wiki_pages"
    if not pages_root.is_dir():
        return

    pages = sorted(pages_root.rglob("*.md"), key=lambda item: item.relative_to(pages_root).as_posix())
    for path in pages:
        location = relative_path(root, path)
        text = read_text(path, errors, location)
        frontmatter, parse_errors = parse_frontmatter(text, location)
        errors.extend(parse_errors)

        if frontmatter is not None:
            validate_page_frontmatter(frontmatter, records, location, errors)

        validate_obsidian_links(root, path, text, errors)
        validate_source_citations(root, path, text, records, errors)


def validate_page_frontmatter(
    frontmatter: dict[str, Any],
    records: dict[str, SourceRecord],
    location: str,
    errors: list[str],
) -> None:
    for field in sorted(frontmatter):
        if field not in PAGE_FRONTMATTER_FIELDS:
            errors.append(f"{location}: frontmatter field is not allowed: {field}")

    page_type = scalar_value(frontmatter, "page_type")
    if page_type and page_type not in PAGE_TYPES:
        errors.append(f"{location}: page_type must be one of {', '.join(sorted(PAGE_TYPES))}")

    for field in ["aliases", "tags"]:
        if field in frontmatter and not isinstance(frontmatter[field], list):
            errors.append(f"{location}: {field} must be a list")

    record_id = scalar_value(frontmatter, "record_id")
    if record_id:
        record = records.get(record_id)
        if record is None:
            errors.append(f"{location}: record_id points to unknown source record: {record_id}")
        elif has_nonempty_scalar(frontmatter, "title"):
            title = scalar_value(frontmatter, "title")
            record_title = scalar_value(record.data, "title")
            if title != record_title:
                errors.append(f"{location}: mirrored title does not match source record title for {record_id}")


def validate_obsidian_links(root: Path, page_path: Path, text: str, errors: list[str]) -> None:
    location = relative_path(root, page_path)
    seen: set[str] = set()

    for match in OBSIDIAN_LINK_RE.finditer(text):
        raw_target = match.group(1).strip()
        target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
        if not target or target in seen:
            continue
        seen.add(target)

        if not resolve_wiki_page(root / "wiki_pages", target):
            errors.append(f"{location}: unknown Obsidian link target: [[{target}]]")


def resolve_wiki_page(pages_root: Path, target: str) -> bool:
    if "/" in target:
        candidates = [pages_root / target]
        if not target.endswith(".md"):
            candidates.append(pages_root / f"{target}.md")
        for candidate in candidates:
            if path_is_under(candidate, pages_root) and candidate.is_file():
                return True
        return False

    stem = target[:-3] if target.endswith(".md") else target
    for candidate in pages_root.rglob("*.md"):
        if candidate.stem == stem:
            return True
    return False


def validate_source_citations(
    root: Path,
    page_path: Path,
    text: str,
    records: dict[str, SourceRecord],
    errors: list[str],
) -> None:
    location = relative_path(root, page_path)
    cited_records: list[str] = []
    for match in SOURCE_CITATION_RE.finditer(text):
        record_id = match.group(1)
        if record_id not in cited_records:
            cited_records.append(record_id)

    if not cited_records:
        return

    lines = text.splitlines()
    for record_id in cited_records:
        if record_id not in records:
            errors.append(f"{location}: unknown source record citation: {record_id}")
        expected_body_start = f"[^{record_id}]: `{record_id}`"
        if not any(line.startswith(expected_body_start) for line in lines):
            errors.append(f"{location}: missing source record citation footnote body for {record_id}")


def validate_wiki(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"wiki root is not a directory: {root}"]

    validate_required_paths(root, errors)
    validate_schema(root, errors)
    validate_proposals(root, errors)
    records = load_source_records(root, errors)
    validate_source_records(root, records, errors)
    validate_pages(root, records, errors)
    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an LLM Wiki directory.")
    parser.add_argument("wiki_root", type=Path, help="Path to the wiki root.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    errors = validate_wiki(args.wiki_root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"valid: {args.wiki_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
