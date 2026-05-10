# LLM Wiki

LLM Wiki is a portable, schema-driven skill for building a maintained markdown knowledge base with an LLM agent.

Instead of treating sources as a pile of files to search every time, LLM Wiki turns them into:

- structured source records in `wiki_records/`;
- readable Obsidian-friendly pages in `wiki_pages/`;
- source-record citations;
- an index and log;
- deterministic validation reports.

The core design goal is portability. The workflow is stored as files that can be copied into different agent environments, while the wiki itself remains plain markdown and YAML.

## Quick Start

Create a wiki:

```bash
python3 llm-wiki/core/scripts/init_llm_wiki.py path/to/wiki
```

Validate it:

```bash
python3 llm-wiki/core/scripts/validate_wiki.py path/to/wiki
```

Ask your agent to read:

```text
path/to/wiki/WIKI_SCHEMA.md
```

Then tell the agent what source to ingest or what question to answer.

## What Gets Created

The initializer creates this layout:

```text
path/to/wiki/
  WIKI_SCHEMA.md
  WIKI_SCHEMA_PROPOSALS.md
  AGENTS.md
  CLAUDE.md
  raw/
  wiki_records/
    sources/
  wiki_pages/
    index.md
    log.md
    questions.md
    sources/
    entities/
    concepts/
    synthesis/
```

`WIKI_SCHEMA.md` is the operating contract. `AGENTS.md` and `CLAUDE.md` are pointer files that tell Codex and Claude Code to read the schema.

## Install As A Skill

Keep the bundle layout intact:

```text
llm-wiki/
  adapters/
    codex/SKILL.md
    claude/SKILL.md
  core/
```

The adapter files use relative paths such as `../../core/README.md`. If you copy an adapter without the core beside it, the skill will not have its shared instructions.

For Codex, use `llm-wiki/adapters/codex/SKILL.md` as the host entrypoint. For Claude Code, use `llm-wiki/adapters/claude/SKILL.md`.

## Add A Source

Put local source artifacts under `raw/`, or use an external URL. Then create one source record:

```yaml
record_id: SRC-0001
record_type: source
status: active
duplicate_of:
superseded_by:
source_storage: local
raw_path: raw/example.md
source_url:
page_path: wiki_pages/sources/example.md
source_type: article
source_format: markdown
title: Example Source
authors: []
added_date: 2026-05-11
processed_date: 2026-05-11
published_date:
content_fingerprint:
```

Then create a readable source summary:

```markdown
---
record_id: SRC-0001
page_type: source_summary
title: Example Source
aliases: []
tags:
  - source
---

# Example Source

Durable claims cite source records.[^SRC-0001]

[^SRC-0001]: `SRC-0001` - [[sources/example]]
```

Update `wiki_pages/index.md` and `wiki_pages/log.md`, then run the validator.

## Manage A Wiki

Use these recurring operations:

- `ingest`: process one source into one record, one source summary, index updates, and log updates.
- `query`: answer from `wiki_pages/` first, then consult records and sources when needed.
- `file`: save durable query results into `wiki_pages/synthesis/` only with human approval.
- `lint`: fix mechanical drift, but ask before semantic, schema, duplicate, archival, deletion, or synthesis changes.
- `validate`: run `validate_wiki.py` after edits.

The validator is structural. It checks file layout, schema headings, proposal blocks, source records, page frontmatter, mirrored titles, wiki links, and source-record citations. It does not judge whether every claim is sufficiently supported.

## Customize The Schema

The schema is living, but its top-level sections are fixed in v1.

To change schema behavior:

1. Add a generic proposal to `WIKI_SCHEMA_PROPOSALS.md`.
2. Keep entry-specific exceptions out of the schema.
3. Get human approval.
4. Apply the approved change to `WIKI_SCHEMA.md`.
5. Update references and validator tests when the change is machine-checkable.
6. Log the schema change.

Records are schema-closed. If you add a source record field, also update `ALLOWED_SOURCE_FIELDS` in `llm-wiki/core/scripts/validate_wiki.py`.

## Power User Tasks

### Reinitialize Without Losing Work

Run:

```bash
python3 llm-wiki/core/scripts/init_llm_wiki.py path/to/wiki
```

Existing files are skipped. Use `--force` only when you intend to overwrite starter-managed files:

```bash
python3 llm-wiki/core/scripts/init_llm_wiki.py path/to/wiki --force
```

The initializer rejects file/directory conflicts and symlinked starter-managed paths.

### Add A Page Type

Update all relevant layers:

1. `WIKI_SCHEMA.md`
2. `llm-wiki/core/references/page-contracts.md`
3. `PAGE_TYPES` in `validate_wiki.py`
4. starter wiki directories if the page type needs one
5. tests in `tests/test_validate_wiki.py`

### Add A Record Field

Update:

1. `WIKI_SCHEMA.md`
2. `llm-wiki/core/references/record-contracts.md`
3. `ALLOWED_SOURCE_FIELDS` in `validate_wiki.py`
4. validation logic if the field has constraints
5. tests and examples

### Optimize Low-Level Workflows

For small and medium wikis, start with `wiki_pages/index.md` and normal file search. Add tooling only when the wiki outgrows that.

Useful low-level improvements:

- add scripts for repetitive record creation;
- add local search over `wiki_pages/`;
- add CI that runs `validate_wiki.py`;
- add lint commands for mechanical fixes;
- add optional MCP tooling only for workflows that benefit from a long-lived server.

Do not move semantic decisions into automation. Duplicate merges, source supersession, schema changes, durable synthesis, and deletion require human approval.

## Documentation

- `docs/llm-wiki-application.md`: how to apply the skill to a wiki.
- `docs/llm-wiki-implementation.md`: implementation reference.
- `docs/llm-wiki-extension.md`: extension guide.
- `docs/llm-wiki-packaging.md`: packaging decision and future path.

The original idea essay is in `llm-wiki.md`.

## Verify The Repository

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The tests cover starter assets, initialization, validation, and an end-to-end source-record workflow.
