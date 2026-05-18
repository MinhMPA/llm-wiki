# Changelog

All notable project changes are recorded here.

## Unreleased

- Added source-to-source relation records and managed `## Related sources` rendering for Obsidian graph workflows.
- Added canonical per-source BibTeX sidecars and `.bib` files under `wiki_records/bibtex/`.
- Added `fetch_bibtex.py` for INSPIRE-first BibTeX lookup with optional NASA/ADS fallback through `ADS_API_TOKEN`.
- Added `export_bibtex.py` to generate `wiki_records/bibtex/references.bib` or write a bibliography directly to a LaTeX draft with `--output`.
- Hardened bibliography validation for canonical paths, single-entry per-source `.bib` files, duplicate keys, non-active entries, and stale `references.bib` exports.
- Added source bibliography fields: `arxiv_id`, `doi`, and `bibtex_key`.
- Added MIT license.
- Added README credit for Andrej Karpathy's `llm-wiki.md` idea file.
