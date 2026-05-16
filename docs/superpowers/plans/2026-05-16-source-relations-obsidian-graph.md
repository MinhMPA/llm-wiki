# Source Relations Obsidian Graph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add first-class source-to-source relations so Obsidian and similar Markdown graph tools show readable, schema-governed source relationships.

**Architecture:** Keep relation records canonical in `wiki_records/relations/*.yaml`, render active outgoing relations as deterministic Obsidian links in source summary pages, and validate that the structured and rendered layers match. Preserve the current portable plain Markdown/YAML design: schema first, deterministic standard-library scripts, minimal Obsidian page properties, no semantic automation without human approval.

**Tech Stack:** Python standard library, Markdown, simple YAML subset parsed by `validate_wiki.py`, `unittest`, portable skill files.

---

## Interview Decisions

- Managed relation boundary: every link in a managed `## Related sources` section must be backed by one relation record.
- Freeform Obsidian links remain allowed outside the managed section and are not treated as managed source relations.
- Source pages with no active outgoing relations omit `## Related sources`.
- Managed relation links are grouped by relation type.
- The managed section format is strict; ordinary page prose remains loosely validated by existing Obsidian-link checks.
- Readable source slugs are required for new/generated pages, but old opaque page paths remain backward compatible.
- Slug collision policy: title slug, then year, then author/org token, then source ID fallback.
- Duplicate and superseded source lifecycle fields remain authoritative and must be mirrored by graph-visible relation records once processed source pages exist.
- Relation direction is v1-only `source_to_target`.
- Examples use baby-care scenarios for user-facing docs and research-literature scenarios for relation-heavy tests/spec examples.
- Schema changes are proposal-first: add a pending proposal, then apply approved schema changes only after human approval.
- Relation records use universal `record_id` with values like `REL-0001`, not `relation_id`.
- Obsidian graph readability comes from readable source page filenames/slugs, not from frontmatter display behavior.
- Managed link labels come from the target source record's authoritative `title`.
- Only `status: active` relation records render.
- `evidence` is required and must be a list, but may be empty.
- `notes` is excluded from v1 relation records.
- `confidence` is required with values `low`, `medium`, `high`, or `unknown`.
- `created_date` is required; `reviewed_date` is optional and may be blank.
- Relation IDs are globally sequential.
- Relation records live in `wiki_records/relations/`.
- V1 relation type vocabulary is exactly: `cites`, `builds_on`, `extends`, `supports`, `contradicts`, `revises`, `duplicates`, `supersedes`, `uses_dataset`, `uses_method`, `same_topic`, `same_entity`, `background_for`, `responds_to`.
- Links within each relation type group are ordered by target source title, then relation `record_id`.
- A declared managed `## Related sources` section must contain only relation-type groups and managed relation bullets.
- Include a deterministic renderer script in v1.
- Renderer is a separate script: `llm-wiki/core/scripts/render_relations.py`.
- Renderer defaults to dry-run/check mode; `--apply` is required for writes.
- Renderer may remove stale now-empty managed sections only in `--apply` mode.

## File-By-File Change List

- Create or modify `WIKI_SCHEMA_PROPOSALS.md` in the target wiki during implementation:
  - Add a pending schema proposal for source relation records, managed related-source links, readable slug policy, validator behavior, and renderer behavior.
  - Do not apply the schema change until the human approves this proposal.

- Modify `llm-wiki/core/assets/starter-wiki/WIKI_SCHEMA_PROPOSALS.md`:
  - Keep the template generic.
  - Do not pre-seed an approved relation proposal unless the user explicitly instructs the implementation agent to ship the starter with that proposal.

- Modify `llm-wiki/core/assets/starter-wiki/WIKI_SCHEMA.md` after approval:
  - Add `wiki_records/relations/` to `Directory Layout`.
  - Add relation record contract under `Naming Conventions`.
  - Add managed `Related sources` rendering rules under `Page Types` or `Evidence And Citations`; prefer `Page Types` if framed as source summary page structure.
  - Add relation rendering to `Lint Workflow`.
  - Add human approval rules for semantic relation changes to `Review Policy`.
  - Keep all existing top-level headings unchanged and in the same order.

- Modify `llm-wiki/core/assets/starter-wiki/wiki_records/relations/.gitkeep`:
  - Add this starter directory.

