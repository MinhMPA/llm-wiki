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
    "wiki_records/relations",
    "wiki_records/bibtex",
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

ALLOWED_SOURCE_FIELDS = {
    "record_id",
    "record_type",
    "status",
    "duplicate_of",
    "superseded_by",
    "source_storage",
    "raw_path",
    "source_url",
    "page_path",
    "source_type",
    "source_format",
    "title",
    "authors",
    "added_date",
    "processed_date",
    "published_date",
    "content_fingerprint",
    "arxiv_id",
    "doi",
    "bibtex_key",
}

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

REQUIRED_RELATION_FIELDS = [
    "record_id",
    "record_type",
    "status",
    "source_record_id",
    "target_record_id",
    "relation_type",
    "direction",
    "evidence",
    "created_date",
    "confidence",
]

ALLOWED_RELATION_FIELDS = {
    "record_id",
    "record_type",
    "status",
    "source_record_id",
    "target_record_id",
    "relation_type",
    "direction",
    "evidence",
    "created_date",
    "reviewed_date",
    "confidence",
}

RELATION_STATUSES = {"active", "archived"}
RELATION_TYPES = [
    "cites",
    "builds_on",
    "extends",
    "supports",
    "contradicts",
    "revises",
    "duplicates",
    "supersedes",
    "uses_dataset",
    "uses_method",
    "same_topic",
    "same_entity",
    "background_for",
    "responds_to",
]
RELATION_TYPE_SET = set(RELATION_TYPES)
RELATION_TYPE_LABELS = {
    "cites": "Cites",
    "builds_on": "Builds on",
    "extends": "Extends",
    "supports": "Supports",
    "contradicts": "Contradicts",
    "revises": "Revises",
    "duplicates": "Duplicates",
    "supersedes": "Supersedes",
    "uses_dataset": "Uses dataset",
    "uses_method": "Uses method",
    "same_topic": "Same topic",
    "same_entity": "Same entity",
    "background_for": "Background for",
    "responds_to": "Responds to",
}
RELATION_LABEL_TYPES = {label: relation_type for relation_type, label in RELATION_TYPE_LABELS.items()}
RELATION_DIRECTIONS = {"source_to_target"}
RELATION_CONFIDENCES = {"low", "medium", "high", "unknown"}

REQUIRED_BIBTEX_FIELDS = [
    "record_id",
    "record_type",
    "status",
    "provider",
    "provider_priority",
    "providers_tried",
    "lookup_id",
    "bibtex_key",
    "fetched_date",
    "source_bib_path",
]

ALLOWED_BIBTEX_FIELDS = set(REQUIRED_BIBTEX_FIELDS)
BIBTEX_STATUSES = {"active", "unresolved"}
BIBTEX_PROVIDERS = {"inspire", "ads", "manual"}
PROVIDER_ORDER = ["inspire", "ads"]

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
RELATION_ID_RE = re.compile(r"^REL-\d{4}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FINGERPRINT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]*:.+$")
OBSIDIAN_LINK_RE = re.compile(r"\[\[([^\]\n]+)\]\]")
SOURCE_CITATION_RE = re.compile(r"\[\^(SRC-\d{4})\]")
MANAGED_RELATION_BULLET_RE = re.compile(r"^- \[\[([^\]|#\n]+)\|([^\]\n]+)\]\] \(`(REL-\d{4})`\)$")


@dataclass(frozen=True)
class SourceRecord:
    path: Path
    data: dict[str, Any]


@dataclass(frozen=True)
class RelationRecord:
    path: Path
    data: dict[str, Any]


@dataclass(frozen=True)
class BibtexRecord:
    path: Path
    data: dict[str, Any]


@dataclass(frozen=True)
class ManagedRelationLink:
    relation_type: str
    target: str
    label: str
    record_id: str


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
        if not record_id:
            errors.append(f"{location}: record_id is required")
            continue

        if record_id in records:
            errors.append(f"{location}: duplicate record_id: {record_id}")
        else:
            records[record_id] = SourceRecord(path=path, data=data)

    return records


def load_relation_records(root: Path, errors: list[str]) -> dict[str, RelationRecord]:
    records: dict[str, RelationRecord] = {}
    relations_dir = root / "wiki_records" / "relations"
    if not relations_dir.is_dir():
        return records

    for path in sorted(relations_dir.glob("*.yaml"), key=lambda item: item.name):
        location = relative_path(root, path)
        text = read_text(path, errors, location)
        data, parse_errors = parse_simple_yaml(text, location)
        errors.extend(parse_errors)

        record_id = scalar_value(data, "record_id")
        if not record_id:
            errors.append(f"{location}: record_id is required")
            continue

        if record_id in records:
            errors.append(f"{location}: duplicate record_id: {record_id}")
        else:
            records[record_id] = RelationRecord(path=path, data=data)

    return records


