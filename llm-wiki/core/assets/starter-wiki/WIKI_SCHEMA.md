# Wiki Schema

## Purpose

This wiki preserves knowledge as portable files with explicit records, readable pages, version history, custom schema control, local/private operation, model choice, ongoing maintenance, and auditability.

## Directory Layout

- `WIKI_SCHEMA.md`: approved operating contract.
- `WIKI_SCHEMA_PROPOSALS.md`: maintained proposal queue for schema changes.
- `AGENTS.md`: pointer file for ChatGPT Codex.
- `CLAUDE.md`: pointer file for Claude Code.
- `raw/`: local immutable source artifacts.
- `wiki_records/`: structured authoritative records. Source record files live under `wiki_records/sources/` as `.yaml` files. Example: `wiki_records/sources/SRC-0001.yaml`.
- `wiki_pages/`: human-readable maintained wiki pages. Source-summary pages live under `wiki_pages/sources/` as `.md` files. Entity, concept, and synthesis pages live under matching subdirectories.

## Page Types

Allowed `page_type` values are `source_summary`, `entity`, `concept`, `synthesis`, `index`, `log`, and `questions`.

Readable pages use minimal Obsidian-compatible frontmatter:

```yaml
---
record_id: SRC-0001
page_type: source_summary
title: Example Source
aliases: []
tags:
  - source
---
```

Allowed page frontmatter fields are only `record_id`, `page_type`, `title`, `aliases`, and `tags`.

Records are authoritative. Page properties are minimal mirrors for navigation and discovery, not complete copies of record data.

## Evidence And Citations

Durable claims cite source records with footnotes such as `[^SRC-0001]`. The footnote body must begin with the matching record ID in backticks, for example:

```markdown
Claim text.[^SRC-0001]

[^SRC-0001]: `SRC-0001` - [[sources/example]]
```

## Ingest Workflow

Processing a source creates or updates:

- one source record in `wiki_records/sources/SRC-0001.yaml`;
- one source summary in `wiki_pages/sources/`, unless explicitly record-only;
- `wiki_pages/index.md`;
- `wiki_pages/log.md`.

Entity, concept, synthesis, and question pages are updated when supported by the source. The source record must be written before durable claims are added to readable pages.

## Query Workflow

Answer from wiki pages first, then consult records and sources when needed. Durable synthesis may be filed only with human approval.

## Lint Workflow

Mechanical drift may be fixed automatically. Semantic, schema, or destructive changes require human approval.

## Naming Conventions

Use explicit short field names. Universal field names are preferred when precise, including `record_id`, `record_type`, `page_type`, `source_type`, and `source_format`.

Source record IDs use `SRC-0001`, `SRC-0002`, and so on. A v1 source record uses this YAML contract:

```yaml
record_id: SRC-0001
record_type: source
status: active
duplicate_of:
superseded_by:
source_storage: local
raw_path: raw/SRC-0001/example.pdf
source_url:
page_path: wiki_pages/sources/SRC-0001-example-source.md
source_type: paper
source_format: pdf
title: Example Source
authors: []
added_date: 2026-05-11
processed_date:
published_date:
content_fingerprint:
```

Required source record fields are `record_id`, `record_type`, `status`, `source_storage`, `source_type`, `title`, `authors`, and `added_date`.

Optional source record fields are `duplicate_of`, `superseded_by`, `raw_path`, `source_url`, `page_path`, `source_format`, `processed_date`, `published_date`, and `content_fingerprint`.

`record_type` must be `source` for source records.

Controlled `status` values are exactly `active`, `archived`, `superseded`, and `duplicate`.

Controlled `source_storage` values are `local` and `external`.

Conditional source record rules:

- `record_type` must be `source`.
- `raw_path` is required when `source_storage` is `local` and must point under `raw/`.
- `source_url` is required when `source_storage` is `external`.
- `processed_date` is required once `page_path` points to an existing source summary.
- `duplicate_of` is required when `status` is `duplicate`.
- `superseded_by` is required when `status` is `superseded`.
- `content_fingerprint` may be blank; when present it must include an algorithm prefix such as `sha256:`.
- `authors` is a list and may be empty.

Controlled `source_type` values are `article`, `paper`, `book`, `chapter`, `transcript`, `note`, `image`, `dataset`, `video`, `audio`, `report`, `documentation`, and `other`.

Controlled `source_format` values are `markdown`, `pdf`, `html`, `text`, `image`, `audio`, `video`, `csv`, `spreadsheet`, `json`, `yaml`, and `other`.

## Review Policy

Schema changes, exception-like rules, semantic rewrites, duplicate merges, superseding sources, archival, deletion, and new durable synthesis require human approval. Schema proposals must use the block format in `WIKI_SCHEMA_PROPOSALS.md` before approval.

## User Preferences

Keep structured data separate from readable pages. Keep page frontmatter minimal and Obsidian-compatible. Prefer source records for machine-readable facts and readable pages for human-oriented summaries, synthesis, indexes, logs, and open questions. Tags are for `wiki_pages/` only and do not belong in canonical record YAML.

## Schema Evolution

Top-level schema sections are fixed. Schema rules and subsections must stay generic. Generic schema changes are proposed in `WIKI_SCHEMA_PROPOSALS.md` using the machine-checkable proposal block format. Entry-specific exception rules do not belong in the schema. If an agent encounters an entry-specific exception request, it must route it to human review as a question or schema proposal instead of adding it directly to the schema.