- Modify `llm-wiki/core/references/record-contracts.md`:
  - Add relation record contract, field list, required fields, optional fields, closed-field rule, controlled values, ID/filename rule, endpoint rules, date rules, and lifecycle mirror rules.

- Modify `llm-wiki/core/references/page-contracts.md`:
  - Add managed `## Related sources` contract.
  - Document grouped relation type subheadings and exact bullet format.
  - Document that no-relation source pages omit the section.
  - Document that unmanaged prose belongs outside the managed section.

- Modify `llm-wiki/core/references/workflows.md` if present:
  - Add relation creation/update workflow.
  - Add renderer workflow: dry-run first, then `--apply`, then validate.

- Modify `llm-wiki/core/scripts/init_llm_wiki.py`:
  - Include `wiki_records/relations/.gitkeep` in starter-managed paths through the existing asset-copy mechanism.
  - Preserve merge-safe behavior.

- Modify `llm-wiki/core/scripts/validate_wiki.py`:
  - Add relation record loading and validation.
  - Add managed related-source section parsing and validation.
  - Add processed duplicate/superseded mirror validation.
  - Add required directory validation for `wiki_records/relations`.
  - Keep dependency-free standard-library implementation.

- Create `llm-wiki/core/scripts/render_relations.py`:
  - Read source records, relation records, and source summary pages.
  - Compute desired managed sections from active outgoing relation records.
  - In dry-run mode, report stale/missing/extra managed sections and exit nonzero when changes are needed.
  - In `--apply` mode, rewrite only managed `## Related sources` sections.
  - Omit sections when no active outgoing relations exist.
  - Never edit prose outside the managed section.
  - Refuse to write if base records/pages are invalid enough that rendering would be ambiguous.

- Modify `docs/specs/source-relations-obsidian-graph-spec.md`:
  - Align the spec with interview decisions: `record_id`, no `notes`, active-only rendering, renderer script, dry-run default, strict managed section, proposal-first governance.

- Modify `docs/llm-wiki-extension.md`:
  - Add extension guidance for new relation types and managed relation contract changes.
  - State that schema, validator, renderer, and tests must change together after approval.

- Modify root `README.md`:
  - Add user-facing explanation of source relations and Obsidian graph-readable source pages.
  - Keep baby-care examples for readability.

- Modify tests:
  - `tests/test_starter_wiki.py`
  - `tests/test_validate_wiki.py`
  - `tests/test_init_llm_wiki.py`
  - Add `tests/test_render_relations.py`
  - Update end-to-end tests if starter validation assumes the exact required directory list.

## Relation Record Contract

Use this closed v1 shape:

```yaml
record_id: REL-0001
record_type: relation
status: active
source_record_id: SRC-0001
target_record_id: SRC-0002
relation_type: cites
direction: source_to_target
evidence: []
created_date: 2026-05-16
reviewed_date:
confidence: high
```

Required fields:

- `record_id`
- `record_type`
- `status`
- `source_record_id`
- `target_record_id`
- `relation_type`
- `direction`
- `evidence`
- `created_date`
- `confidence`

Optional fields:

- `reviewed_date`

Rules:

- `record_id` must match `REL-\d{4}` and filename stem.
- `record_type` must be `relation`.
- `status` must be `active` or `archived`.
- `source_record_id` and `target_record_id` must reference existing source records.
- `source_record_id` must not equal `target_record_id`.
- `direction` must be `source_to_target`.
- `relation_type` must be in the accepted v1 vocabulary.
- `evidence` must be a list and may be empty.
- `created_date` and nonblank `reviewed_date` values must be valid ISO dates.
- `confidence` must be `low`, `medium`, `high`, or `unknown`.
- Unknown fields are invalid.

## Managed Section Contract

Desired rendered form:

```markdown
## Related sources

### Cites
- [[sources/readable-source-title|Readable Source Title]] (`REL-0001`)
```

Rules:

- Render only active outgoing relations from the page's backing `record_id`.
- Group by relation type with deterministic title-case labels.
- Order groups by a fixed vocabulary order matching the schema.
- Order bullets within a group by target source title, then relation `record_id`.
- Link target must be the target source record's `page_path` relative to `wiki_pages/`, without `.md`.
- Link label must equal the target source record's `title`.
- Relation ID must appear as backticked inline code in parentheses.
- If no active outgoing relations exist, omit the whole section.
- The section may contain only blank lines, `###` relation type headings, and managed bullets.
- Explanatory prose must live outside the managed section.

