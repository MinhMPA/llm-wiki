# Source Relations for Obsidian Graph View

## Purpose

Implement first-class source-to-source links in `llm-wiki` so Obsidian and similar Markdown graph tools can show meaningful relationships between sources.

The current system supports source records, source summary pages, and source-record citations. However, it does not yet model relationships between sources as first-class graph edges. Obsidian graph view is built from Markdown links, so relationships must appear visibly in source summary pages using readable `[[...]]` links.

This specification defines a minimal v1 source-relation system.

## Non-goals

Do not implement any of the following in this task:

- full RAG;
- vector search;
- graph database;
- UI;
- Obsidian plugin;
- automatic semantic relation inference;
- autonomous duplicate merging;
- destructive source archival;
- relation-aware query answering.

The goal is a schema-governed relation layer that is useful for Obsidian graph view now and future RAG later.

## Existing project context

`llm-wiki` currently has the following relevant concepts:

```text
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
WIKI_SCHEMA.md
WIKI_SCHEMA_PROPOSALS.md
AGENTS.md
CLAUDE.md
llm-wiki/core/references/record-contracts.md
llm-wiki/core/references/page-contracts.md
llm-wiki/core/references/workflows.md
llm-wiki/core/scripts/init_llm_wiki.py
llm-wiki/core/scripts/render_relations.py
llm-wiki/core/scripts/validate_wiki.py
tests/
```

Current design:

- `raw/` stores local source artifacts.
- `wiki_records/sources/*.yaml` stores canonical source metadata.
- `wiki_pages/sources/*.md` stores human-readable source summaries.
- source-record citations link durable claims back to source records.
- validation checks structure, records, frontmatter, links, and citations.

Missing design:

- source-to-source relations;
- Obsidian-visible links between source pages;
- validation that relation records and rendered links stay consistent;
- readable source page titles/slugs optimized for graph view.

## Core design

Add two complementary representations of source relations:

```text
wiki_records/relations/*.yaml
```

for canonical machine-readable relation records, and:

```markdown
## Related sources
- [[sources/readable-source-title|Readable Source Title]] (`REL-0001`)
```

inside source summary pages for Obsidian-visible graph links.

The relation record is canonical. The Markdown link is required for graph visibility.

## Directory layout

New starter wikis should include:

```text
wiki_records/
  sources/
  relations/
```

`wiki_records/relations/` contains relation records named by stable sequential IDs:

```text
wiki_records/relations/REL-0001.yaml
wiki_records/relations/REL-0002.yaml
```

## Relation record contract

A v1 relation record has this shape:

```yaml
record_id: REL-0001
record_type: relation
status: active
source_record_id: SRC-0001
target_record_id: SRC-0002
relation_type: cites
direction: source_to_target
evidence: []
created_date: 2026-05-16
reviewed_date:
confidence: high
```

### Required fields

- `record_id`
- `record_type`
- `status`
- `source_record_id`
- `target_record_id`
- `relation_type`
- `direction`
- `evidence`
- `created_date`
- `confidence`

### Optional fields

- `reviewed_date`

### Field rules

- `record_id` must look like `REL-0001` and match the filename stem.
- `record_type` must be `relation`.
- `status` must be one of:
  - `active`
  - `archived`
- `source_record_id` must reference an existing source record.
- `target_record_id` must reference an existing source record.
- `source_record_id` must not equal `target_record_id`.
- `direction` must be `source_to_target` in v1.
- `evidence` must be a list and may be empty.
- `confidence` must be one of:
  - `low`
  - `medium`
  - `high`
  - `unknown`
- `created_date` is required.
- `reviewed_date` may be blank.
- unknown fields are invalid; `notes` and `relation_id` are not valid v1 fields.

### Allowed relation types

Use this small v1 vocabulary:

- `cites`
- `builds_on`
- `extends`
- `supports`
- `contradicts`
- `revises`
- `duplicates`
- `supersedes`
- `uses_dataset`
- `uses_method`
- `same_topic`
- `same_entity`
- `background_for`
- `responds_to`

Do not add additional relation types unless the schema is updated and validation is updated.

## Source summary page rendering

Every source summary page that participates in outgoing relations should include a `Related sources` section.

Example:

```markdown
## Related sources

### Cites
- [[sources/readable-source-title|Readable Source Title]] (`REL-0001`)

### Builds on
- [[sources/another-readable-title|Another Readable Title]] (`REL-0002`)
```

Rules:

- Relation records are canonical.
- Outgoing relation links must be rendered in the source summary page of `source_record_id`.
- Links must be regular Obsidian wiki links.
- Link targets should use readable source page slugs.
- Link labels should use human-readable source titles.
- Include the relation ID near the link for auditability.
- Only active relation records render. Archived relation records remain for auditability but must not render.
- Managed `Related sources` sections may contain only blank lines, relation type group headings, and managed relation bullets.
- Do not require incoming backlink sections in v1.
- Do not require every source to have relations.
- Omit `## Related sources` when a source has no active outgoing relations.

## Source title and slug policy

Obsidian graph nodes are more useful when source page names are readable. Source summary page paths should prefer readable slugs, not opaque IDs.

Prefer:

```text
wiki_pages/sources/hospital-discharge-instructions.md
wiki_pages/sources/aap-safe-sleep-guidance.md
wiki_pages/sources/smith-2024-field-level-inference.md
```

Avoid:

```text
wiki_pages/sources/SRC-0001.md
```

### Slug rules

- lowercase;
- hyphen-separated;
- no spaces;
- no opaque source ID unless no title is available;
- derived from title, authors, and year when available;
- resolve collisions with a short suffix, preferably year or source ID;
- keep source record IDs canonical and stable.