def load_bibtex_records(root: Path, errors: list[str]) -> dict[str, BibtexRecord]:
    records: dict[str, BibtexRecord] = {}
    bibtex_dir = root / "wiki_records" / "bibtex"
    if not bibtex_dir.is_dir():
        return records

    for path in sorted(bibtex_dir.glob("*.yaml"), key=lambda item: item.name):
        location = relative_path(root, path)
        text = read_text(path, errors, location)
        data, parse_errors = parse_simple_yaml(text, location)
        errors.extend(parse_errors)

        record_id = scalar_value(data, "record_id")
        if not record_id:
            errors.append(f"{location}: record_id is required")
            continue

        if record_id in records:
            errors.append(f"{location}: duplicate record_id: {record_id}")
        else:
            records[record_id] = BibtexRecord(path=path, data=data)

    return records


def validate_source_records(root: Path, records: dict[str, SourceRecord], errors: list[str]) -> None:
    for record_id in sorted(records):
        record = records[record_id]
        data = record.data
        location = relative_path(root, record.path)

        for field in sorted(data):
            if field not in ALLOWED_SOURCE_FIELDS:
                errors.append(f"{location}: unsupported source record field: {field}")

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


def validate_relation_records(
    root: Path,
    records: dict[str, RelationRecord],
    source_records: dict[str, SourceRecord],
    errors: list[str],
) -> None:
    for record_id in sorted(records):
        record = records[record_id]
        data = record.data
        location = relative_path(root, record.path)

        for field in sorted(data):
            if field not in ALLOWED_RELATION_FIELDS:
                errors.append(f"{location}: unsupported relation record field: {field}")

        for field in REQUIRED_RELATION_FIELDS:
            if field not in data:
                errors.append(f"{location}: {field} is required")
            elif field != "evidence" and isinstance(data[field], list):
                errors.append(f"{location}: {field} must be a scalar")
            elif field != "evidence" and str(data[field]) == "":
                errors.append(f"{location}: {field} is required")

        if "evidence" in data and not isinstance(data["evidence"], list):
            errors.append(f"{location}: evidence must be a list")

        if record_id and not RELATION_ID_RE.fullmatch(record_id):
            errors.append(f"{location}: record_id must look like REL-0001")
        if record_id and record_id != record.path.stem:
            errors.append(f"{location}: record_id must match filename stem")

        record_type = scalar_value(data, "record_type")
        if record_type and record_type != "relation":
            errors.append(f"{location}: record_type must be relation")

        status = scalar_value(data, "status")
        if status and status not in RELATION_STATUSES:
            errors.append(f"{location}: status must be one of {', '.join(sorted(RELATION_STATUSES))}")

        relation_type = scalar_value(data, "relation_type")
        if relation_type and relation_type not in RELATION_TYPE_SET:
            errors.append(f"{location}: relation_type must be one of {', '.join(RELATION_TYPES)}")

        direction = scalar_value(data, "direction")
        if direction and direction not in RELATION_DIRECTIONS:
            errors.append(f"{location}: direction must be source_to_target")

        confidence = scalar_value(data, "confidence")
        if confidence and confidence not in RELATION_CONFIDENCES:
            errors.append(f"{location}: confidence must be one of {', '.join(sorted(RELATION_CONFIDENCES))}")

        source_record_id = scalar_value(data, "source_record_id")
        target_record_id = scalar_value(data, "target_record_id")
        if source_record_id and source_record_id not in source_records:
            errors.append(f"{location}: source_record_id points to unknown source record: {source_record_id}")
        if target_record_id and target_record_id not in source_records:
            errors.append(f"{location}: target_record_id points to unknown source record: {target_record_id}")
        if source_record_id and target_record_id and source_record_id == target_record_id:
            errors.append(f"{location}: source_record_id must not equal target_record_id")
        if status == "active":
            source = source_records.get(source_record_id)
            target = source_records.get(target_record_id)
            if source is not None and source_page_file(root, source) is None:
                errors.append(f"{location}: active relation source page is missing for {record_id}")
            if target is not None and source_page_file(root, target) is None:
                errors.append(f"{location}: active relation target page is missing for {record_id}")
            if target is not None and source_page_file(root, target) is not None:
                target_path = source_page_target(root, target)
                target_title = scalar_value(target.data, "title")
                if any(character in target_path for character in "[]|#\n"):
                    errors.append(f"{location}: active relation target page path cannot render as a managed link: {target_path}")
                if any(character in target_title for character in "]\n"):
                    errors.append(f"{location}: active relation target title cannot render as a managed link label")

        for field in ["created_date", "reviewed_date"]:
            if field not in data:
                continue
            value = scalar_value(data, field)
            if value and not is_valid_date(value):
                errors.append(f"{location}: {field} must be YYYY-MM-DD")


