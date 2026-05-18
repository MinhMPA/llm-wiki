# BibTeX Bibliography Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add first-class BibTeX retrieval, validation, and export for paper sources so LLM Wiki can maintain canonical per-source bibliography records and generate a LaTeX-ready aggregate `.bib`.

**Architecture:** Keep the structured/unstructured split intact. Source records remain authoritative for source identity, per-source `.bib` files plus sidecar `.yaml` files remain authoritative for bibliography state, and generated `references.bib` remains non-canonical. Use standard-library-only scripts, identifier-first provider lookup, dry-run-by-default mutation commands, and offline deterministic validation.

**Tech Stack:** Python standard library, Markdown, simple YAML subset parsed by `validate_wiki.py`, `urllib.request`, `unittest`, portable skill files.

---

## Interview Decisions

- Canonical bibliography storage is per-source under `wiki_records/bibtex/`:
  - `wiki_records/bibtex/SRC-0001.bib`
  - `wiki_records/bibtex/SRC-0001.yaml`
- A generated aggregate export lives at `wiki_records/bibtex/references.bib` and is non-canonical.
- BibTeX fetching is an explicit maintenance workflow, not a required ingest output.
- New optional source-record fields are `arxiv_id`, `doi`, and `bibtex_key`.
- Provider priority for v1 is fixed:
  - `inspire`
  - `ads`
- Google Scholar is excluded from v1.
- ADS is optional and credential-backed through `ADS_API_TOKEN`; token setup is not part of base install.
- `fetch_bibtex.py` and `export_bibtex.py` are dry-run by default and write only with `--apply`.
- Eligibility is limited to `source_type: paper` with an exact scholarly identifier.
- Title search and author search are excluded from lookup in v1.
- `authors` may be used for mismatch detection after identifier lookup, not as a search key.
- BibTeX normalization is minimal:
  - optional key rewrite from source-record `bibtex_key`
  - trim wrapper whitespace
  - ensure one trailing newline
- BibTeX sidecars are schema-closed and validator-enforced.
- Unresolved attempts write sidecars with `status: unresolved`.
- `providers_tried` is required, ordered, and may be empty.
- `provider: manual` is allowed with empty or non-empty `providers_tried`.
- Sidecars must reflect only providers actually attempted. Missing ADS token means `ads` is omitted from `providers_tried`.
- Active-only policy applies to fetch and export. Archived, duplicate, and superseded sources are out of scope for v1 bibliography mutation.
- `bibtex_key` stays out of page frontmatter.
- `references.bib` is ordered by `record_id`, contains active entries only, and has no timestamp/provenance banner.
- Scripts must have minimal-footprint behavior: no inference from orphan `.bib` files, no surprise repair, no source-record edits.
- Bibliography workflow belongs under `Lint Workflow`.
- Sidecar `record_type` is `bibtex`.
- The companion operational reference doc lives at `llm-wiki/core/references/bibliography.md`.
- Fetch is networked maintenance; export and validation remain offline.

## User Journeys

- As a researcher, I want to fetch a canonical BibTeX entry for one arXiv paper source, so that my wiki keeps a structured citation record beside the source record.
- As a researcher, I want to fetch missing BibTeX entries for many active paper sources, so that I can maintain a citation-ready wiki without editing each source by hand.
- As a researcher, I want a generated `references.bib`, so that a LaTeX draft can cite the current active wiki corpus without copy-paste.
- As a maintainer, I want invalid or stale bibliography artifacts to fail deterministic validation, so that agents cannot silently drift the bibliography layer away from the schema.
- As a maintainer, I want ADS credentials to be optional, so that the core wiki remains usable without external account setup.

## File Structure

**Create:**

- `llm-wiki/core/scripts/bibtex_support.py`
  - Shared bibliography helpers for source eligibility, arXiv normalization, minimal BibTeX parsing, sidecar conventions, and export ordering.
- `llm-wiki/core/scripts/fetch_bibtex.py`
  - Networked dry-run/apply fetch script for INSPIRE then ADS.
- `llm-wiki/core/scripts/export_bibtex.py`
  - Offline dry-run/apply export script for `references.bib`.
- `llm-wiki/core/references/bibliography.md`
  - Portable-core operational reference for bibliography commands, sidecar shape, provider order, and credential setup.
- `llm-wiki/core/assets/starter-wiki/wiki_records/bibtex/.gitkeep`
  - Starter directory for bibliography artifacts.
- `tests/test_bibtex_support.py`
  - Unit-style behavioral coverage for shared helpers.
- `tests/test_fetch_bibtex.py`
  - Script-facing tests for dry-run/apply fetch workflows.
- `tests/test_export_bibtex.py`
  - Script-facing tests for dry-run/apply export workflows.

**Modify:**

- `llm-wiki/core/assets/starter-wiki/WIKI_SCHEMA.md`
  - Add bibliography directory, source-record fields, sidecar contract, and `Bibliography workflow` under `Lint Workflow`.
- `llm-wiki/core/references/record-contracts.md`
  - Document new source-record fields and BibTeX sidecar contract.
- `llm-wiki/core/references/workflows.md`
  - Add `Bibliography Workflow` under `Lint Workflow` guidance.
- `llm-wiki/core/references/validation.md`
  - Document bibliography validation surface.
- `llm-wiki/core/scripts/init_llm_wiki.py`
  - Ensure starter `wiki_records/bibtex/` is created merge-safely.
- `llm-wiki/core/scripts/validate_wiki.py`
  - Add source-field support and BibTeX record validation.
- `tests/test_starter_wiki.py`
  - Assert starter schema and starter layout include bibliography pieces.
- `tests/test_init_llm_wiki.py`
  - Assert init creates `wiki_records/bibtex/`.
- `tests/test_validate_wiki.py`
  - Add bibliography validation coverage.
- `tests/test_end_to_end.py`
  - Cover starter init -> local bibtex records -> export -> validate.
- `README.md`
  - Add user-facing bibliography workflow.
- `docs/llm-wiki-implementation.md`
  - Explain the actual implementation boundaries.
- `docs/llm-wiki-extension.md`
  - Explain how future provider/schema changes must propagate.
- `docs/llm-wiki-application.md`
  - Document practical researcher workflows and ADS optional setup.
- `CONTEXT.md`
  - Keep glossary updates that define the bibliography terms used by the implementation.

**Do not modify:**

- `llm-wiki/core/assets/starter-wiki/WIKI_SCHEMA_PROPOSALS.md`
  - Keep it generic; do not pre-seed a bibliography proposal block into the starter template.

