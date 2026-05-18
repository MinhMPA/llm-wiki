# Wiki Schema

## Purpose

This wiki preserves knowledge as portable files with explicit records, readable pages, version history, custom schema control, local/private operation, model choice, ongoing maintenance, and auditability.

## Directory Layout

- `WIKI_SCHEMA.md`: approved operating contract.
- `WIKI_SCHEMA_PROPOSALS.md`: maintained proposal queue for schema changes.
- `AGENTS.md`: pointer file for ChatGPT Codex.
- `CLAUDE.md`: pointer file for Claude Code.
- `raw/`: local immutable source artifacts.
- `wiki_records/`: structured authoritative records. Source record files live under `wiki_records/sources/` as `.yaml` files. Example: `wiki_records/sources/SRC-0001.yaml`. Source relation records live under `wiki_records/relations/` as `.yaml` files. Example: `wiki_records/relations/REL-0001.yaml`. Bibliography artifacts live under `wiki_records/bibtex/`.
- `wiki_pages/`: human-readable maintained wiki pages. Source-summary pages live under `wiki_pages/sources/` as `.md` files. Entity, concept, and synthesis pages live under matching subdirectories.

## Page Types

Allowed `page_type` values are `source_summary`, `entity`, `concept`, `synthesis`, `index`, `log`, and `questions`.

Readable pages use minimal Obsidian-compatible frontmatter:

Every markdown file under `wiki_pages/` must include it.

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

Required page frontmatter fields are `page_type`, `title`, `aliases`, and `tags`. `record_id` is required only when a page mirrors a structured record.

Records are authoritative. Page properties are minimal mirrors for navigation and discovery, not complete copies of record data.

Source-summary pages may include a managed `Related sources` section when active outgoing source relations exist. Omit the section when there are no active outgoing relations.

```markdown
  ## Related sources

  ### Cites
  - [[sources/readable-source-title|Readable Source Title]] (`REL-0001`)
```

The managed section may contain only blank lines, relation type group headings, and managed relation bullets. Each managed bullet must correspond to one active relation record. Freeform related-source prose belongs outside the managed section.

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

Rendering managed `Related sources` sections from approved relation records is a mechanical lint operation. Creating, removing, or changing the meaning of relation records is semantic work and requires human approval.

Bibliography workflow maintenance is a lint-boundary operation for active paper sources. Fetch previews and aggregate export previews are non-mutating by default; writing canonical BibTeX artifacts or `wiki_records/bibtex/references.bib` requires `--apply`.

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
arxiv_id: 1808.02002
doi:
bibtex_key:
```

Required source record fields are `record_id`, `record_type`, `status`, `source_storage`, `source_type`, `title`, `authors`, and `added_date`.

Optional source record fields are `duplicate_of`, `superseded_by`, `raw_path`, `source_url`, `page_path`, `source_format`, `processed_date`, `published_date`, `content_fingerprint`, `arxiv_id`, `doi`, and `bibtex_key`.

The source record field set is closed in v1. Unknown fields are invalid. Human navigation fields such as `tags` belong only in `wiki_pages/` frontmatter.

`record_type` must be `source` for source records.

Controlled `status` values are exactly `active`, `archived`, `superseded`, and `duplicate`.

Controlled `source_storage` values are `local` and `external`.

Conditional source record rules:

- `record_type` must be `source`.
- `raw_path` is required when `source_storage` is `local` and must point under `raw/`.
- `source_url` is required when `source_storage` is `external`.
- `processed_date` is required once `page_path` points to an existing source summary.
- when `page_path` points to an existing page, that path must be a file whose frontmatter has `page_type: source_summary`.
- `duplicate_of` is required when `status` is `duplicate`.
- `superseded_by` is required when `status` is `superseded`.
- `content_fingerprint` may be blank; when present it must include an algorithm prefix such as `sha256:`.
- `authors` is a list and may be empty.

Controlled `source_type` values are `article`, `paper`, `book`, `chapter`, `transcript`, `note`, `image`, `dataset`, `video`, `audio`, `report`, `documentation`, and `other`.

Controlled `source_format` values are `markdown`, `pdf`, `html`, `text`, `image`, `audio`, `video`, `csv`, `spreadsheet`, `json`, `yaml`, and `other`.

A v1 BibTeX sidecar uses this YAML contract:

```yaml
record_id: SRC-0001
record_type: bibtex
status: active
provider: inspire
provider_priority: 1
providers_tried:
  - inspire