## Validator Changes

- Add `wiki_records/relations` to required directories.
- Add `RelationRecord` dataclass or equivalent internal structure.
- Add constants:
  - `RELATION_ID_RE`
  - `REQUIRED_RELATION_FIELDS`
  - `ALLOWED_RELATION_FIELDS`
  - `RELATION_STATUSES`
  - `RELATION_TYPES`
  - `RELATION_DIRECTIONS`
  - `RELATION_CONFIDENCES`
  - relation type display labels.
- Add `load_relation_records(root, errors)` parallel to `load_source_records`.
- Add `validate_relation_records(root, relation_records, source_records, errors)`.
- Add validation for relation ID filename matching, closed fields, required fields, scalar/list types, endpoint existence, self-edge rejection, date fields, and controlled vocabularies.
- Add managed section parser for source summary pages.
- Add validation that every active outgoing relation whose source and target pages exist has exactly one rendered managed bullet in the source page.
- Add validation that every managed bullet corresponds to exactly one active relation record.
- Add validation that archived relations are not rendered.
- Add validation that managed section group headings match relation type labels.
- Add validation that managed bullets use the exact target path, target title, and relation ID.
- Add validation that unmanaged content inside `## Related sources` fails.
- Add lifecycle mirror validation:
  - processed `status: duplicate` + `duplicate_of` requires an active `duplicates` relation.
  - processed `status: superseded` + `superseded_by` requires an active `supersedes` relation.
  - unprocessed lifecycle records continue to validate only the lifecycle target field.
- Preserve existing Obsidian link validation for links outside managed sections.
- Preserve backward compatibility by not failing existing source pages solely because their `page_path` uses an opaque `SRC-0001` style slug.

## Renderer Behavior

Command shape:

```bash
python3 llm-wiki/core/scripts/render_relations.py /path/to/wiki
python3 llm-wiki/core/scripts/render_relations.py /path/to/wiki --apply
```

Dry-run mode:

- Reads records and pages.
- Computes desired managed sections.
- Prints files that would change.
- Exits `0` when no changes are needed.
- Exits nonzero when changes are needed or rendering is blocked.
- Does not write files.

Apply mode:

- Rewrites only `## Related sources` managed sections.
- Inserts a managed section when active outgoing relations exist and the page lacks one.
- Replaces stale managed sections.
- Removes a stale managed section when no active outgoing relations remain.
- Leaves all other source-summary prose unchanged.

Blocking conditions:

- missing source record endpoint;
- missing source summary page for a relation that should render;
- duplicate relation IDs;
- invalid page frontmatter;
- ambiguous or malformed existing managed section that cannot be safely bounded.

## Tests To Add

### Starter Tests

- `test_required_paths_exist` includes `wiki_records/relations/.gitkeep`.
- Schema tests assert relation records are documented without changing top-level schema headings.
- Schema tests assert `Related sources` managed section rules exist.
- Reference docs tests, if added, assert relation contract and renderer workflow are documented.

### Validator Tests

- Valid starter wiki still passes.
- Valid relation record with two processed source records and matching managed link passes.
- Relation record missing required field fails.
- Relation record unknown field such as `notes` fails.
- `record_id` / filename mismatch fails.
- Invalid relation type fails.
- Invalid status fails.
- Invalid direction fails.
- Invalid confidence fails.
- `evidence` scalar fails.
- Missing source endpoint fails.
- Self-relation fails.
- Archived relation rendered in page fails.
- Active relation missing from page fails.
- Managed page link without relation record fails.
- Managed bullet with wrong target path fails.
- Managed bullet with wrong display label fails.
- Managed bullet with wrong relation ID fails.
- Ungrouped bullet inside `## Related sources` fails.
- Prose inside managed section fails.
- Source page with no relations and no section passes.
- Source page with no relations but stale managed section fails validation before renderer apply.
- Processed duplicate source without matching `duplicates` relation fails.
- Unprocessed duplicate source without matching relation passes if `duplicate_of` is valid.
- Processed superseded source without matching `supersedes` relation fails.
- Existing opaque `page_path: wiki_pages/sources/SRC-0001.md` remains valid if all other rules pass.