## Implementation Constraints

- Follow vertical TDD slices only. Do not write all tests up front.
- Use `unittest` and existing subprocess-driven script tests.
- Keep all new logic standard-library-only.
- Do not add automated Google Scholar handling.
- Do not mutate source records during fetch.
- Do not infer manual sidecars from orphan `.bib` files.
- Do not add page-frontmatter bibliography fields.
- Do not require ADS setup at install time.

## Task 1: Starter Schema And Documentation Surface

**Files:**

- Create: `llm-wiki/core/assets/starter-wiki/wiki_records/bibtex/.gitkeep`
- Modify: `llm-wiki/core/assets/starter-wiki/WIKI_SCHEMA.md`
- Modify: `llm-wiki/core/references/record-contracts.md`
- Modify: `llm-wiki/core/references/workflows.md`
- Modify: `llm-wiki/core/references/validation.md`
- Create: `llm-wiki/core/references/bibliography.md`
- Modify: `tests/test_starter_wiki.py`
- Modify: `tests/test_init_llm_wiki.py`

- [ ] **Step 1: Write the failing starter tests**

```python
def test_required_paths_exist(self):
    required = [
        "wiki_records/bibtex/.gitkeep",
    ]
    for path in required:
        self.assertTrue((STARTER / path).exists(), path)


def test_schema_defines_bibliography_contract(self):
    schema = (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8")
    source_yaml = fenced_yaml_after(schema, "A v1 source record uses this YAML contract:")
    self.assertEqual(
        yaml_keys(source_yaml),
        [
            "record_id",
            "record_type",
            "status",
            "duplicate_of",
            "superseded_by",
            "source_storage",
            "raw_path",
            "source_url",
            "page_path",
            "source_type",
            "source_format",
            "title",
            "authors",
            "added_date",
            "processed_date",
            "published_date",
            "content_fingerprint",
            "arxiv_id",
            "doi",
            "bibtex_key",
        ],
    )
    self.assertIn("wiki_records/bibtex/", schema)
    self.assertIn("Bibliography workflow", schema)
    self.assertIn("record_type: bibtex", schema)
```

- [ ] **Step 2: Run the starter tests to verify RED**

Run:

```bash
python3 -m unittest tests.test_starter_wiki tests.test_init_llm_wiki -v
```

Expected:

- `FAIL` because `wiki_records/bibtex/.gitkeep` does not exist yet.
- `FAIL` because the source-record contract and schema text do not mention bibliography yet.

- [ ] **Step 3: Commit the RED checkpoint**

```bash
git add tests/test_starter_wiki.py tests/test_init_llm_wiki.py
git commit -m "test: add bibliography starter contract checks"
```

- [ ] **Step 4: Add the minimal starter/schema implementation**

Add the starter directory and extend the starter schema with these exact contract surfaces:

```yaml
record_id: SRC-0001
record_type: source
status: active
duplicate_of:
superseded_by:
source_storage: local
raw_path: raw/articles/example.md
source_url:
page_path: wiki_pages/sources/example.md
source_type: paper
source_format: pdf
title: Example Paper
authors: []
added_date: 2026-05-18
processed_date:
published_date:
content_fingerprint:
arxiv_id: 1808.02002
doi:
bibtex_key:
```

Add the sidecar contract to both the schema and `record-contracts.md`:

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

Add the workflow section text to `workflows.md` and `bibliography.md`:

```markdown
## Bibliography Workflow

Use bibliography maintenance after ingest, under the lint boundary:

1. Run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT SRC-0001` to preview lookup.
2. Run `python3 llm-wiki/core/scripts/fetch_bibtex.py WIKI_ROOT SRC-0001 --apply` to write canonical BibTeX artifacts.
3. Run `python3 llm-wiki/core/scripts/export_bibtex.py WIKI_ROOT` to preview aggregate export changes.
4. Run `python3 llm-wiki/core/scripts/export_bibtex.py WIKI_ROOT --apply` to write `wiki_records/bibtex/references.bib`.
5. Run `python3 llm-wiki/core/scripts/validate_wiki.py WIKI_ROOT`.
```

- [ ] **Step 5: Re-run the starter tests to verify GREEN**

Run:

```bash
python3 -m unittest tests.test_starter_wiki tests.test_init_llm_wiki -v
```

Expected:

- All selected tests `PASS`.

- [ ] **Step 6: Commit the GREEN checkpoint**

```bash
git add llm-wiki/core/assets/starter-wiki/WIKI_SCHEMA.md llm-wiki/core/assets/starter-wiki/wiki_records/bibtex/.gitkeep llm-wiki/core/references/record-contracts.md llm-wiki/core/references/workflows.md llm-wiki/core/references/validation.md llm-wiki/core/references/bibliography.md tests/test_starter_wiki.py tests/test_init_llm_wiki.py
git commit -m "fix: add bibliography starter schema and references"
```

## Task 2: Shared BibTeX Helper Module

**Files:**

- Create: `llm-wiki/core/scripts/bibtex_support.py`
- Create: `tests/test_bibtex_support.py`

- [ ] **Step 1: Write one failing helper test for arXiv normalization**

```python
from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "llm-wiki" / "core" / "scripts" / "bibtex_support.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bibtex_support", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestBibtexSupport(unittest.TestCase):
    def test_normalize_arxiv_id_strips_version_suffix(self):
        module = load_module()
        self.assertEqual(module.normalize_arxiv_id("1808.02002v2"), "1808.02002")
```

- [ ] **Step 2: Run the helper test to verify RED**

Run:

```bash
python3 -m unittest tests.test_bibtex_support.TestBibtexSupport.test_normalize_arxiv_id_strips_version_suffix -v
```

Expected:

- `ERROR` or `FAIL` because `bibtex_support.py` does not exist yet.

- [ ] **Step 3: Commit the RED checkpoint**

```bash
git add tests/test_bibtex_support.py
git commit -m "test: add bibtex helper behavior coverage"
```

- [ ] **Step 4: Implement the minimal helper module**

Start the module with these public helpers:

```python
ARXIV_ID_RE = re.compile(r"^(?P<base>\d{4}\.\d{4,5})(?:v\d+)?$")
PROVIDER_ORDER = ["inspire", "ads"]


def normalize_arxiv_id(value: str) -> str:
    match = ARXIV_ID_RE.match(value.strip())
    if not match:
        return value.strip()
    return match.group("base")


