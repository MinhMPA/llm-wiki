# LLM Wiki Workflows

## Ingest Workflow

Processing one source must produce or update:

1. One source record under `wiki_records/sources/`.
2. One source summary under `wiki_pages/sources/`, unless the source is explicitly record-only.
3. `wiki_pages/index.md`.
4. `wiki_pages/log.md`.

Update `wiki_pages/entities/`, `wiki_pages/concepts/`, `wiki_pages/synthesis/`, and `wiki_pages/questions.md` only when the source supports those updates.

The final ingest report must list records and pages created or updated, unresolved questions, and validation results.

## Query Workflow

Answer from `wiki_pages/` first, then consult `wiki_records/` and raw or external sources as needed. Durable synthesis may be filed into `wiki_pages/synthesis/` only with human approval. Filing a query result requires source-record citations, an index update, and a log entry.

## Lint Workflow

Lint may fix mechanical drift automatically:

- missing index entries for existing pages
- unambiguous broken links
- page frontmatter order and allowed fields
- mirrored page fields that drift from authoritative records
- log entries for lint or validation runs

Lint must request approval before semantic, schema, or destructive changes:

- duplicate merges
- superseding sources
- evidence interpretation changes
- schema rule changes
- new synthesis pages
- deletion or archival
- substantive rewrites

## Schema Proposal Workflow

Agents may add proposals to `WIKI_SCHEMA_PROPOSALS.md` under `Pending`. Agents may move proposals to `Approved` or `Rejected` only after explicit human approval or rejection. Approved proposals may then be applied to `WIKI_SCHEMA.md` and logged in `wiki_pages/log.md`.