### Renderer Tests

- Dry-run reports missing managed section and does not edit file.
- `--apply` inserts grouped managed section.
- `--apply` updates stale target label/path/relation ID.
- `--apply` removes stale section when no active outgoing relations remain.
- Archived relations are omitted.
- Groups render in schema vocabulary order.
- Bullets render by target title then relation ID.
- Renderer preserves prose before and after the managed section.
- Renderer refuses malformed existing managed section with unsafe boundaries.

### Init Tests

- New starter initialization creates `wiki_records/relations/.gitkeep`.
- Merge-safe init skips an existing `wiki_records/relations` directory.
- `--force` follows current starter-managed overwrite rules without deleting user relation records.

### End-To-End Tests

- Initialize starter wiki.
- Add two source records and pages.
- Add one relation record.
- Run renderer dry-run and observe nonzero stale report.
- Run renderer `--apply`.
- Run validator and expect success.

## Migration And Backward Compatibility

- Existing wikis gain a new required `wiki_records/relations/` directory once the approved schema is applied.
- Existing source pages do not need `## Related sources` unless active outgoing relation records exist.
- Existing opaque source page filenames remain valid; new generation workflows should prefer readable slugs.
- Existing `duplicate_of` and `superseded_by` fields remain authoritative. Matching relation records are required only for processed source summaries after this feature is active.
- Archived relation records remain valid but must not render.
- No migration should rewrite ordinary page prose.
- Renderer changes are mechanical and explicit: dry-run by default, `--apply` required for writes.
- Schema proposal approval is the compatibility boundary. Do not change `WIKI_SCHEMA.md` or validator behavior for relation records before approval.

## Risks And Open Questions

- Managed section parsing must have clear bounds. The implementation should define the section as starting at `## Related sources` and ending at the next `## ` heading or end of file.
- Relation type display labels must be deterministic and documented. Recommended labels: `Cites`, `Builds on`, `Extends`, `Supports`, `Contradicts`, `Revises`, `Duplicates`, `Supersedes`, `Uses dataset`, `Uses method`, `Same topic`, `Same entity`, `Background for`, `Responds to`.
- The renderer and validator may duplicate parsing logic at first. Avoid premature abstraction unless duplication becomes error-prone during implementation.
- Simple YAML parser supports only the current subset. Relation evidence must remain a simple list of scalar strings in v1.
- Obsidian graph node labels depend on filenames, so readable slugs matter more than page frontmatter titles.
- Relation semantics are human-authored. The validator can enforce structure and consistency, not truth.

## Implementation Tasks

### Task 1: Add Proposal-First Governance Artifact

**Files:**

- Modify target wiki `WIKI_SCHEMA_PROPOSALS.md` during implementation.
- Modify `docs/specs/source-relations-obsidian-graph-spec.md`.

Steps:

- [ ] Add a pending proposal block for source relations before applying schema changes.
- [ ] Mark change type as schema extension and validator behavior.
- [ ] List affected schema sections: `Directory Layout`, `Page Types`, `Evidence And Citations`, `Lint Workflow`, `Naming Conventions`, `Review Policy`, `Schema Evolution`.
- [ ] State human approval is required.
- [ ] Update the spec to match accepted decisions.
- [ ] Run the proposal/schema tests and confirm they pass.

### Task 2: Add Starter Directory And Schema Documentation

**Files:**

- Modify `llm-wiki/core/assets/starter-wiki/WIKI_SCHEMA.md`.
- Create `llm-wiki/core/assets/starter-wiki/wiki_records/relations/.gitkeep`.
- Modify `llm-wiki/core/references/record-contracts.md`.
- Modify `llm-wiki/core/references/page-contracts.md`.

Steps:

- [ ] Add failing starter tests for required relation directory and schema text.
- [ ] Add the starter directory.
- [ ] Document the relation record contract.
- [ ] Document the managed section contract.
- [ ] Run starter tests and confirm they pass.

### Task 3: Extend Validator For Relation Records

**Files:**

- Modify `llm-wiki/core/scripts/validate_wiki.py`.
- Modify `tests/test_validate_wiki.py`.

Steps:

