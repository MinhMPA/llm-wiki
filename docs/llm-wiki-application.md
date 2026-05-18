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
arxiv_id:
doi:
bibtex_key:
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

## Add Source Relations

Create relation records under `wiki_records/relations/` when one source should point to another in Obsidian graph view:

```yaml
record_id: REL-0001
record_type: relation
status: active
source_record_id: SRC-0001
target_record_id: SRC-0002
relation_type: background_for
direction: source_to_target
evidence: []
created_date: 2026-05-16
reviewed_date:
confidence: high
```

For example, a safe-sleep guidance source can mark a hospital discharge checklist as `background_for`. The renderer turns active outgoing relations into managed links:

```bash
python3 llm-wiki/core/scripts/render_relations.py path/to/wiki
python3 llm-wiki/core/scripts/render_relations.py path/to/wiki --apply
```

The first command previews source pages that would change. The second rewrites only managed `## Related sources` sections. Then run validation.

## Manage BibTeX

For active paper sources, add exact identifiers to the source record when available:

```yaml
source_type: paper
arxiv_id: 1808.02002
doi:
bibtex_key:
```

Fetch BibTeX after ingest when you need citation artifacts. Run the command on the wiki root, not on `raw/`; the fetcher reads source records under `wiki_records/sources/`.

```bash
python3 llm-wiki/core/scripts/fetch_bibtex.py path/to/wiki SRC-0001
python3 llm-wiki/core/scripts/fetch_bibtex.py path/to/wiki SRC-0001 --apply
```

The first command previews. The second writes `wiki_records/bibtex/SRC-0001.bib` and `wiki_records/bibtex/SRC-0001.yaml`.

For a whole wiki, fetch missing entries in two steps:

```bash
python3 llm-wiki/core/scripts/fetch_bibtex.py path/to/wiki --missing
python3 llm-wiki/core/scripts/fetch_bibtex.py path/to/wiki --missing --apply
```

Use `--retry-unresolved` to retry sources previously marked unresolved. Use `--all` only when you intentionally want to revisit every eligible active paper source.

The fetcher tries INSPIRE first. To enable the ADS fallback, set an ADS token after core installation:

```bash
export ADS_API_TOKEN="..."
```

Then retry the fetch. The token is runtime configuration and should not be written into wiki files, docs, git, or shared shell commands. Regenerate the token in ADS if it is exposed.

Export a draft-ready bibliography:

```bash
python3 llm-wiki/core/scripts/export_bibtex.py path/to/wiki
python3 llm-wiki/core/scripts/export_bibtex.py path/to/wiki --apply
```

The generated file is `wiki_records/bibtex/references.bib`. It includes active entries only and can also be written to a LaTeX draft with:

```bash
python3 llm-wiki/core/scripts/export_bibtex.py path/to/wiki --output /path/to/draft/references.bib --apply
```

Validate after fetching or exporting:

```bash
python3 llm-wiki/core/scripts/validate_wiki.py path/to/wiki
```

## Filing Query Results

When a query produces durable synthesis worth keeping:

1. Ask for human approval before writing a durable synthesis page.
2. File it under `wiki_pages/synthesis/`.
3. Use source-record citations.
4. Update `wiki_pages/index.md`.
5. Add a log entry.
6. Run the validator.

Do not put human navigation metadata such as `tags` into source records. Tags belong only in `wiki_pages/` frontmatter.
