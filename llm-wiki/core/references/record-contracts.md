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
```

The v1 field set is closed. Unknown source record fields are invalid. Human navigation fields such as `tags` belong in `wiki_pages/` frontmatter, not in canonical record YAML.

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
