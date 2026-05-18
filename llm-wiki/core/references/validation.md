# Validation

Validation enforces concrete structure and consistency. It does not enforce broad guiding principles directly and does not semantically judge whether every durable claim has enough citations.

V1 validation checks:

- required root files and directories
- fixed `WIKI_SCHEMA.md` top-level heading order
- `WIKI_SCHEMA_PROPOSALS.md` queue sections and proposal blocks
- source record contracts
- closed source record fields
- optional source bibliography fields: `arxiv_id`, `doi`, and `bibtex_key`
- relation record contracts
- closed relation record fields
- BibTeX sidecar contracts under `wiki_records/bibtex/`
- closed BibTeX sidecar fields
- active BibTeX sidecars point to matching per-source `.bib` files
- generated `wiki_records/bibtex/references.bib` is treated as non-canonical export output
- managed `Related sources` consistency between relation records and source summary pages
- archived relation records are not rendered
- duplicate and superseded lifecycle fields have graph-visible mirror relations after source pages are processed
- required minimal page frontmatter
- mirrored record/page fields
- source record `page_path` targets when the target page exists
- Obsidian links inside `wiki_pages/`
- source-record footnote references
- symlink and path-type safety in the initializer test suite
