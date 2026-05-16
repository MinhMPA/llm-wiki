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

## Managed Related Sources

Source summary pages render active outgoing source relations in a managed section:

```markdown
## Related sources

### Cites
- [[sources/readable-source-title|Readable Source Title]] (`REL-0001`)
```

Rules:

- Omit `## Related sources` when the source has no active outgoing relations.
- Each managed bullet must correspond to exactly one active relation record.
- Archived relations must not render.
- Group headings use the fixed relation type labels in schema vocabulary order.
- Bullets within a group are ordered by target source title, then relation `record_id`.
- Link targets use the target source record `page_path` relative to `wiki_pages/`, without `.md`.
- Link labels use the target source record `title`.
- The managed section may contain only blank lines, relation type group headings, and managed bullets.
- Freeform related-source prose and ordinary Obsidian links belong outside the managed section.
