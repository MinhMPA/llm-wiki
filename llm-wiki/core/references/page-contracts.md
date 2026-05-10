# Page Contracts

## Required Layout

`wiki_pages/` must contain:

- `index.md`
- `log.md`
- `questions.md`
- `sources/`
- `entities/`
- `concepts/`
- `synthesis/`

## Page Types

Allowed `page_type` values:

- `source_summary`
- `entity`
- `concept`
- `synthesis`
- `index`
- `log`
- `questions`

## Mirrored Page Properties

Every markdown page under `wiki_pages/` must have minimal Obsidian-compatible frontmatter.

Allowed fields are:

- `record_id`
- `page_type`
- `title`
- `aliases`
- `tags`

`record_id` is used when a page mirrors a structured record. `title` is mirrored from the authoritative record when a backing record exists. `aliases` and `tags` are human navigation metadata and live only on pages.

Required fields on every wiki page are:

- `page_type`
- `title`
- `aliases`
- `tags`

`record_id` is required only when the page mirrors a structured record. `aliases` and `tags` must be lists.

## Source Record Citations

Durable claims cite source records with footnotes:

```markdown
The claim goes here.[^SRC-0001]

[^SRC-0001]: `SRC-0001` — [[sources/example-source]]
```

Footnote IDs must match existing source record IDs. `index.md`, `log.md`, and `questions.md` are exempt unless they make substantive claims.