### Source page frontmatter

Source summary pages should preserve:

```yaml
---
record_id: SRC-0001
page_type: source_summary
title: AAP Safe Sleep Guidance
aliases:
  - SRC-0001
  - Safe Sleep Guidance
tags:
  - source
  - official-guidance
---
```

Rules:

- `record_id` remains the canonical stable ID.
- `title` should be human-readable.
- `title` should mirror the source record when a backing record exists.
- `aliases` should include useful alternate names, including source ID and short title.
- `tags` remain human navigation metadata.

## Validator requirements

Update `llm-wiki/core/scripts/validate_wiki.py`.

Validation should check:

### Directory and file checks

- `wiki_records/relations/` exists.
- relation YAML files are named as `REL-0001.yaml`, `REL-0002.yaml`, etc.
- relation IDs are unique.

### Schema checks

- relation YAML files are schema-closed.
- all required relation fields exist.
- unknown fields are invalid.
- `record_id` matches filename stem.
- `record_type` is `relation`.
- `status`, `direction`, `relation_type`, and `confidence` use allowed values.
- `evidence` is a list.

### Referential checks

- `source_record_id` exists.
- `target_record_id` exists.
- self-relations fail validation.
- source and target records have source summary pages when rendered graph links are required.

### Rendered-link checks

For each active relation:

- locate the source summary page for `source_record_id`;
- locate the target source summary page for `target_record_id`;
- verify that the source summary page contains a Markdown wiki link to the target source page;
- verify that the relation ID appears near the rendered relation link;
- fail if the relation record exists but the rendered outgoing link is missing;
- fail if the rendered link points to the wrong target page.
- fail if an archived relation is rendered.
- fail if unmanaged content appears inside a managed `Related sources` section.

### Duplicate and supersession consistency

If source records use `duplicate_of` or `superseded_by`, validation should ensure these fields do not contradict relation records of type:

- `duplicates`
- `supersedes`

Do not attempt to prove semantic correctness. Only validate structural consistency.

## Initializer requirements

Update `llm-wiki/core/scripts/init_llm_wiki.py` so starter wikis include:

```text
wiki_records/
  sources/
  relations/
```

Reinitialization should preserve existing user files. Do not overwrite user-created relation records. Respect the existing `--force` behavior for starter-managed files.

## Renderer requirements

Add `llm-wiki/core/scripts/render_relations.py`.

The renderer should:

- dry-run by default and report pages that would change;
- write only when `--apply` is provided;
- rewrite only managed `## Related sources` sections;
- insert sections when active outgoing relations exist;
- remove stale sections when no active outgoing relations remain;
- refuse malformed managed sections that contain unmanaged prose or ambiguous structure;
- preserve ordinary page prose, frontmatter, citations, and freeform Obsidian links outside the managed section.

## Documentation requirements

Update relevant documentation:

- `llm-wiki/core/assets/starter-wiki/WIKI_SCHEMA.md`
- `llm-wiki/core/references/record-contracts.md`
- `llm-wiki/core/references/page-contracts.md`
- `llm-wiki/core/references/workflows.md`
- `docs/llm-wiki-extension.md`
- any implementation docs that describe records, pages, validation, or schema extension.

Document:

- relation record contract;
- related-source page section;
- readable source slug/title policy;
- validation rules;
- why rendered Markdown links are needed for Obsidian graph view;
- how source relations will support future relation-aware retrieval/RAG.

If the project convention requires schema evolution through `WIKI_SCHEMA_PROPOSALS.md`, add a proposal for first-class source relations before applying the schema update.

## Tests

Add or update tests under `tests/`.

Required tests:

- starter wiki contains `wiki_records/relations/`;
- valid relation record passes validation;
- relation with missing target source fails;
- relation with missing source source fails;
- relation with invalid `relation_type` fails;
- relation with invalid `confidence` fails;
- relation with self-edge fails;
- relation not rendered in source summary page fails;
- rendered related-source link to the wrong page fails;
- relation ID missing from rendered link line fails;
- readable source page path/title/aliases examples pass validation;
- duplicate/superseded consistency checks behave as expected.

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

All tests should pass.

## Example

If the repository has an examples directory, add or update a minimal example wiki with two or three sources and one or two relations.

Example sources:

- `SRC-0001`: AAP Safe Sleep Guidance
- `SRC-0002`: Hospital Discharge Instructions

Example relation:

```yaml
record_id: REL-0001
record_type: relation
status: active
source_record_id: SRC-0002
target_record_id: SRC-0001
relation_type: supports
direction: source_to_target
evidence:
  - "Hospital instructions repeat the same core safe-sleep guidance."
created_date: 2026-05-16
reviewed_date:
confidence: high
```

Rendered source summary section:

```markdown
## Related sources

### Supports
- [[sources/aap-safe-sleep-guidance|AAP Safe Sleep Guidance]] (`REL-0001`)
```

## Implementation principles

Preserve the existing design principles:

- canonical state lives in Markdown/YAML files;
- validation is deterministic;
- use standard-library Python unless there is a strong reason not to;
- keep semantic decisions human-approved;
- do not infer relations automatically in this task;
- do not add heavyweight dependencies;
- do not make `.wiki_index/` or any future retrieval index canonical;
- do not turn source relations into a graph database.

## Deliverables

At the end, provide:

- files changed;
- schema changes;
- validator changes;
- tests added or updated;
- test command result;
- limitations;
- recommended follow-up tasks.

Suggested follow-up tasks, not part of this implementation unless trivial:

- `export_graph.py` for GraphML/JSON/DOT;
- relation-aware RAG retrieval;
- Obsidian Dataview examples;
- relation lint/autofix command;
- optional incoming backlink section generation.
