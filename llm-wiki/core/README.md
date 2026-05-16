# LLM Wiki Portable Core

This core defines the agent-neutral LLM Wiki workflow.

An LLM Wiki is a schema-driven markdown knowledge base. `WIKI_SCHEMA.md` is the operating contract. `wiki_records/` stores structured authoritative records. `wiki_pages/` stores human-readable Obsidian-friendly pages. `raw/` stores local immutable source artifacts when sources are kept locally.

## Host-Agent Contract

An agent can use this core when it can:

1. Load markdown instructions from a skill folder.
2. Read sibling files by relative path.
3. Run or inspect bundled scripts.

Script execution is useful but not required for the markdown workflow to remain understandable.

## Start Here

- Read `references/workflows.md` for ingest, query, lint, and schema proposal workflows.
- Read `references/record-contracts.md` for structured records.
- Read `references/page-contracts.md` for wiki pages, Obsidian frontmatter, and citations.
- Read `references/validation.md` before changing validation behavior.
- Read `references/advanced-workflows.md` only when the host can use subagents or background workers.

## Scripts

- `scripts/init_llm_wiki.py TARGET [--force]` initializes or refreshes a starter wiki without deleting unrelated user files.
- `scripts/validate_wiki.py WIKI_ROOT` validates concrete structure, source records, page frontmatter, links, and source-record citations.
- `scripts/render_relations.py WIKI_ROOT [--apply]` renders managed `Related sources` sections from active relation records. It is dry-run by default and writes only with `--apply`.

Both scripts use only the Python standard library.
