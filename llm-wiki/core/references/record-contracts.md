# Record Contracts

## Source Records

Source records live in `wiki_records/sources/` as `.yaml` files named by stable sequential IDs:

```text
wiki_records/sources/SRC-0001.yaml
```

Required fields:

- `record_id`
- `record_type`
- `status`
- `source_storage`
- `source_type`
- `title`
- `authors`
- `added_date`

Full v1 field set:

```yaml
record_id: SRC-0001
record_type: source
status: active
duplicate_of:
superseded_by:
source_storage: local
raw_path: raw/articles/example.md
source_url: https://example.com/article
page_path: wiki_pages/sources/example.md
source_type: article
source_format: markdown
title: Example Article
authors: []
added_date: 2026-05-10
processed_date:
published_date:
content_fingerprint:
arxiv_id: 1808.02002
doi:
bibtex_key:
```

Optional bibliography identifier fields:

- `arxiv_id`
- `doi`
- `bibtex_key`

The v1 field set is closed. Unknown source record fields are invalid. Human navigation fields such as `tags` belong in `wiki_pages/` frontmatter, not in canonical record YAML. `bibtex_key` belongs in source records and BibTeX sidecars, not page frontmatter.

Allowed `status` values:

- `active`
- `archived`
- `superseded`
- `duplicate`

Allowed `source_storage` values:

- `local`
- `external`

Allowed `source_type` values:

- `article`
- `paper`
- `book`
- `chapter`
- `transcript`
- `note`
- `image`
- `dataset`
- `video`
- `audio`
- `report`
- `documentation`
- `other`

Allowed `source_format` values:

- `markdown`
- `pdf`
- `html`
- `text`
- `image`
- `audio`
- `video`
- `csv`
- `spreadsheet`
- `json`
- `yaml`
- `other`

## Conditional Rules

- `record_type` must be `source`.
- `raw_path` is required when `source_storage` is `local` and must point under `raw/`.
- `source_url` is required when `source_storage` is `external`.
- `processed_date` is required once `page_path` points to an existing source summary.
- When `page_path` points to an existing page, that path must be a file whose frontmatter has `page_type: source_summary`.
- `duplicate_of` is required when `status` is `duplicate`.
- `superseded_by` is required when `status` is `superseded`.
- `content_fingerprint` may be blank; when present it must include an algorithm prefix such as `sha256:`.
- `authors` is a list and may be empty.

## Relation Records

Relation records live in `wiki_records/relations/` as `.yaml` files named by stable sequential IDs:

```text
wiki_records/relations/REL-0001.yaml
```

Required fields:

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

Full v1 field set:

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

The v1 field set is closed. Unknown relation record fields are invalid. Relation records use the universal `record_id` field; do not use `relation_id`.

Allowed `status` values:

- `active`
- `archived`

Allowed `relation_type` values:

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

Allowed `direction` values:

- `source_to_target`

Allowed `confidence` values:

- `low`
- `medium`
- `high`
- `unknown`

## Relation Conditional Rules

- `record_id` must look like `REL-0001` and match the filename stem.
- `record_type` must be `relation`.
- `source_record_id` and `target_record_id` must reference existing source records.
- `source_record_id` must not equal `target_record_id`.
- `evidence` must be a list and may be empty.
- `created_date` must be `YYYY-MM-DD`.
- `reviewed_date` may be blank; when present it must be `YYYY-MM-DD`.
- Only `active` relations render in managed `Related sources` sections.
- `archived` relations remain records for auditability but must not render.
- A processed source with `status: duplicate` and `duplicate_of` requires an active `duplicates` relation to the same target.
- A processed source with `status: superseded` and `superseded_by` requires an active `supersedes` relation to the same target.

## BibTeX Sidecars

BibTeX sidecars live in `wiki_records/bibtex/` as `.yaml` files named by source ID:

```text
wiki_records/bibtex/SRC-0001.yaml
```

Canonical per-source BibTeX entries live beside sidecars:

```text
wiki_records/bibtex/SRC-0001.bib
```

Full v1 field set:

```yaml
record_id: SRC-0001
record_type: bibtex
status: active
provider: inspire
provider_priority: 1
providers_tried:
  - inspire
lookup_id: arxiv:1808.02002
bibtex_key: Schmidt:2018
fetched_date: 2026-05-18
source_bib_path: wiki_records/bibtex/SRC-0001.bib
```

The BibTeX sidecar field set is closed. `record_type` must be `bibtex`. The generated aggregate `wiki_records/bibtex/references.bib` is non-canonical and must be regenerated from active sidecars and per-source `.bib` files.