lookup_id: arxiv:1808.02002
bibtex_key: Schmidt:2018
fetched_date: 2026-05-18
source_bib_path: wiki_records/bibtex/SRC-0001.bib
```

BibTeX sidecars live under `wiki_records/bibtex/` as `.yaml` files beside canonical per-source `.bib` files. Active sidecars must use `wiki_records/bibtex/SRC-XXXX.bib`, and each active per-source `.bib` file must contain exactly one BibTeX entry. The generated `wiki_records/bibtex/references.bib` export is non-canonical and must match the deterministic active export when present.

A v1 relation record uses this YAML contract:

```yaml
record_id: REL-0001
record_type: relation
status: active
source_record_id: SRC-0001
target_record_id: SRC-0002
relation_type: cites
direction: source_to_target
evidence: []
created_date: 2026-05-16
reviewed_date:
confidence: high
```

Required relation record fields are `record_id`, `record_type`, `status`, `source_record_id`, `target_record_id`, `relation_type`, `direction`, `evidence`, `created_date`, and `confidence`.

Optional relation record fields are `reviewed_date`.

The relation record field set is closed in v1. Unknown fields are invalid. Use `record_id` for relation identity; do not use `relation_id`.

`record_type` must be `relation` for relation records.

Controlled relation `status` values are exactly `active` and `archived`.

Controlled `relation_type` values are `cites`, `builds_on`, `extends`, `supports`, `contradicts`, `revises`, `duplicates`, `supersedes`, `uses_dataset`, `uses_method`, `same_topic`, `same_entity`, `background_for`, and `responds_to`.

Controlled `direction` values are exactly `source_to_target`.

Controlled `confidence` values are `low`, `medium`, `high`, and `unknown`.

Conditional relation record rules:

- `record_id` must look like `REL-0001` and match the filename stem.
- `source_record_id` and `target_record_id` must point to existing source records.
- `source_record_id` must not equal `target_record_id`.
- `evidence` must be a list and may be empty.
- `created_date` is required and must be `YYYY-MM-DD`.
- `reviewed_date` may be blank; when present it must be `YYYY-MM-DD`.
- only `active` relations render in source-summary pages.
- archived relations remain records for auditability but must not render.
- processed duplicate source records require an active `duplicates` relation to `duplicate_of`.
- processed superseded source records require an active `supersedes` relation to `superseded_by`.

Relation type group headings are rendered in the fixed relation vocabulary order. Bullets within each group are ordered by target source title, then relation `record_id`. Link targets use the target source `page_path` relative to `wiki_pages/` without `.md`; link labels use the target source record `title`.

## Review Policy

Schema changes, exception-like rules, semantic rewrites, duplicate merges, superseding sources, relation record creation or semantic relation changes, relation type vocabulary changes, archival, deletion, and new durable synthesis require human approval. Schema proposals must use the block format in `WIKI_SCHEMA_PROPOSALS.md` before approval.

## User Preferences

Keep structured data separate from readable pages. Keep page frontmatter minimal and Obsidian-compatible. Prefer source records for machine-readable facts and readable pages for human-oriented summaries, synthesis, indexes, logs, and open questions. Tags are for `wiki_pages/` only and do not belong in canonical record YAML.

## Schema Evolution

Top-level schema sections are fixed. Schema rules and subsections must stay generic. Generic schema changes are proposed in `WIKI_SCHEMA_PROPOSALS.md` using the machine-checkable proposal block format. Entry-specific exception rules do not belong in the schema. If an agent encounters an entry-specific exception request, it must route it to human review as a question or schema proposal instead of adding it directly to the schema.