def extract_bibtex_key(entry_text: str) -> str:
    match = re.search(r"@\w+\{([^,\s]+)\s*,", entry_text)
    if match is None:
        return ""
    return match.group(1).strip()


def extract_bibtex_keys(entry_text: str) -> list[str]:
    return [match.strip() for match in re.findall(r"@\w+\{([^,\s]+)\s*,", entry_text)]


def providers_follow_order(providers: list[str]) -> bool:
    positions = [PROVIDER_ORDER.index(provider) for provider in providers if provider in PROVIDER_ORDER]
    return positions == sorted(positions) and len(positions) == len(set(positions))


def validate_bibtex_records(
    root: Path,
    records: dict[str, BibtexRecord],
    source_records: dict[str, SourceRecord],
    errors: list[str],
) -> None:
    bibtex_dir = root / "wiki_records" / "bibtex"

    for record_id in sorted(records):
        record = records[record_id]
        data = record.data
        location = relative_path(root, record.path)

        for field in sorted(data):
            if field not in ALLOWED_BIBTEX_FIELDS:
                errors.append(f"{location}: unsupported BibTeX record field: {field}")

        for field in REQUIRED_BIBTEX_FIELDS:
            if field not in data:
                errors.append(f"{location}: {field} is required")
            elif field != "providers_tried" and isinstance(data[field], list):
                errors.append(f"{location}: {field} must be a scalar")

        if record_id and not RECORD_ID_RE.fullmatch(record_id):
            errors.append(f"{location}: record_id must look like SRC-0001")
        if record_id and record_id != record.path.stem:
            errors.append(f"{location}: record_id must match filename stem")
        if record_id and record_id not in source_records:
            errors.append(f"{location}: record_id points to unknown source record: {record_id}")

        record_type = scalar_value(data, "record_type")
        if record_type and record_type != "bibtex":
            errors.append(f"{location}: record_type must be bibtex")

        status = scalar_value(data, "status")
        if status and status not in BIBTEX_STATUSES:
            errors.append(f"{location}: status must be one of {', '.join(sorted(BIBTEX_STATUSES))}")

        provider = scalar_value(data, "provider")
        provider_priority = scalar_value(data, "provider_priority")
        if status == "active":
            if provider not in BIBTEX_PROVIDERS:
                errors.append(f"{location}: provider must be one of {', '.join(sorted(BIBTEX_PROVIDERS))}")
            if provider == "inspire" and provider_priority != "1":
                errors.append(f"{location}: provider_priority must be 1 for inspire")
            if provider == "ads" and provider_priority != "2":
                errors.append(f"{location}: provider_priority must be 2 for ads")
            if provider == "manual" and provider_priority:
                errors.append(f"{location}: provider_priority must be blank for manual")
        elif status == "unresolved":
            if provider:
                errors.append(f"{location}: provider must be blank for unresolved")
            if provider_priority:
                errors.append(f"{location}: provider_priority must be blank for unresolved")

        providers_tried = data.get("providers_tried", "")
        if not isinstance(providers_tried, list):
            errors.append(f"{location}: providers_tried must be a list")
            providers: list[str] = []
        else:
            providers = [str(provider_value) for provider_value in providers_tried]
            for provider_value in providers:
                if provider_value not in PROVIDER_ORDER:
                    errors.append(f"{location}: providers_tried contains unknown provider: {provider_value}")
            if not providers_follow_order(providers):
                errors.append(f"{location}: providers_tried must follow provider order: {', '.join(PROVIDER_ORDER)}")

        fetched_date = scalar_value(data, "fetched_date")
        if fetched_date and not is_valid_date(fetched_date):
            errors.append(f"{location}: fetched_date must be YYYY-MM-DD")

        source_bib_path = scalar_value(data, "source_bib_path")
        bibtex_key = scalar_value(data, "bibtex_key")
        if status == "active":
            expected_bib_path = f"wiki_records/bibtex/{record_id}.bib"
            if source_bib_path != expected_bib_path:
                errors.append(f"{location}: source_bib_path must be {expected_bib_path}")
            if not bibtex_key:
                errors.append(f"{location}: bibtex_key is required for active status")
            bib_path = root / source_bib_path if source_bib_path else bibtex_dir / f"{record_id}.bib"
            if not bib_path.is_file():
                errors.append(f"{location}: missing BibTeX file: {source_bib_path or expected_bib_path}")
            else:
                entry_text = read_text(bib_path, errors, relative_path(root, bib_path))
                entry_key = extract_bibtex_key(entry_text)
                if not entry_key:
                    errors.append(f"{relative_path(root, bib_path)}: BibTeX entry key not found")
                elif bibtex_key and entry_key != bibtex_key:
                    errors.append(f"{location}: bibtex_key does not match BibTeX entry key")
                source = source_records.get(record_id)
                if source is not None:
                    source_key = scalar_value(source.data, "bibtex_key")
                    if source_key and source_key != bibtex_key:
                        errors.append(f"{location}: bibtex_key does not match source record bibtex_key")
        elif status == "unresolved":
            if bibtex_key:
                errors.append(f"{location}: bibtex_key must be blank for unresolved")
            if source_bib_path:
                errors.append(f"{location}: source_bib_path must be blank for unresolved")

    for path in sorted(bibtex_dir.glob("SRC-*.bib"), key=lambda item: item.name):
        record_id = path.stem
        if record_id not in records:
            errors.append(f"{relative_path(root, path)}: BibTeX file has no sidecar record")

    validate_references_bib(root, records, source_records, errors)


