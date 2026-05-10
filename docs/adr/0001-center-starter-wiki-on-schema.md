# Center the starter wiki on an explicit schema

The portable LLM Wiki starter uses `WIKI_SCHEMA.md` as the canonical operating file and `wiki_pages/` for generated markdown pages. We chose explicit names over friendlier names like `WIKI.md` and `pages/` because the skill is schema-driven: agents should treat the schema as the central contract, not as a casual overview page. Host-specific files such as `AGENTS.md` or `CLAUDE.md` may point to the schema, but they are not the source of truth.

## Status

Accepted and implemented.

## Consequences

- Platform-specific files stay thin.
- `WIKI_SCHEMA.md` carries the operational record, page, citation, workflow, review, and schema-evolution rules.
- Schema proposals live in `WIKI_SCHEMA_PROPOSALS.md`.
- Structured records live under `wiki_records/`, while human-readable pages live under `wiki_pages/`.
- Validator behavior follows the schema-centered contract and rejects drift such as unknown source record fields or pages without required frontmatter.
