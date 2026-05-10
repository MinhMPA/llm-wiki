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

Wiki page frontmatter is minimal Obsidian-compatible metadata. Allowed fields are:

- `record_id`
- `page_type`
- `title`
- `aliases`
- `tags`

`record_id` is used when a page mirrors a structured record. `title` is mirrored from the authoritative record when a backing record exists. `aliases` and `tags` are human navigation metadata and live only on pages.

## Source Record Citations

Durable claims cite source records with footnotes:

```markdown
The claim goes here.[^SRC-0001]

[^SRC-0001]: `SRC-0001` — [[sources/example-source]]
```

Footnote IDs must match existing source record IDs. `index.md`, `log.md`, and `questions.md` are exempt unless they make substantive claims.