def validate_references_bib(
    root: Path,
    records: dict[str, BibtexRecord],
    source_records: dict[str, SourceRecord],
    errors: list[str],
) -> None:
    references_path = root / "wiki_records" / "bibtex" / "references.bib"
    if not references_path.is_file():
        return

    location = relative_path(root, references_path)
    text = read_text(references_path, errors, location)
    keys = extract_bibtex_keys(text)
    seen: set[str] = set()
    for key in keys:
        if key in seen:
            errors.append(f"{location}: references.bib contains duplicate BibTeX key: {key}")
        seen.add(key)

    active_keys: set[str] = set()
    for record_id, record in records.items():
        source = source_records.get(record_id)
        if source is None:
            continue
        if scalar_value(source.data, "status") != "active":
            continue
        if scalar_value(record.data, "status") != "active":
            continue
        bibtex_key = scalar_value(record.data, "bibtex_key")
        if bibtex_key:
            active_keys.add(bibtex_key)

    for key in keys:
        if key not in active_keys:
            errors.append(f"{location}: references.bib contains non-active BibTeX key: {key}")


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

    if not page_file.exists():
        return
    if not page_file.is_file():
        errors.append(f"{location}: page_path must point to a file")
        return
    if not has_nonempty_scalar(data, "processed_date"):
        errors.append(f"{location}: processed_date is required when page_path points to an existing page")

    page_text = read_text(page_file, errors, relative_path(root, page_file))
    frontmatter, parse_errors = parse_frontmatter(page_text, relative_path(root, page_file))
    errors.extend(parse_errors)
    if frontmatter is None or scalar_value(frontmatter, "page_type") != "source_summary":
        errors.append(f"{location}: page_path must point to a source_summary page")
    elif scalar_value(frontmatter, "record_id") != scalar_value(data, "record_id"):
        errors.append(f"{location}: page_path frontmatter record_id must match source record_id")


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


def source_page_file(root: Path, record: SourceRecord) -> Path | None:
    page_path = scalar_value(record.data, "page_path")
    if not page_path:
        return None
    page_file = root / page_path
    if page_path.startswith("wiki_pages/") and page_file.is_file() and path_is_under(page_file, root / "wiki_pages"):
        return page_file
    return None


def source_page_target(root: Path, record: SourceRecord) -> str:
    page_path = scalar_value(record.data, "page_path")
    if page_path.startswith("wiki_pages/"):
        target = page_path.removeprefix("wiki_pages/")
        if target.endswith(".md"):
            target = target[:-3]
        return target
    return ""


