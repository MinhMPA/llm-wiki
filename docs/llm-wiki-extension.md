# Extending LLM Wiki

This guide is for future implementers extending the portable LLM Wiki skill.

## Extension Principles

Keep the core portable:

- shared behavior belongs in `llm-wiki/core/`;
- host-specific trigger files belong in `llm-wiki/adapters/`;
- starter wiki behavior must be understandable as plain markdown;
- scripts must remain deterministic and standard-library-only unless there is an explicit packaging decision to change that;
- `WIKI_SCHEMA.md` remains the wiki-level source of truth.

Do not add entry-specific exceptions to `WIKI_SCHEMA.md`. Schema rules must describe generic classes of records, pages, workflows, or review policies.

## Add A Schema Rule

Use the proposal queue:

1. Copy the template in `WIKI_SCHEMA_PROPOSALS.md`.
2. Place the proposal under `## Pending`.
3. Explain the generic rule and why it is not entry-specific.
4. Wait for human approval.
5. Move the proposal to `## Approved` or `## Rejected`.
6. Apply approved changes to `WIKI_SCHEMA.md`.
7. Update `wiki_pages/log.md`.
8. Update validator tests if the rule is machine-checkable.

Do not silently change top-level schema sections. They are fixed in v1.

## Add A Record Field

To add a source record field:

1. Propose the field in `WIKI_SCHEMA_PROPOSALS.md`.
2. Define whether it is required, optional, or conditional.
3. Add it to `WIKI_SCHEMA.md`.
4. Add it to `llm-wiki/core/references/record-contracts.md`.
5. Add it to `ALLOWED_SOURCE_FIELDS` in `validate_wiki.py`.
6. Add validation rules and tests if the field has constraints.
7. Update application examples if users must write the field manually.

Because records are schema-closed, adding only documentation is not enough. The validator must also know the field.

## Extend Bibliography Support

Changing bibliography behavior requires schema, docs, validation, scripts, and tests to move together.

Use the schema proposal queue before changing:

- source bibliography fields such as `arxiv_id`, `doi`, or `bibtex_key`;
- BibTeX sidecar fields;
- provider order or provider vocabulary;
- fetch eligibility;
- unresolved/manual sidecar rules;
- export ordering or filtering.

After approval, update `WIKI_SCHEMA.md`, `llm-wiki/core/references/record-contracts.md`, `llm-wiki/core/references/bibliography.md`, `validate_wiki.py`, `fetch_bibtex.py`, `export_bibtex.py`, and focused tests in the same implementation.

Do not add Google Scholar scraping or title/author search as a small patch. Those would change the reliability contract and need a separate proposal.

## Add A Page Type

To add a page type:

1. Propose the page type in `WIKI_SCHEMA_PROPOSALS.md`.
2. Add it to `WIKI_SCHEMA.md`.
3. Add it to `llm-wiki/core/references/page-contracts.md`.
4. Add it to `PAGE_TYPES` in `validate_wiki.py`.
5. Add or update starter directories only when the page type needs a stable home.
6. Add tests for valid and invalid page frontmatter.

Pages remain human-readable markdown. Keep structured machine facts in `wiki_records/` unless they are only for human browsing.

## Extend The Validator

Validator changes should follow this sequence:

1. Add a failing test in `tests/test_validate_wiki.py`.
2. Implement the smallest deterministic check.
3. Keep error messages stable enough for tests and automation.
4. Run the full test suite.

The validator should check concrete contracts. It should not judge broad principles, citation adequacy, or semantic truth.

## Extend Source Relations

Changing relation behavior requires schema, docs, validation, rendering, and tests to move together.

Use the schema proposal queue before changing:

- relation record fields;
- allowed `relation_type` values;
- managed `Related sources` heading or bullet format;
- active/archived rendering behavior;
- duplicate or superseded mirror rules;
- renderer write behavior.

After approval, update `WIKI_SCHEMA.md`, `llm-wiki/core/references/record-contracts.md`, `llm-wiki/core/references/page-contracts.md`, `validate_wiki.py`, `render_relations.py`, and the focused validator/renderer tests in the same implementation.

Do not add entry-specific relation exceptions to the schema. If one source needs special treatment, route it to human review instead of adding a one-off rule.

## Extend The Initializer

Initializer changes should preserve merge-safety:

- no deleting user files;
- no overwriting without `--force`;
- no writing through symlinks in starter-managed paths;
- deterministic summary output;
- clear nonzero exits for conflicts.

Add tests in `tests/test_init_llm_wiki.py` before changing behavior.

## Add A Host Adapter

A new host adapter should stay thin. It should:

- point to `../../core/README.md`;
- point to the relevant `../../core/references/*.md` files;
- tell the host agent to read `WIKI_SCHEMA.md` inside a wiki before editing;
- avoid duplicating record, page, or workflow rules already defined in the core.

If an adapter needs substantial behavior, consider whether that behavior belongs in `llm-wiki/core/` instead.

## Future Packaging

The implemented v1 is a portable skill folder. Future packaging can proceed in this order:

1. Use the skill in Claude Code and ChatGPT Codex.
2. Package it as a plugin after the workflow stabilizes.
3. Add optional MCP tools for operations that benefit from a long-lived tool server.
4. Extract a standalone CLI/package only if users need non-agent automation.

Subagent-driven synthesis drafting is documented as an advanced workflow, but v1 does not require host support for background agents.