def extract_bibtex_key(entry_text: str) -> str:
    match = re.search(r"@\w+\{([^,]+),", entry_text)
    if match is None:
        raise ValueError("BibTeX entry key not found")
    return match.group(1).strip()


def source_identifier_candidates(data: dict[str, object]) -> list[str]:
    candidates = []
    arxiv_id = str(data.get("arxiv_id") or "").strip()
    if arxiv_id:
        candidates.append(f"arxiv:{normalize_arxiv_id(arxiv_id)}")
    doi = str(data.get("doi") or "").strip()
    if doi:
        candidates.append(f"doi:{doi}")
    source_url = str(data.get("source_url") or "").strip()
    if "arxiv.org/" in source_url:
        tail = source_url.rstrip("/").split("/")[-1]
        if tail:
            candidates.append(f"arxiv:{normalize_arxiv_id(tail)}")
    raw_path = str(data.get("raw_path") or "").strip()
    raw_name = Path(raw_path).name
    raw_stem = Path(raw_name).stem
    if ARXIV_ID_RE.match(raw_stem):
        candidates.append(f"arxiv:{normalize_arxiv_id(raw_stem)}")
    return list(dict.fromkeys(candidates))
```

- [ ] **Step 5: Add the next failing tests one at a time**

Add these behaviors incrementally, rerunning RED before each implementation change:

```python
    def test_source_identifier_candidates_prioritize_explicit_arxiv_then_doi(self):
        module = load_module()
        candidates = module.source_identifier_candidates(
            {
                "arxiv_id": "1808.02002v3",
                "doi": "10.1234/example",
                "source_url": "https://arxiv.org/abs/1808.02002v2",
            }
        )
        self.assertEqual(candidates, ["arxiv:1808.02002", "doi:10.1234/example"])

    def test_extract_bibtex_key_reads_single_entry_key(self):
        module = load_module()
        key = module.extract_bibtex_key("@article{Schmidt:2018,\n  title={Example}\n}\n")
        self.assertEqual(key, "Schmidt:2018")

    def test_is_eligible_source_requires_active_paper_with_identifier(self):
        module = load_module()
        self.assertTrue(
            module.is_eligible_bibtex_source(
                {"status": "active", "source_type": "paper", "arxiv_id": "1808.02002"}
            )
        )
        self.assertFalse(
            module.is_eligible_bibtex_source(
                {"status": "archived", "source_type": "paper", "arxiv_id": "1808.02002"}
            )
        )
```

- [ ] **Step 6: Re-run the helper test file to verify GREEN**

Run:

```bash
python3 -m unittest tests.test_bibtex_support -v
```

Expected:

- All selected tests `PASS`.

- [ ] **Step 7: Commit the GREEN checkpoint**

```bash
git add llm-wiki/core/scripts/bibtex_support.py tests/test_bibtex_support.py
git commit -m "fix: add shared bibtex support helpers"
```

## Task 3: Validator Support For Source Fields And BibTeX Records

**Files:**

- Modify: `llm-wiki/core/scripts/validate_wiki.py`
- Modify: `tests/test_validate_wiki.py`
- Modify: `llm-wiki/core/references/validation.md`

- [ ] **Step 1: Write the first failing validator test for new source fields**

```python
    def test_source_record_accepts_bibliography_identifier_fields(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://arxiv.org/abs/1808.02002v2
                source_type: paper
                title: Example Paper
                authors: []
                added_date: 2026-05-18
                arxiv_id: 1808.02002v2
                doi: 10.1234/example
                bibtex_key: Example:2018
                """,
            )
            result = run_validator(wiki)
            self.assertEqual(result.returncode, 0, result.stderr)
```

- [ ] **Step 2: Run the validator test to verify RED**

Run:

```bash
python3 -m unittest tests.test_validate_wiki.TestValidateWiki.test_source_record_accepts_bibliography_identifier_fields -v
```

Expected:

- `FAIL` because `arxiv_id`, `doi`, and `bibtex_key` are not yet accepted source fields.

- [ ] **Step 3: Commit the first RED checkpoint**

```bash
git add tests/test_validate_wiki.py
git commit -m "test: add bibliography source field validator coverage"
```

- [ ] **Step 4: Implement the minimal source-field validator change**

Extend `validate_wiki.py` constants with:

```python
ALLOWED_SOURCE_FIELDS = {
    "record_id",
    "record_type",
    "status",
    "duplicate_of",
    "superseded_by",
    "source_storage",
    "raw_path",
    "source_url",
    "page_path",
    "source_type",
    "source_format",
    "title",
    "authors",
    "added_date",
    "processed_date",
    "published_date",
    "content_fingerprint",
    "arxiv_id",
    "doi",
    "bibtex_key",
}
```

Keep them optional and do not require them for non-paper sources.

- [ ] **Step 5: Add one failing test for sidecar validation**

```python
    def test_active_bibtex_sidecar_requires_matching_bib_file(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://arxiv.org/abs/1808.02002
                source_type: paper
                title: Example Paper
                authors: []
                added_date: 2026-05-18
                arxiv_id: 1808.02002
                """,
            )
            sidecar = wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml"
            sidecar.write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: bibtex",
                        "status: active",
                        "provider: inspire",
                        "provider_priority: 1",
                        "providers_tried:",
                        "  - inspire",
                        "lookup_id: arxiv:1808.02002",
                        "bibtex_key: Example:2018",
                        "fetched_date: 2026-05-18",
                        "source_bib_path: wiki_records/bibtex/SRC-0001.bib",
                    ]
                ),
                encoding="utf-8",
            )
            result = run_validator(wiki)
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing BibTeX file", result.stderr)
```

- [ ] **Step 6: Run the sidecar test to verify RED**

Run:

```bash
python3 -m unittest tests.test_validate_wiki.TestValidateWiki.test_active_bibtex_sidecar_requires_matching_bib_file -v
```

Expected:

- `FAIL` because BibTeX sidecars are not validated yet.

- [ ] **Step 7: Commit the second RED checkpoint**

```bash
git add tests/test_validate_wiki.py
git commit -m "test: add bibliography sidecar validator coverage"
```

- [ ] **Step 8: Implement the BibTeX sidecar validator**

Add to `validate_wiki.py`:

```python
REQUIRED_BIBTEX_FIELDS = [
    "record_id",
    "record_type",
    "status",
    "provider",
    "provider_priority",
    "providers_tried",
    "lookup_id",
    "bibtex_key",
    "fetched_date",
    "source_bib_path",
]

