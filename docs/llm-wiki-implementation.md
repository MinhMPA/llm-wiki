# LLM Wiki Implementation Reference

This reference describes the implemented v1 portable LLM Wiki skill.

## Repository Layout

```text
llm-wiki/
  adapters/
    claude/SKILL.md
    codex/SKILL.md
  core/
    README.md
    assets/starter-wiki/
    references/
    scripts/
      init_llm_wiki.py
      validate_wiki.py
tests/
```

The adapters are thin host-specific entrypoints. Shared behavior lives in `llm-wiki/core/`.

## Starter Wiki Layout

The initializer creates this wiki shape:

```text
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

`WIKI_SCHEMA.md` is the operating contract. `AGENTS.md` and `CLAUDE.md` only point agents to the schema.

## Initializer

Command:

```bash
python3 llm-wiki/core/scripts/init_llm_wiki.py TARGET [--force]
```

Behavior:

- copies files from `llm-wiki/core/assets/starter-wiki/`;
- creates missing directories;
- skips existing files unless `--force` is set;
- overwrites existing starter-managed files only with `--force`;
- never deletes unrelated user files;
- rejects target-root file conflicts;
- rejects file-versus-directory conflicts;
- rejects symlinks in starter-managed target paths;
- prints `created:`, `skipped:`, and `overwritten:` summaries.

The initializer uses only the Python standard library.

## Validator

Command:

```bash
python3 llm-wiki/core/scripts/validate_wiki.py WIKI_ROOT
```

Behavior:

- exits `0` and prints `valid: WIKI_ROOT` when valid;
- exits `1` and prints deterministic errors to stderr when invalid;
- uses only the Python standard library.

The validator parses a small YAML subset:

- `key: value`;
- blank value as an empty string;
- `[]` as an empty list;
- block list items written as `  - value`.

It does not implement full YAML.

## Source Record Contract

Source records live in `wiki_records/sources/*.yaml`. The `record_id` must match the filename stem.

Required fields:

- `record_id`
- `record_type`
- `status`
- `source_storage`
- `source_type`
- `title`
- `authors`
- `added_date`

Allowed fields are closed to the v1 source record field set:

- `record_id`
- `record_type`
- `status`
- `duplicate_of`
- `superseded_by`
- `source_storage`
- `raw_path`
- `source_url`
- `page_path`
- `source_type`
- `source_format`
- `title`
- `authors`
- `added_date`
- `processed_date`
- `published_date`
- `content_fingerprint`

Unknown fields fail validation. This keeps canonical records machine-readable. Human navigation fields such as `tags` belong in page frontmatter, not in record YAML.

## Page Contract

Every markdown file under `wiki_pages/` must have frontmatter.

Allowed frontmatter fields:

- `record_id`
- `page_type`
- `title`
- `aliases`
- `tags`

Required frontmatter fields:

- `page_type`
- `title`
- `aliases`
- `tags`

`record_id` is required only when a page mirrors a structured source record.

`aliases` and `tags` must be lists. If a page mirrors a record and has a title, that title must match the record title.

## Citation Contract

Durable source-record citations use footnotes:

```markdown
Claim.[^SRC-0001]

[^SRC-0001]: `SRC-0001` - [[sources/example]]
```

The cited source record must exist. The footnote body must start with the matching record ID in backticks.

## Test Suite

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The tests cover starter layout, schema contracts, initializer behavior, validator behavior, and an end-to-end init-record-page-validate workflow.