def active_renderable_relations(
    root: Path,
    relations: dict[str, RelationRecord],
    source_records: dict[str, SourceRecord],
) -> list[RelationRecord]:
    renderable: list[RelationRecord] = []
    for relation in relations.values():
        data = relation.data
        if scalar_value(data, "status") != "active":
            continue
        source = source_records.get(scalar_value(data, "source_record_id"))
        target = source_records.get(scalar_value(data, "target_record_id"))
        if source is None or target is None:
            continue
        if source_page_file(root, source) is None or source_page_file(root, target) is None:
            continue
        renderable.append(relation)
    return renderable


def render_managed_section(root: Path, relations: list[RelationRecord], source_records: dict[str, SourceRecord]) -> list[str]:
    if not relations:
        return []

    by_type: dict[str, list[RelationRecord]] = {relation_type: [] for relation_type in RELATION_TYPES}
    for relation in relations:
        relation_type = scalar_value(relation.data, "relation_type")
        if relation_type in by_type:
            by_type[relation_type].append(relation)

    lines = ["## Related sources", ""]
    first_group = True
    for relation_type in RELATION_TYPES:
        group = by_type[relation_type]
        if not group:
            continue
        if not first_group:
            lines.append("")
        first_group = False
        lines.append(f"### {RELATION_TYPE_LABELS[relation_type]}")

        def sort_key(relation: RelationRecord) -> tuple[str, str]:
            target = source_records[scalar_value(relation.data, "target_record_id")]
            return (scalar_value(target.data, "title").lower(), scalar_value(relation.data, "record_id"))

        for relation in sorted(group, key=sort_key):
            target = source_records[scalar_value(relation.data, "target_record_id")]
            target_path = source_page_target(root, target)
            target_title = scalar_value(target.data, "title")
            relation_id = scalar_value(relation.data, "record_id")
            lines.append(f"- [[{target_path}|{target_title}]] (`{relation_id}`)")
    return lines