- [ ] Add failing tests for valid and invalid relation records.
- [ ] Add relation record loading.
- [ ] Add closed-field, required-field, ID, endpoint, date, and vocabulary validation.
- [ ] Add `wiki_records/relations` required directory validation.
- [ ] Run focused validator tests and confirm relation record tests pass.

### Task 4: Extend Validator For Managed Sections

**Files:**

- Modify `llm-wiki/core/scripts/validate_wiki.py`.
- Modify `tests/test_validate_wiki.py`.

Steps:

- [ ] Add failing tests for active relation rendering, missing rendering, extra rendering, archived rendering, wrong labels, wrong targets, unmanaged content, and no-section no-relation cases.
- [ ] Parse managed `## Related sources` sections only on source summary pages.
- [ ] Validate exact group headings and bullet format.
- [ ] Validate bidirectional consistency between active relation records and rendered managed bullets.
- [ ] Keep ordinary Obsidian link validation unchanged outside the managed section.
- [ ] Run focused validator tests and confirm managed section tests pass.

### Task 5: Add Duplicate/Superseded Graph Mirror Validation

**Files:**

- Modify `llm-wiki/core/scripts/validate_wiki.py`.
- Modify `tests/test_validate_wiki.py`.

Steps:

- [ ] Add failing tests for processed duplicate and superseded records missing mirrored relation records.
- [ ] Add passing tests for unprocessed duplicate and superseded records with valid lifecycle targets.
- [ ] Implement mirror validation after both source and relation records are loaded.
- [ ] Run focused validator tests and confirm lifecycle mirror tests pass.

### Task 6: Add Deterministic Relation Renderer

**Files:**

- Create `llm-wiki/core/scripts/render_relations.py`.
- Create `tests/test_render_relations.py`.

Steps:

- [ ] Add failing renderer dry-run and apply tests.
- [ ] Implement read-only dry-run behavior.
- [ ] Implement `--apply` behavior for inserting, replacing, and removing managed sections.
- [ ] Ensure only managed sections are changed.
- [ ] Ensure malformed unsafe sections block rendering.
- [ ] Run renderer tests and confirm they pass.

### Task 7: Update Init And End-To-End Coverage

**Files:**

- Modify `llm-wiki/core/scripts/init_llm_wiki.py` only if needed by starter asset handling.
- Modify `tests/test_init_llm_wiki.py`.
- Modify `tests/test_end_to_end.py`.

Steps:

- [ ] Add failing init test for the relation directory.
- [ ] Ensure starter asset copy includes `wiki_records/relations/.gitkeep`.
- [ ] Add end-to-end relation workflow test.
- [ ] Run init and end-to-end tests.

### Task 8: Update User And Extension Documentation

**Files:**

- Modify `README.md`.
- Modify `docs/llm-wiki-extension.md`.
- Modify `docs/llm-wiki-implementation.md` if it describes validation or scripts.
- Modify `llm-wiki/core/README.md` if it lists scripts.

Steps:

- [ ] Add user-facing relation workflow with baby-care example.
- [ ] Add power-user renderer and validation workflow.
- [ ] Add extension guidance for changing relation types or managed-section format.
- [ ] Keep competitor-neutral positioning.
- [ ] Run documentation-related tests.

### Task 9: Full Verification

Steps:

- [ ] Run all tests with bytecode disabled.
- [ ] Run validator against a freshly initialized starter wiki.
- [ ] Run renderer dry-run against a relation fixture.
- [ ] Inspect `git diff` to ensure no unrelated files changed.
- [ ] Commit only after tests pass and the human has approved implementation.

## Exact Test Command

Run the full suite:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Expected result:

```text
OK
```

Targeted commands during implementation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_validate_wiki -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_render_relations -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_starter_wiki -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_init_llm_wiki -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_end_to_end -v
```

## Self-Review

- Spec coverage: the plan covers relation records, rendered Obsidian links, readable slugs, duplicate/superseded mirrors, validator changes, renderer script, docs, tests, and backward compatibility.
- Placeholder scan: no implementation task relies on undefined "later" behavior; semantic automation remains explicitly out of scope.
- Type consistency: the plan consistently uses `record_id`, `record_type: relation`, `wiki_records/relations/`, `source_record_id`, `target_record_id`, and managed `## Related sources` sections.
