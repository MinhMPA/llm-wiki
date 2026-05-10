# Wiki Schema

## Purpose

This wiki preserves knowledge as portable files with explicit records, readable pages, version history, custom schema control, local/private operation, model choice, ongoing maintenance, and auditability.

## Directory Layout

- `WIKI_SCHEMA.md`: approved operating contract.
- `WIKI_SCHEMA_PROPOSALS.md`: maintained proposal queue for schema changes.
- `AGENTS.md`: pointer file for ChatGPT Codex.
- `CLAUDE.md`: pointer file for Claude Code.
- `raw/`: local immutable source artifacts.
- `wiki_records/`: structured authoritative records.
- `wiki_pages/`: human-readable maintained wiki pages.

## Page Types

Allowed page types are `source_summary`, `entity`, `concept`, `synthesis`, `index`, `log`, and `questions`.

## Evidence And Citations

Durable claims cite source records with footnotes such as `[^SRC-0001]`. The footnote body must begin with the matching record ID in backticks.

## Ingest Workflow

Processing a source creates or updates a source record, a source summary unless explicitly record-only, the index, and the log. Entity, concept, synthesis, and question pages are updated when supported by the source.

## Query Workflow

Answer from wiki pages first, then consult records and sources when needed. Durable synthesis may be filed only with human approval.

## Lint Workflow

Mechanical drift may be fixed automatically. Semantic, schema, or destructive changes require human approval.

## Naming Conventions

Use explicit short field names. Use universal fields when they remain precise, such as `record_id`.

## Review Policy

Schema changes, exception-like rules, semantic rewrites, duplicate merges, superseding sources, archival, deletion, and new durable synthesis require human approval.

## User Preferences

Keep structured data separate from readable pages. Keep page frontmatter minimal and Obsidian-compatible.

## Schema Evolution

Top-level schema sections are fixed. Generic schema changes are proposed in `WIKI_SCHEMA_PROPOSALS.md`. Entry-specific exceptions are not allowed in the schema without explicit human approval.
