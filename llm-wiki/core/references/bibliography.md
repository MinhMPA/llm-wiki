# Bibliography

Bibliography records are optional maintenance artifacts for active paper sources with exact scholarly identifiers.

Canonical per-source files live under `wiki_records/bibtex/`:

```text
wiki_records/bibtex/SRC-0001.bib
wiki_records/bibtex/SRC-0001.yaml
```

The generated aggregate export lives at `wiki_records/bibtex/references.bib`. It is non-canonical and should be regenerated from source sidecars and per-source `.bib` files. When present, validation compares it to the deterministic active export.

## Sidecar Contract

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

Provider priority is `inspire`, then `ads`. ADS is optional and uses `ADS_API_TOKEN` when configured. ADS lookup searches for a bibcode, then exports BibTeX for that bibcode. Missing ADS credentials mean ADS was not attempted and should not appear in `providers_tried`.

Each active per-source `.bib` file must live at the canonical `wiki_records/bibtex/SRC-XXXX.bib` path and contain exactly one BibTeX entry.

## Bibliography Workflow

Use bibliography maintenance after ingest, under the lint boundary. Run commands on the wiki root. The fetcher reads source records under `wiki_records/sources/`; it does not scan `raw/` directly.

1. Run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT SRC-0001` to preview lookup.
2. Run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT SRC-0001 --apply` to write canonical BibTeX artifacts.
3. For bulk maintenance, run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT --missing` and then rerun with `--apply`.
4. Use `--retry-unresolved` to retry unresolved sidecars, or `--all` to revisit every eligible active paper source.
5. Run `python3 llm-wiki/core/scripts/export_bibtex.py WIKI_ROOT` to preview aggregate export changes.
6. Run `python3 llm-wiki/core/scripts/export_bibtex.py WIKI_ROOT --apply` to write `wiki_records/bibtex/references.bib`.
7. Optionally write to a LaTeX draft with `python3 llm-wiki/core/scripts/export_bibtex.py WIKI_ROOT --output /path/to/draft/references.bib --apply`.
8. Run `python3 llm-wiki/core/scripts/validate_wiki.py WIKI_ROOT`.

Eligible automatic fetch targets are active paper sources with an exact identifier from `arxiv_id`, `doi`, an arXiv `source_url`, or an arXiv-looking `raw_path`.
