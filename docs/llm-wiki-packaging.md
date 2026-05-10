# LLM Wiki Packaging Decision

LLM Wiki starts as a portable skill folder with an agent-neutral core and thin host-specific adapters.

The core value is not a single model, product, or runtime. The value is a schema-driven workflow for turning raw or external sources into maintained records, readable wiki pages, citations, logs, and validation reports. For that reason, shared behavior belongs in `llm-wiki/core/`, while host-specific trigger metadata belongs in `llm-wiki/adapters/`.

## Implemented V1

The v1 implementation includes:

- an agent-neutral core under `llm-wiki/core/`;
- thin adapters for ChatGPT Codex and Claude Code under `llm-wiki/adapters/`;
- a schema-centered starter wiki under `llm-wiki/core/assets/starter-wiki/`;
- a merge-safe initializer at `llm-wiki/core/scripts/init_llm_wiki.py`;
- a deterministic validator at `llm-wiki/core/scripts/validate_wiki.py`;
- tests for starter assets, initialization, validation, and the end-to-end source workflow.

## Future Build Order

1. Use the skill in Claude Code and ChatGPT Codex.
2. Package the skill as a plugin once the workflow stabilizes.
3. Add optional MCP tools for operations that benefit from a long-lived tool server.
4. Extract a standalone package only if users need CLI/library or CI automation outside agent environments.

## Guiding Principles

- Portability
- Model choice
- Version history
- Maintenance automation
- Custom schemas
- Obsidian-native organization
- Local/private operation
- Longitudinal records
- Auditability

These are guiding principles, not validator-enforced absolutes. Operational artifacts should express the principles without naming competing products.