def managed_section_bounds(lines: list[str]) -> tuple[int, int] | None:
    starts = [index for index, line in enumerate(lines) if line == "## Related sources"]
    if not starts:
        return None
    start = starts[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return start, end


def parse_managed_relation_links(lines: list[str], location: str, errors: list[str]) -> list[ManagedRelationLink]:
    starts = [index for index, line in enumerate(lines) if line == "## Related sources"]
    if len(starts) > 1:
        errors.append(f"{location}: multiple Related sources sections are not allowed")
        return []
    if not starts:
        return []

    bounds = managed_section_bounds(lines)
    if bounds is None:
        return []
    start, end = bounds
    current_relation_type = ""
    links: list[ManagedRelationLink] = []

    for line_number, line in enumerate(lines[start + 1 : end], start=start + 2):
        if not line:
            continue
        if line.startswith("### "):
            label = line[4:]
            relation_type = RELATION_LABEL_TYPES.get(label)
            if relation_type is None:
                errors.append(f"{location}:{line_number}: unknown relation type group: {label}")
                current_relation_type = ""
            else:
                current_relation_type = relation_type
            continue
        if line.startswith("- "):
            if not current_relation_type:
                errors.append(f"{location}:{line_number}: managed relation bullet must follow a relation type group")
                continue
            match = MANAGED_RELATION_BULLET_RE.fullmatch(line)
            if match is None:
                errors.append(f"{location}:{line_number}: managed relation bullet has invalid format")
                continue
            target, label, record_id = match.groups()
            links.append(ManagedRelationLink(current_relation_type, target, label, record_id))
            continue
        errors.append(f"{location}:{line_number}: unmanaged content is not allowed in Related sources")
    return links


def validate_managed_relation_sections(
    root: Path,
    path: Path,
    text: str,
    frontmatter: dict[str, Any] | None,
    source_records: dict[str, SourceRecord],
    relation_records: dict[str, RelationRecord],
    errors: list[str],
) -> None:
    location = relative_path(root, path)
    lines = text.splitlines()
    actual_links = parse_managed_relation_links(lines, location, errors)

    if frontmatter is None or scalar_value(frontmatter, "page_type") != "source_summary":
        if any(line == "## Related sources" for line in lines):
            errors.append(f"{location}: Related sources section is only allowed on source_summary pages")
        return

    source_record_id = scalar_value(frontmatter, "record_id")
    bounds = managed_section_bounds(lines)
    if not source_record_id:
        if bounds is not None or actual_links:
            errors.append(f"{location}: Related sources section requires source_summary record_id")
        return

    desired_relations = [
        relation
        for relation in active_renderable_relations(root, relation_records, source_records)
        if scalar_value(relation.data, "source_record_id") == source_record_id
    ]
    desired_lines = render_managed_section(root, desired_relations, source_records)

    if not desired_lines:
        if bounds is not None:
            errors.append(f"{location}: Related sources section is stale; no active outgoing relations render here")
        for link in actual_links:
            relation = relation_records.get(link.record_id)
            if relation is not None and scalar_value(relation.data, "status") == "archived":
                errors.append(f"{location}: archived relation is rendered in Related sources: {link.record_id}")
            else:
                errors.append(f"{location}: managed relation link has no active relation record: {link.record_id}")
        return

    if bounds is None:
        errors.append(f"{location}: missing Related sources section for active outgoing relations")
        return

    start, end = bounds
    actual_section = lines[start:end]
    while actual_section and actual_section[-1] == "":
        actual_section.pop()
    if actual_section != desired_lines:
        errors.append(f"{location}: Related sources section does not match relation records")

    expected_ids = {scalar_value(relation.data, "record_id") for relation in desired_relations}
    actual_ids = {link.record_id for link in actual_links}
    for record_id in sorted(actual_ids - expected_ids):
        relation = relation_records.get(record_id)
        if relation is not None and scalar_value(relation.data, "status") == "archived":
            errors.append(f"{location}: archived relation is rendered in Related sources: {record_id}")
        else:
            errors.append(f"{location}: managed relation link has no active relation record: {record_id}")
    for record_id in sorted(expected_ids - actual_ids):
        errors.append(f"{location}: missing managed relation link for active relation: {record_id}")


def validate_lifecycle_relation_mirrors(
    root: Path,
    source_records: dict[str, SourceRecord],
    relation_records: dict[str, RelationRecord],
    errors: list[str],
) -> None:
    active_edges = {
        (
            scalar_value(relation.data, "source_record_id"),
            scalar_value(relation.data, "target_record_id"),
            scalar_value(relation.data, "relation_type"),
        )
        for relation in relation_records.values()
        if scalar_value(relation.data, "status") == "active"
    }

    for record_id, record in sorted(source_records.items()):
        if source_page_file(root, record) is None:
            continue
        location = relative_path(root, record.path)
        status = scalar_value(record.data, "status")
        if status == "duplicate":
            target_id = scalar_value(record.data, "duplicate_of")
            if target_id and (record_id, target_id, "duplicates") not in active_edges:
                errors.append(f"{location}: processed duplicate source requires an active duplicates relation to {target_id}")
        if status == "superseded":
            target_id = scalar_value(record.data, "superseded_by")
            if target_id and (record_id, target_id, "supersedes") not in active_edges:
                errors.append(f"{location}: processed superseded source requires an active supersedes relation to {target_id}")


def validate_pages(
    root: Path,
    records: dict[str, SourceRecord],
    relation_records: dict[str, RelationRecord],
    errors: list[str],
) -> None:
    pages_root = root / "wiki_pages"
    if not pages_root.is_dir():
        return

    pages = sorted(pages_root.rglob("*.md"), key=lambda item: item.relative_to(pages_root).as_posix())
    for path in pages:
        location = relative_path(root, path)
        text = read_text(path, errors, location)
        frontmatter, parse_errors = parse_frontmatter(text, location)
        errors.extend(parse_errors)

        if frontmatter is None:
            errors.append(f"{location}: frontmatter is required")
        else:
            validate_page_frontmatter(frontmatter, records, location, errors)

        validate_obsidian_links(root, path, text, errors)
        validate_source_citations(root, path, text, records, errors)
        validate_managed_relation_sections(root, path, text, frontmatter, records, relation_records, errors)


def validate_page_frontmatter(
    frontmatter: dict[str, Any],
    records: dict[str, SourceRecord],
    location: str,
    errors: list[str],
) -> None:
    for field in sorted(frontmatter):
        if field not in PAGE_FRONTMATTER_FIELDS:
            errors.append(f"{location}: frontmatter field is not allowed: {field}")

    for field in ["page_type", "title", "aliases", "tags"]:
        if field not in frontmatter:
            errors.append(f"{location}: {field} is required in frontmatter")

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
    relation_records = load_relation_records(root, errors)
    bibtex_records = load_bibtex_records(root, errors)
    validate_source_records(root, records, errors)
    validate_relation_records(root, relation_records, records, errors)
    validate_bibtex_records(root, bibtex_records, records, errors)
    validate_lifecycle_relation_mirrors(root, records, relation_records, errors)
    validate_pages(root, records, relation_records, errors)
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