BIBTEX_STATUSES = {"active", "unresolved"}
BIBTEX_PROVIDERS = {"inspire", "ads", "manual"}
```

Add loading and validation routines:

```python
def load_bibtex_sidecars(root: Path, errors: list[str]) -> dict[str, dict[str, Any]]:
    sidecars: dict[str, dict[str, Any]] = {}
    bibtex_dir = root / "wiki_records" / "bibtex"
    if not bibtex_dir.is_dir():
        return sidecars
    for path in sorted(bibtex_dir.glob("*.yaml"), key=lambda item: item.name):
        location = relative_path(root, path)
        text = read_text(path, errors, location)
        data, parse_errors = parse_simple_yaml(text, location)
        errors.extend(parse_errors)
        record_id = scalar_value(data, "record_id")
        if record_id:
            sidecars[record_id] = data
    return sidecars


def validate_bibtex_sidecars(root: Path, sidecars: dict[str, dict[str, Any]], source_records: dict[str, SourceRecord], errors: list[str]) -> None:
    for record_id, data in sorted(sidecars.items()):
        location = f"wiki_records/bibtex/{record_id}.yaml"
        validate_bibtex_sidecar(root, location, data, source_records, errors)
```

Enforce these rules:

- `record_id` must match the source filename stem `SRC-0001`.
- `record_type` must be `bibtex`.
- `status` must be `active` or `unresolved`.
- `providers_tried` must be a list, contain only `inspire` and `ads`, and preserve provider-order prefix semantics.
- `provider_priority` is `1` for `inspire`, `2` for `ads`, blank for `manual` and unresolved.
- `provider` is blank only for unresolved.
- `lookup_id` and `source_bib_path` are blank-allowed only when the contract says so.
- `active` sidecars require a matching `.bib` file and extractable BibTeX key.
- `unresolved` sidecars must not require a `.bib` file.
- orphan `.bib` files without sidecars fail validation only if the validator explicitly sees them under `wiki_records/bibtex/`.

- [ ] **Step 9: Add the remaining failing tests one at a time**

Add these behaviors incrementally:

```python
    def test_unresolved_bibtex_sidecar_without_bib_file_passes(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://arxiv.org/abs/1808.02002
                source_type: paper
                title: Example Paper
                authors: []
                added_date: 2026-05-18
                arxiv_id: 1808.02002
                """,
            )
            (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: bibtex",
                        "status: unresolved",
                        "provider:",
                        "provider_priority:",
                        "providers_tried:",
                        "  - inspire",
                        "lookup_id: arxiv:1808.02002",
                        "bibtex_key:",
                        "fetched_date: 2026-05-18",
                        "source_bib_path:",
                    ]
                ),
                encoding="utf-8",
            )
            result = run_validator(wiki)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_manual_bibtex_sidecar_allows_nonempty_providers_tried(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://arxiv.org/abs/1808.02002
                source_type: paper
                title: Example Paper
                authors: []
                added_date: 2026-05-18
                arxiv_id: 1808.02002
                """,
            )
            (wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").write_text(
                "@article{Example:2018,\n  title={Example}\n}\n",
                encoding="utf-8",
            )
            (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: bibtex",
                        "status: active",
                        "provider: manual",
                        "provider_priority:",
                        "providers_tried:",
                        "  - inspire",
                        "  - ads",
                        "lookup_id:",
                        "bibtex_key: Example:2018",
                        "fetched_date: 2026-05-18",
                        "source_bib_path: wiki_records/bibtex/SRC-0001.bib",
                    ]
                ),
                encoding="utf-8",
            )
            result = run_validator(wiki)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_bibtex_sidecar_rejects_provider_order_violation(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://arxiv.org/abs/1808.02002
                source_type: paper
                title: Example Paper
                authors: []
                added_date: 2026-05-18
                arxiv_id: 1808.02002
                """,
            )
            (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: bibtex",
                        "status: unresolved",
                        "provider:",
                        "provider_priority:",
                        "providers_tried:",
                        "  - ads",
                        "  - inspire",
                        "lookup_id: arxiv:1808.02002",
                        "bibtex_key:",
                        "fetched_date: 2026-05-18",
                        "source_bib_path:",
                    ]
                ),
                encoding="utf-8",
            )
            result = run_validator(wiki)
            self.assertEqual(result.returncode, 1)
            self.assertIn("providers_tried must follow provider order", result.stderr)

    def test_bibtex_sidecar_rejects_key_mismatch_with_entry(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            write_source_record(
                wiki,
                "SRC-0001.yaml",
                """
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://arxiv.org/abs/1808.02002
                source_type: paper
                title: Example Paper
                authors: []
                added_date: 2026-05-18
                arxiv_id: 1808.02002
                """,
            )
            (wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").write_text(
                "@article{Actual:2018,\n  title={Example}\n}\n",
                encoding="utf-8",
            )
            (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: bibtex",
                        "status: active",
                        "provider: inspire",
                        "provider_priority: 1",
                        "providers_tried:",
                        "  - inspire",
                        "lookup_id: arxiv:1808.02002",
                        "bibtex_key: Expected:2018",
                        "fetched_date: 2026-05-18",
                        "source_bib_path: wiki_records/bibtex/SRC-0001.bib",
                    ]
                ),
                encoding="utf-8",
            )
            result = run_validator(wiki)
            self.assertEqual(result.returncode, 1)
            self.assertIn("bibtex_key does not match BibTeX entry key", result.stderr)

    def test_bibtex_sidecar_rejects_unknown_source_record(self):
        temp_dir, wiki = initialized_wiki()
        with temp_dir:
            (wiki / "wiki_records" / "bibtex" / "SRC-9999.yaml").write_text(
                "\n".join(
                    [
                        "record_id: SRC-9999",
                        "record_type: bibtex",
                        "status: unresolved",
                        "provider:",
                        "provider_priority:",
                        "providers_tried:",
                        "  - inspire",
                        "lookup_id: arxiv:1808.02002",
                        "bibtex_key:",
                        "fetched_date: 2026-05-18",
                        "source_bib_path:",
                    ]
                ),
                encoding="utf-8",
            )
            result = run_validator(wiki)
            self.assertEqual(result.returncode, 1)
            self.assertIn("record_id points to unknown source record", result.stderr)
```

- [ ] **Step 10: Re-run the validator suite slice to verify GREEN**

Run:

```bash
python3 -m unittest tests.test_validate_wiki -v
```

Expected:

- All validator tests `PASS`.

- [ ] **Step 11: Commit the GREEN checkpoint**

```bash
git add llm-wiki/core/scripts/validate_wiki.py llm-wiki/core/references/validation.md tests/test_validate_wiki.py
git commit -m "fix: validate bibliography records and source fields"
```

## Task 4: Fetch Script For INSPIRE Then ADS

**Files:**

- Create: `llm-wiki/core/scripts/fetch_bibtex.py`
- Create: `tests/test_fetch_bibtex.py`
- Modify: `llm-wiki/core/references/bibliography.md`
- Modify: `README.md`

- [ ] **Step 1: Write the first failing fetch-script test**

```python
import contextlib
import io
import os
import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
FETCH_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "fetch_bibtex.py"
INIT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "init_llm_wiki.py"


def load_fetch_module():
    spec = importlib.util.spec_from_file_location("fetch_bibtex", FETCH_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PreparedWiki:
    def __init__(self, bibtex_key=""):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "wiki"
        subprocess.run([sys.executable, str(INIT_SCRIPT), str(self.path)], check=True, capture_output=True, text=True)
        record = self.path / "wiki_records" / "sources" / "SRC-0001.yaml"
        record.write_text(
            textwrap.dedent(
                f"""
                record_id: SRC-0001
                record_type: source
                status: active
                source_storage: external
                source_url: https://arxiv.org/abs/1808.02002v2
                source_type: paper
                title: Example Paper
                authors: []
                added_date: 2026-05-18
                arxiv_id: 1808.02002v2
                doi:
                bibtex_key: {bibtex_key}
                """
            ).strip() + "\n",
            encoding="utf-8",
        )

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type, exc, tb):
        self.temp_dir.cleanup()


def prepared_wiki_with_active_arxiv_source(bibtex_key=""):
    return PreparedWiki(bibtex_key=bibtex_key)


def prepared_wiki_with_unresolved_sidecar():
    wiki_context = PreparedWiki()
    wiki = wiki_context.path
    sidecar = wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml"
    sidecar.write_text(
        "\n".join(
            [
                "record_id: SRC-0001",
                "record_type: bibtex",
                "status: unresolved",
                "provider:",
                "provider_priority:",
                "providers_tried:",
                "  - inspire",
                "lookup_id: arxiv:1808.02002",
                "bibtex_key:",
                "fetched_date: 2026-05-18",
                "source_bib_path:",
            ]
        ),
        encoding="utf-8",
    )
    return wiki_context


def call_main(module, args):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        returncode = module.main(list(args))
    return types.SimpleNamespace(returncode=returncode, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def run_fetch_with_fake_provider(wiki, *args):
    module = load_fetch_module()
    bibtex_entry = next(arg for arg in args if isinstance(arg, str) and arg.startswith("@"))
    cli_args = [str(wiki), *[arg for arg in args if not (isinstance(arg, str) and arg.startswith("@"))]]
    with mock.patch.object(module, "fetch_from_inspire", return_value=bibtex_entry):
        return call_main(module, cli_args)


def run_fetch_with_provider_sequence(wiki, record_id, provider_results, *args, env=None):
    module = load_fetch_module()
    cli_args = [str(wiki), record_id, *args]
    with mock.patch.dict(os.environ, env or {}, clear=False):
        with mock.patch.object(module, "fetch_from_inspire", return_value=provider_results[0]):
            ads_result = provider_results[1] if len(provider_results) > 1 else None
            with mock.patch.object(module, "fetch_from_ads", return_value=ads_result):
                return call_main(module, cli_args)


def run_fetch(wiki, *args):
    module = load_fetch_module()
    return call_main(module, [str(wiki), *args])


class TestFetchBibtex(unittest.TestCase):
    def test_single_source_dry_run_reports_inspire_match(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            result = run_fetch_with_fake_provider(wiki, "SRC-0001", "@article{Example:2018,\n  title={Example}\n}\n")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("would write", result.stdout)
            self.assertFalse((wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").exists())
```

- [ ] **Step 2: Run the fetch-script test to verify RED**

Run:

```bash
python3 -m unittest tests.test_fetch_bibtex.TestFetchBibtex.test_single_source_dry_run_reports_inspire_match -v
```

Expected:

- `ERROR` or `FAIL` because `fetch_bibtex.py` does not exist yet.

- [ ] **Step 3: Commit the RED checkpoint**

```bash
git add tests/test_fetch_bibtex.py
git commit -m "test: add fetch bibtex workflow coverage"
```

- [ ] **Step 4: Implement the minimal fetch script**

Build the CLI shape first:

```python
parser = argparse.ArgumentParser(description="Fetch canonical BibTeX entries for LLM Wiki paper sources.")
parser.add_argument("wiki_root", type=Path)
parser.add_argument("record_id", nargs="?")
parser.add_argument("--all", action="store_true")
parser.add_argument("--missing", action="store_true")
parser.add_argument("--retry-unresolved", action="store_true")
parser.add_argument("--apply", action="store_true")
```

Use these provider routines:

```python
def fetch_from_inspire(lookup_id: str) -> str | None:
    url = inspire_bibtex_url(lookup_id)
    with urllib.request.urlopen(url, timeout=30) as response:
        text = response.read().decode("utf-8")
    return normalize_bibtex_entry(text) if text.strip() else None


def fetch_from_ads(lookup_id: str, token: str) -> str | None:
    request = urllib.request.Request(ads_bibtex_url(lookup_id), headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        text = response.read().decode("utf-8")
    return normalize_bibtex_entry(text) if text.strip() else None
```

Use these behavioral rules:

- select only active eligible paper sources;
- try exact identifier candidates in priority order;
- try INSPIRE first;
- try ADS only when `ADS_API_TOKEN` is present;
- keep `providers_tried` to actual attempts only;
- on dry-run, report what would be written;
- on `--apply`, write sidecar and `.bib`;
- do not overwrite orphan manual `.bib` files without sidecars.

- [ ] **Step 5: Add one failing test at a time for the remaining fetch behaviors**

Add these tests incrementally:

```python
    def test_apply_writes_bib_and_sidecar_for_inspire_result(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            result = run_fetch_with_fake_provider(wiki, "SRC-0001", "@article{Example:2018,\n  title={Example}\n}\n", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").exists())
            sidecar = (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").read_text(encoding="utf-8")
            self.assertIn("provider: inspire", sidecar)
            self.assertIn("providers_tried:\n  - inspire", sidecar)

    def test_fetch_uses_ads_when_inspire_misses_and_token_exists(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            env = os.environ.copy()
            env["ADS_API_TOKEN"] = "token"
            result = run_fetch_with_provider_sequence(wiki, "SRC-0001", [None, "@article{AdsKey,\n  title={Example}\n}\n"], "--apply", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            sidecar = (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").read_text(encoding="utf-8")
            self.assertIn("provider: ads", sidecar)
            self.assertIn("  - inspire\n  - ads", sidecar)

    def test_missing_ads_token_skips_ads_and_reports_unresolved(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            env = os.environ.copy()
            env.pop("ADS_API_TOKEN", None)
            result = run_fetch_with_provider_sequence(wiki, "SRC-0001", [None], "--apply", env=env)
            self.assertEqual(result.returncode, 1)
            sidecar = (wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").read_text(encoding="utf-8")
            self.assertIn("status: unresolved", sidecar)
            self.assertIn("providers_tried:\n  - inspire", sidecar)
            self.assertNotIn("  - ads", sidecar)

    def test_missing_mode_skips_existing_sidecars_without_retry(self):
        with prepared_wiki_with_unresolved_sidecar() as wiki:
            result = run_fetch(wiki, "--missing")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("skipped unresolved", result.stdout)

    def test_retry_unresolved_retries_unresolved_sidecar(self):
        with prepared_wiki_with_unresolved_sidecar() as wiki:
            result = run_fetch_with_fake_provider(wiki, "--missing", "--retry-unresolved", "@article{Retry:2018,\n  title={Example}\n}\n", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Retry:2018", (wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").read_text(encoding="utf-8"))

    def test_manual_orphan_bib_file_is_reported_but_not_inferred(self):
        with prepared_wiki_with_active_arxiv_source() as wiki:
            (wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").write_text("@article{Manual:2018,\n  title={Manual}\n}\n", encoding="utf-8")
            result = run_fetch(wiki, "SRC-0001", "--apply")
            self.assertEqual(result.returncode, 1)
            self.assertIn("orphan BibTeX file", result.stderr)
            self.assertFalse((wiki / "wiki_records" / "bibtex" / "SRC-0001.yaml").exists())

    def test_bibtex_key_override_rewrites_entry_key(self):
        with prepared_wiki_with_active_arxiv_source(bibtex_key="PreferredKey") as wiki:
            result = run_fetch_with_fake_provider(wiki, "SRC-0001", "@article{ProviderKey,\n  title={Example}\n}\n", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("@article{PreferredKey,", (wiki / "wiki_records" / "bibtex" / "SRC-0001.bib").read_text(encoding="utf-8"))
```

- [ ] **Step 6: Re-run the fetch test file to verify GREEN**

Run:

```bash
python3 -m unittest tests.test_fetch_bibtex -v
```

Expected:

- All fetch tests `PASS`.

- [ ] **Step 7: Commit the GREEN checkpoint**

```bash
git add llm-wiki/core/scripts/fetch_bibtex.py llm-wiki/core/references/bibliography.md README.md tests/test_fetch_bibtex.py
git commit -m "fix: add fetch bibtex workflow"
```

## Task 5: Export Script And Aggregate Workflow

**Files:**

- Create: `llm-wiki/core/scripts/export_bibtex.py`
- Create: `tests/test_export_bibtex.py`
- Modify: `tests/test_end_to_end.py`
- Modify: `docs/llm-wiki-application.md`

- [ ] **Step 1: Write the first failing export test**

```python
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "init_llm_wiki.py"
EXPORT_SCRIPT = ROOT / "llm-wiki" / "core" / "scripts" / "export_bibtex.py"


def active_source(record_id, title, status="active"):
    return "\n".join(
        [
            f"record_id: {record_id}",
            "record_type: source",
            f"status: {status}",
            "duplicate_of:",
            "superseded_by:",
            "source_storage: external",
            f"source_url: https://arxiv.org/abs/{record_id.lower()}",
            "page_path:",
            "source_type: paper",
            "source_format: pdf",
            f"title: {title}",
            "authors: []",
            "added_date: 2026-05-18",
            "processed_date:",
            "published_date:",
            "content_fingerprint:",
            "arxiv_id: 1808.02002",
            "doi:",
            "bibtex_key:",
            "",
        ]
    )


def active_sidecar(record_id, bibtex_key):
    return "\n".join(
        [
            f"record_id: {record_id}",
            "record_type: bibtex",
            "status: active",
            "provider: manual",
            "provider_priority:",
            "providers_tried:",
            "lookup_id:",
            f"bibtex_key: {bibtex_key}",
            "fetched_date: 2026-05-18",
            f"source_bib_path: wiki_records/bibtex/{record_id}.bib",
            "",
        ]
    )


def unresolved_sidecar(record_id):
    return "\n".join(
        [
            f"record_id: {record_id}",
            "record_type: bibtex",
            "status: unresolved",
            "provider:",
            "provider_priority:",
            "providers_tried:",
            "  - inspire",
            "lookup_id: arxiv:1808.02002",
            "bibtex_key:",
            "fetched_date: 2026-05-18",
            "source_bib_path:",
            "",
        ]
    )


class PreparedExportWiki:
    def __init__(self, status_1="active", status_2="active", key_1="AKey", key_2="BKey", unresolved=False):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "wiki"
        subprocess.run([sys.executable, str(INIT_SCRIPT), str(self.path)], check=True, capture_output=True, text=True)
        sources = self.path / "wiki_records" / "sources"
        bibtex = self.path / "wiki_records" / "bibtex"
        sources.joinpath("SRC-0001.yaml").write_text(active_source("SRC-0001", "A", status=status_1), encoding="utf-8")
        sources.joinpath("SRC-0002.yaml").write_text(active_source("SRC-0002", "B", status=status_2), encoding="utf-8")
        if unresolved:
            bibtex.joinpath("SRC-0001.yaml").write_text(unresolved_sidecar("SRC-0001"), encoding="utf-8")
        else:
            bibtex.joinpath("SRC-0001.bib").write_text(f"@article{{{key_1},\n  title={{A}}\n}}\n", encoding="utf-8")
            bibtex.joinpath("SRC-0001.yaml").write_text(active_sidecar("SRC-0001", key_1), encoding="utf-8")
            bibtex.joinpath("SRC-0002.bib").write_text(f"@article{{{key_2},\n  title={{B}}\n}}\n", encoding="utf-8")
            bibtex.joinpath("SRC-0002.yaml").write_text(active_sidecar("SRC-0002", key_2), encoding="utf-8")

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type, exc, tb):
        self.temp_dir.cleanup()


def prepared_wiki_with_two_active_bibtex_entries(key_1="AKey", key_2="BKey"):
    return PreparedExportWiki(key_1=key_1, key_2=key_2)


def prepared_wiki_with_unresolved_bibtex_sidecar():
    return PreparedExportWiki(unresolved=True)


def prepared_wiki_with_bibtex_for_archived_source():
    return PreparedExportWiki(status_1="archived", status_2="archived", key_1="AKey", key_2="BKey")


def run_export(wiki, *args):
    return subprocess.run([sys.executable, str(EXPORT_SCRIPT), str(wiki), *args], capture_output=True, text=True, check=False)


class TestExportBibtex(unittest.TestCase):
    def test_dry_run_reports_references_export_ordered_by_record_id(self):
        with prepared_wiki_with_two_active_bibtex_entries() as wiki:
            result = run_export(wiki)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("would write", result.stdout)
            self.assertIn("2 entries", result.stdout)
```

- [ ] **Step 2: Run the export test to verify RED**

Run:

```bash
python3 -m unittest tests.test_export_bibtex.TestExportBibtex.test_dry_run_reports_references_export_ordered_by_record_id -v
```

Expected:

- `ERROR` or `FAIL` because `export_bibtex.py` does not exist yet.

- [ ] **Step 3: Commit the RED checkpoint**

```bash
git add tests/test_export_bibtex.py tests/test_end_to_end.py
git commit -m "test: add bibliography export coverage"
```

- [ ] **Step 4: Implement the minimal export script**

Use this CLI shape:

```python
parser = argparse.ArgumentParser(description="Export aggregate BibTeX for an LLM Wiki.")
parser.add_argument("wiki_root", type=Path)
parser.add_argument("--output", type=Path)
parser.add_argument("--apply", action="store_true")
```

Implement these rules:

- load active source records only;
- load active BibTeX sidecars only;
- require matching `.bib` files;
- sort exported entries by `record_id`;
- reject duplicate `bibtex_key` values;
- default output path is `wiki_records/bibtex/references.bib`;
- `--output` may point outside the wiki only when explicitly provided;
- dry-run reports the target and entry count;
- `--apply` writes content-only output, no header comment.

- [ ] **Step 5: Add the remaining export tests one at a time**

Add these tests incrementally:

```python
    def test_apply_writes_references_bib(self):
        with prepared_wiki_with_two_active_bibtex_entries() as wiki:
            result = run_export(wiki, "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            references = (wiki / "wiki_records" / "bibtex" / "references.bib").read_text(encoding="utf-8")
            self.assertLess(references.index("@article{AKey,"), references.index("@article{BKey,"))

    def test_export_rejects_duplicate_keys(self):
        with prepared_wiki_with_two_active_bibtex_entries(key_1="SameKey", key_2="SameKey") as wiki:
            result = run_export(wiki)
            self.assertEqual(result.returncode, 1)
            self.assertIn("duplicate BibTeX key", result.stderr)

    def test_export_skips_unresolved_sidecars(self):
        with prepared_wiki_with_unresolved_bibtex_sidecar() as wiki:
            result = run_export(wiki)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("0 entries", result.stdout)

    def test_export_skips_nonactive_sources(self):
        with prepared_wiki_with_bibtex_for_archived_source() as wiki:
            result = run_export(wiki)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("0 entries", result.stdout)

    def test_external_output_path_writes_only_requested_file(self):
        with prepared_wiki_with_two_active_bibtex_entries() as wiki:
            external = wiki.parent / "draft" / "references.bib"
            external.parent.mkdir()
            result = run_export(wiki, "--output", str(external), "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(external.exists())
            self.assertFalse((wiki / "wiki_records" / "bibtex" / "references.bib").exists())
```

- [ ] **Step 6: Add one end-to-end test for bibliography**

Add to `tests/test_end_to_end.py`:

```python
    def test_init_add_manual_bibtex_export_and_validate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "wiki"
            init_result = subprocess.run([sys.executable, str(INIT_SCRIPT), str(target)], capture_output=True, text=True, check=False)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            record = target / "wiki_records" / "sources" / "SRC-0001.yaml"
            record.write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: source",
                        "status: active",
                        "duplicate_of:",
                        "superseded_by:",
                        "source_storage: external",
                        "source_url: https://arxiv.org/abs/1808.02002",
                        "page_path:",
                        "source_type: paper",
                        "source_format: pdf",
                        "title: Example Paper",
                        "authors: []",
                        "added_date: 2026-05-18",
                        "processed_date:",
                        "published_date:",
                        "content_fingerprint:",
                        "arxiv_id: 1808.02002",
                        "doi:",
                        "bibtex_key:",
                    ]
                ),
                encoding="utf-8",
            )
            (target / "wiki_records" / "bibtex" / "SRC-0001.bib").write_text("@article{Example:2018,\n  title={Example}\n}\n", encoding="utf-8")
            (target / "wiki_records" / "bibtex" / "SRC-0001.yaml").write_text(
                "\n".join(
                    [
                        "record_id: SRC-0001",
                        "record_type: bibtex",
                        "status: active",
                        "provider: manual",
                        "provider_priority:",
                        "providers_tried:",
                        "lookup_id:",
                        "bibtex_key: Example:2018",
                        "fetched_date: 2026-05-18",
                        "source_bib_path: wiki_records/bibtex/SRC-0001.bib",
                    ]
                ),
                encoding="utf-8",
            )

            export_result = subprocess.run([sys.executable, str(EXPORT_SCRIPT), str(target), "--apply"], capture_output=True, text=True, check=False)
            self.assertEqual(export_result.returncode, 0, export_result.stderr)

            validate_result = subprocess.run([sys.executable, str(VALIDATE_SCRIPT), str(target)], capture_output=True, text=True, check=False)
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
```

- [ ] **Step 7: Re-run export and end-to-end tests to verify GREEN**

Run:

```bash
python3 -m unittest tests.test_export_bibtex tests.test_end_to_end -v
```

Expected:

- Export tests `PASS`.
- End-to-end tests `PASS`.

- [ ] **Step 8: Commit the GREEN checkpoint**

```bash
git add llm-wiki/core/scripts/export_bibtex.py tests/test_export_bibtex.py tests/test_end_to_end.py docs/llm-wiki-application.md
git commit -m "fix: add bibliography export workflow"
```

## Task 6: Docs Sync, Refactor, And Full Verification

**Files:**

- Modify: `README.md`
- Modify: `docs/llm-wiki-implementation.md`
- Modify: `docs/llm-wiki-extension.md`
- Modify: `docs/llm-wiki-application.md`
- Modify: `CONTEXT.md`
- Modify: any touched script or test file only if refactor is required to keep code clear while staying green

- [ ] **Step 1: Write one failing documentation-alignment test if needed**

Only add a docs-facing starter test if one specific contract term is still unprotected. Prefer this pattern:

```python
    def test_schema_mentions_ads_token_as_optional_runtime_configuration(self):
        schema = (STARTER / "WIKI_SCHEMA.md").read_text(encoding="utf-8")
        self.assertIn("ADS_API_TOKEN", schema)
```

If all critical schema surfaces are already protected by tests from earlier tasks, skip adding a new docs-only test and move directly to refactor.

- [ ] **Step 2: Refactor only after all prior slices are green**

Allowed refactors:

- extract repeated bibtex-sidecar path logic into `bibtex_support.py`
- extract shared script-run helpers inside new tests
- tighten names and docstrings
- keep script boundaries intact

Do not:

- merge fetch and export scripts
- move bibliography logic into page/frontmatter code
- add new providers

- [ ] **Step 3: Run the full test suite**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Expected:

- Full suite `PASS`.

- [ ] **Step 4: Run coverage if `coverage` is already available locally**

Run:

```bash
coverage run -m unittest discover -s tests -v
coverage report -m
```

Expected:

- practical line coverage at or above `80%` across the new bibliography module surfaces;
- if global repo coverage is lower because of unrelated legacy areas, document the gap explicitly in the final execution summary instead of inventing new tests outside the feature scope.

- [ ] **Step 5: Run manual script smoke checks**

Run:

```bash
python3 llm-wiki/core/scripts/init_llm_wiki.py /private/tmp/llm-wiki-bibtex-smoke
python3 llm-wiki/core/scripts/validate_wiki.py /private/tmp/llm-wiki-bibtex-smoke
python3 llm-wiki/core/scripts/fetch_bibtex.py /private/tmp/llm-wiki-bibtex-smoke --missing
python3 llm-wiki/core/scripts/export_bibtex.py /private/tmp/llm-wiki-bibtex-smoke
git diff --check
```

Expected:

- init succeeds;
- validator reports `valid`;
- fetch dry-run reports no eligible sources or no changes;
- export dry-run reports no active entries or no changes;
- `git diff --check` reports no whitespace errors.

- [ ] **Step 6: Commit the refactor/docs checkpoint**

```bash
git add README.md docs/llm-wiki-implementation.md docs/llm-wiki-extension.md docs/llm-wiki-application.md CONTEXT.md llm-wiki/core/references/bibliography.md llm-wiki/core/references/record-contracts.md llm-wiki/core/references/workflows.md llm-wiki/core/references/validation.md llm-wiki/core/scripts/bibtex_support.py llm-wiki/core/scripts/fetch_bibtex.py llm-wiki/core/scripts/export_bibtex.py llm-wiki/core/scripts/validate_wiki.py tests/test_bibtex_support.py tests/test_fetch_bibtex.py tests/test_export_bibtex.py tests/test_validate_wiki.py tests/test_end_to_end.py tests/test_starter_wiki.py tests/test_init_llm_wiki.py
git commit -m "refactor: finalize bibliography workflow implementation"
```

## Validator Changes Summary

- Accept optional source-record fields:
  - `arxiv_id`
  - `doi`
  - `bibtex_key`
- Require `wiki_records/bibtex/` as a starter directory and validation surface.
- Validate BibTeX sidecars with a closed field set.
- Validate active sidecar -> `.bib` presence and key consistency.
- Validate unresolved sidecars without requiring `.bib`.
- Validate `providers_tried` ordering and allowed values.
- Validate `references.bib` only when present:
  - active entries only
  - no duplicate keys
  - non-canonical generated artifact

## Tests To Add

- `tests/test_bibtex_support.py`
- `tests/test_fetch_bibtex.py`
- `tests/test_export_bibtex.py`
- new bibliography cases in `tests/test_validate_wiki.py`
- starter/schema coverage in `tests/test_starter_wiki.py`
- starter-init coverage in `tests/test_init_llm_wiki.py`
- end-to-end aggregate flow in `tests/test_end_to_end.py`

## Backward Compatibility Notes

- Existing wikis without `wiki_records/bibtex/` should continue to validate only after re-init or after manual addition of the new starter-managed directory. The coding agent should keep this behavior explicit in docs.
- Existing source records remain valid without any bibliography artifacts.
- Existing non-paper sources remain unaffected.
- Existing paper sources without identifiers remain valid but ineligible for automatic fetch.
- `references.bib` remains optional and non-authoritative.

## Risks And Guardrails

- Network-facing fetch tests must stub provider calls; do not let the suite hit live INSPIRE or ADS.
- The validator cannot depend on live ADS token state. Enforce `providers_tried` as an ordered prefix of the fixed provider order, not as a claim that every configured provider was available locally.
- Keep BibTeX parsing intentionally minimal. Do not turn this feature into a full bibliography normalizer.
- Do not broaden fetch eligibility to title search just to make more tests pass.
- Do not silently repair orphan `.bib` files or missing sidecars.

## Exact Test Commands

```bash
python3 -m unittest tests.test_starter_wiki tests.test_init_llm_wiki -v
python3 -m unittest tests.test_bibtex_support -v
python3 -m unittest tests.test_validate_wiki -v
python3 -m unittest tests.test_fetch_bibtex -v
python3 -m unittest tests.test_export_bibtex tests.test_end_to_end -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## Self-Review

- Spec coverage:
  - schema and starter assets: Task 1
  - helper functions and identifier normalization: Task 2
  - validator and sidecar contract: Task 3
  - fetch workflow and provider policy: Task 4
  - export workflow and aggregate output: Task 5
  - docs sync and final verification: Task 6
- Placeholder scan:
  - no `TODO`, `TBD`, or “similar to task N” placeholders remain;
  - every code-changing step includes concrete code or exact command shapes.
- Type consistency:
  - source-record optional fields are consistently `arxiv_id`, `doi`, `bibtex_key`;
  - sidecar `record_type` is consistently `bibtex`;
  - ordered provider field is consistently `providers_tried`;
  - aggregate file is consistently `references.bib`.
