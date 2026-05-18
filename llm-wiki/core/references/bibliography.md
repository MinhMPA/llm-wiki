# Bibliography

Bibliography records are optional maintenance artifacts for active paper sources with exact scholarly identifiers.

Canonical per-source files live under `wiki_records/bibtex/`:

```text
wiki_records/bibtex/SRC-0001.bib
wiki_records/bibtex/SRC-0001.yaml
```

The generated aggregate export lives at `wiki_records/bibtex/references.bib`. It is non-canonical and should be regenerated from source sidecars and per-source `.bib` files.

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

Provider priority is `inspire`, then `ads`. ADS is optional and uses `ADS_API_TOKEN` when configured. Missing ADS credentials mean ADS was not attempted and should not appear in `providers_tried`.

## Bibliography Workflow

Use bibliography maintenance after ingest, under the lint boundary:

1. Run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT SRC-0001` to preview lookup.
2. Run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT SRC-0001 --apply` to write canonical BibTeX artifacts.
3. Run `python3 llm-wiki/core/scripts/export_bibtex.py WIKI_ROOT` to preview aggregate export changes.
4. Run `python3 llm-wiki/core/scripts/export_bibtex.py WIKI_ROOT --apply` to write `wiki_records/bibtex/references.bib`.
5. Run `python3 llm-wiki/core/scripts/validate_wiki.py WIKI_ROOT`.
