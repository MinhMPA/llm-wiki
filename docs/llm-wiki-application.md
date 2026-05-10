# Applying LLM Wiki

This how-to guide is for a user or agent applying the portable LLM Wiki skill to a real knowledge base.

## Create A Wiki

Run the initializer from the repository root:

```bash
python3 llm-wiki/core/scripts/init_llm_wiki.py path/to/wiki
```

The initializer copies the starter wiki into the target directory. It is merge-safe by default:

- missing starter files are created;
- existing files are skipped;
- unrelated user files are left alone;
- symlinked starter-managed paths are rejected so the initializer cannot write through a link outside the target wiki.

Use `--force` only when you intentionally want starter-managed files overwritten:

```bash
python3 llm-wiki/core/scripts/init_llm_wiki.py path/to/wiki --force
```

Even with `--force`, conflicting path types and symlinks are rejected instead of replaced.

## Read The Schema First

Before ingesting, querying, linting, or changing a wiki, read:

```text
path/to/wiki/WIKI_SCHEMA.md
```

`AGENTS.md` and `CLAUDE.md` are pointer files. They are not the schema.

## Add A Source

Create a source record under `wiki_records/sources/`:

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

For local sources, `raw_path` must point under `raw/` and the file must exist. For external sources, `source_url` is required.

Create the source summary page under `wiki_pages/sources/`:

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

Durable claims cite the source record.[^SRC-0001]

[^SRC-0001]: `SRC-0001` - [[sources/example]]
```

Then update `wiki_pages/index.md` and `wiki_pages/log.md`.

## Validate The Wiki

Run:

```bash
python3 llm-wiki/core/scripts/validate_wiki.py path/to/wiki
```

A valid wiki exits with status `0` and prints `valid: ...`.

Validation is structural. It checks records, page frontmatter, mirrored titles, proposal sections, wiki links, and source-record citations. It does not decide whether every claim has enough evidence.

## Filing Query Results

When a query produces durable synthesis worth keeping:

1. Ask for human approval before writing a durable synthesis page.
2. File it under `wiki_pages/synthesis/`.
3. Use source-record citations.
4. Update `wiki_pages/index.md`.
5. Add a log entry.
6. Run the validator.

Do not put human navigation metadata such as `tags` into source records. Tags belong only in `wiki_pages/` frontmatter.
