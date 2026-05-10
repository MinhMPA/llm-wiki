# Validation

Validation enforces concrete structure and consistency. It does not enforce broad guiding principles directly and does not semantically judge whether every durable claim has enough citations.

V1 validation checks:

- required root files and directories
- fixed `WIKI_SCHEMA.md` top-level heading order
- `WIKI_SCHEMA_PROPOSALS.md` queue sections and proposal blocks
- source record contracts
- closed source record fields
- required minimal page frontmatter
- mirrored record/page fields
- source record `page_path` targets when the target page exists
- Obsidian links inside `wiki_pages/`
- source-record footnote references
- symlink and path-type safety in the initializer test suite
