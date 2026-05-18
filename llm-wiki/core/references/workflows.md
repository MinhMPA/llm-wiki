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
- managed `Related sources` sections rendered from active relation records

Lint must request approval before semantic, schema, or destructive changes:

- duplicate merges
- superseding sources
- evidence interpretation changes
- source relation creation, removal, or semantic relation changes
- schema rule changes
- new synthesis pages
- deletion or archival
- substantive rewrites

## Bibliography Workflow

Use bibliography maintenance after ingest, under the lint boundary:

1. Run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT SRC-0001` to preview lookup.
2. Run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT SRC-0001 --apply` to write canonical BibTeX artifacts.
3. For bulk maintenance, run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT --missing` and then rerun with `--apply`.
4. Use `--retry-unresolved` to retry unresolved sidecars, or `--all` to revisit every eligible active paper source.
5. Run `python3 llm-wiki/core/scripts/export_bibtex.py WIKI_ROOT` to preview aggregate export changes.
6. Run `python3 llm-wiki/core/scripts/export_bibtex.py WIKI_ROOT --apply` to write `wiki_records/bibtex/references.bib`.
7. Run `python3 llm-wiki/core/scripts/validate_wiki.py WIKI_ROOT`.

## Schema Proposal Workflow

Agents may add proposals to `WIKI_SCHEMA_PROPOSALS.md` under `Pending`. Agents may move proposals to `Approved` or `Rejected` only after explicit human approval or rejection. Approved proposals may then be applied to `WIKI_SCHEMA.md` and logged in `wiki_pages/log.md`.

## Source Relation Workflow

To add or change a source-to-source relationship:

1. Confirm the semantic relation with a human when it changes source meaning, duplicate status, or supersession.
2. Write or update one relation record under `wiki_records/relations/`.
3. Run `python3 llm-wiki/core/scripts/render_relations.py WIKI_ROOT` to preview managed section changes.
4. Run `python3 llm-wiki/core/scripts/render_relations.py WIKI_ROOT --apply` to mechanically rewrite only managed `Related sources` sections.
5. Run `python3 llm-wiki/core/scripts/validate_wiki.py WIKI_ROOT`.

The renderer must not rewrite source-summary prose, citations, frontmatter, or ordinary Obsidian links outside the managed section.
