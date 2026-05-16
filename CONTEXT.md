# LLM Wiki

This context defines the language for designing an agent-portable LLM-maintained markdown wiki system.

## Language

**LLM Wiki pattern**:
An agent-neutral workflow where raw sources are compiled into a persistent, maintained markdown wiki.
_Avoid_: RAG cache, document chatbot

**Portable LLM Wiki skill**:
A copyable skill folder that teaches different agent environments how to initialize, ingest into, query, and lint an LLM Wiki.
_Avoid_: Codex-only skill, vendor adapter

**Portable core**:
The agent-neutral part of the Portable LLM Wiki skill containing shared workflows, page contracts, starter assets, and deterministic scripts.
_Avoid_: Codex implementation, adapter logic

**Agent adapter**:
A thin agent-specific entrypoint that loads the Portable core and translates the host agent's skill conventions into the shared workflow.
_Avoid_: core workflow, separate implementation

**Portable skill layout**:
The folder structure with `core/` for shared implementation and `adapters/` for host-specific skill entrypoints.
_Avoid_: flat host-specific skill, duplicated workflows

**Host-agent contract**:
The minimum capability set an agent must support to use the Portable LLM Wiki skill.
_Avoid_: universal compatibility, runtime guarantee

**LLM Wiki starter wiki**:
A generated markdown workspace containing immutable raw sources, maintained wiki pages, and local operating instructions.
_Avoid_: Template repo, vault only

**Wiki schema**:
The canonical `WIKI_SCHEMA.md` file at the root of a starter wiki that defines local operating rules for maintaining that wiki.
_Avoid_: AGENTS.md as source of truth, CLAUDE.md as source of truth, WIKI.md as overview

**Living schema**:
A Wiki schema whose fixed top-level sections persist while generic rules, workflows, and conventions evolve with human approval.
_Avoid_: static template, entry-specific rulebook, junk drawer

**Schema skeleton**:
The fixed ordered set of top-level headings required in every Wiki schema.
_Avoid_: optional outline, suggested headings

**Schema proposals**:
The root-level `WIKI_SCHEMA_PROPOSALS.md` file where agents stage proposed changes to the Wiki schema before human approval.
_Avoid_: wiki page backlog, open research questions, silent schema edits

**Schema proposal queue**:
A maintained `WIKI_SCHEMA_PROPOSALS.md` structure with `Pending`, `Approved`, and `Rejected` sections.
_Avoid_: append-only proposal log, unstructured scratchpad

**Schema proposal block**:
A fixed-format proposal entry with an ID, status, date, change type, affected schema sections, proposed change, reason, genericity justification, and approval notes.
_Avoid_: freeform proposal, vague schema request

**Wiki pages**:
The `wiki_pages/` directory containing generated and maintained markdown pages.
_Avoid_: raw sources, schema, chat history

**Source record**:
A structured source identity and provenance file that tracks one raw source independently from its readable summary.
_Avoid_: summary page, raw source, citation prose

**YAML source record**:
A `.yaml` Source record file that contains authoritative structured source metadata.
_Avoid_: markdown-frontmatter source record, prose record, page-owned source metadata

**Source record ID**:
A stable sequential identifier for a Source record, formatted like `SRC-0001`.
_Avoid_: title slug as identity, raw path as identity, hash-only identity

**Record type**:
The explicit `record_type` field in a Wiki record, such as `source`.
_Avoid_: overloading page `type`, generic `id`

**Page type**:
The explicit `page_type` field in Mirrored page properties, such as `source_summary`.
_Avoid_: generic `type`

**Explicit short field names**:
The field-naming rule that names should be explicit when they stay below three words.
_Avoid_: ambiguous short names, overlong field names

**Competitive edge**:
A design advantage of the Portable LLM Wiki skill relative to hosted notebook ecosystems such as NotebookLM and Gemini.
_Avoid_: feature parity checklist, unsupported product claim

**Guiding principle**:
A non-absolute design preference that should shape tradeoffs while still allowing deliberate exceptions.
_Avoid_: hard invariant, casual suggestion

**Competitor-neutral positioning**:
The rule that operational artifacts state design principles without naming competing products.
_Avoid_: name-dropping, marketing copy in schema

**Validator boundary**:
The rule that validators enforce concrete structure and consistency, not broad guiding principles directly.
_Avoid_: validator as philosophy checker

**Source record citation**:
A footnote-style citation whose ID matches a Source record ID and whose body starts with that record ID.
_Avoid_: raw-path citation, unstructured source mention

**Merge-safe init**:
Initialization behavior that creates missing starter files but does not overwrite existing files unless explicitly forced.
_Avoid_: destructive init, all-or-nothing init

**Ingest output contract**:
The minimum artifact set produced or updated when a source is processed into the wiki.
_Avoid_: chat-only ingest, source summary without record

**Subagent-driven synthesis drafting**:
An optional workflow where a background agent turns a query/answer exchange into a file-ready synthesis candidate before human filing approval.
_Avoid_: automatic filing, unreviewed synthesis page

**Lint boundary**:
The rule that lint may fix mechanical drift automatically but must propose semantic, schema, or destructive changes for human approval.
_Avoid_: silent semantic rewrite, report-only maintenance

**Processed date**:
The date a raw source was turned into maintained records and pages.
_Avoid_: ingested date

**Source dates**:
The Source record date fields `added_date`, `processed_date`, and `published_date`.
_Avoid_: ambiguous date, non-ISO dates

**Content fingerprint**:
An optional algorithm-prefixed fingerprint for detecting source duplication or raw-source drift.
_Avoid_: required hash, prose checksum

**Wiki records**:
The `wiki_records/` directory containing structured operational and provenance records.
_Avoid_: readable wiki pages, raw sources

**Source summary**:
A readable wiki page that explains and interprets one raw source for humans and agents.
_Avoid_: source record, source registry

**Structured/unstructured split**:
The design principle that machine-oriented records and human-readable pages live in separate layers.
_Avoid_: metadata hidden in prose, prose-only registry

**Lean extensibility**:
The design principle that v1 should include only required structures while making later deeper or wider expansion straightforward.
_Avoid_: speculative directories, closed design, ball of mud

**Machine/human readability balance**:
The design principle that stable machine-readable identifiers and readable human-facing names should be designed together.
_Avoid_: opaque-only IDs, brittle title-based IDs

**Universal field preference**:
The design principle that a field should be universal across page or record types when it can be precise without losing meaning.
_Avoid_: needless type-specific field names

**Mirrored page properties**:
Minimal YAML frontmatter on Wiki pages that mirrors selected fields from authoritative Wiki records for Obsidian Properties and browsing.
_Avoid_: duplicate record, nested metadata, full provenance mirror

**Human navigation metadata**:
Page-level metadata used for human browsing, linking, and discovery, such as Obsidian `tags` and `aliases`.
_Avoid_: authoritative record fields, provenance fields

**Foundational record field**:
A field that is human-readable but essential to the identity or provenance of a Wiki record.
_Avoid_: browsing-only metadata

**Universal authors field**:
The `authors` field used across all source kinds for people or organizations responsible for a source.
_Avoid_: creators, speakers, publishers, medium-specific contributor fields

**Source storage mode**:
The required `source_storage` field that states whether a source is stored locally or referenced externally.
_Avoid_: implicit missing raw_path, ambiguous source availability

**Source type**:
The required controlled-category field for what kind of source a Source record represents.
_Avoid_: source_kind, source_form

**Source format**:
The optional controlled field for the artifact format of a Source record.
_Avoid_: conflating format with source_type

**Source status**:
The `status` field on Source records with values `active`, `archived`, `superseded`, or `duplicate`.
_Avoid_: duplicated, removed

**Source status relation**:
A status-specific field that points from a non-active Source record to another Source record, such as `duplicate_of` or `superseded_by`.
_Avoid_: vague related_record_id, overgeneral relation list

**Source relation**:
A structured source-to-source edge between two Source records, represented canonically as a relation record and rendered for graph tools in the source summary.
_Avoid_: unmanaged related-source prose, graph-only link

**Managed related source link**:
An Obsidian link in a source summary's managed `Related sources` section that must be backed by a Source relation record.
_Avoid_: ad hoc source link, untracked graph edge

**Relation type group**:
A subsection under a source summary's managed `Related sources` section that groups Managed related source links by controlled relation type.
_Avoid_: mixed relation list, prose grouping

**Relation section renderer**:
A deterministic helper script that rewrites only managed `Related sources` sections from Source relation records.
_Avoid_: LLM-formatted relation block, whole-page formatter

**Platform pointer file**:
A tiny platform-specific instruction file such as `AGENTS.md` or `CLAUDE.md` that tells the host agent to read the Wiki schema.
_Avoid_: duplicated schema, adapter-owned rules

## Relationships

- A **Portable LLM Wiki skill** implements the **LLM Wiki pattern**
- A **Portable LLM Wiki skill** consists of one **Portable core** and one or more **Agent adapters**
- A **Portable LLM Wiki skill** uses the **Portable skill layout**
- The **Portable core** contains templates, references, starter assets, and scripts
- **Agent adapters** initially include `adapters/codex/SKILL.md` and `adapters/claude/SKILL.md`
- An **Agent adapter** must not contain workflow logic that is absent from the **Portable core**
- The **Host-agent contract** requires loading markdown instructions, reading sibling files by relative path, and either running or inspecting bundled scripts
- The first **Agent adapters** target Claude Code and ChatGPT Codex
- A **Portable LLM Wiki skill** creates or maintains an **LLM Wiki starter wiki**
- An **LLM Wiki starter wiki** has exactly one canonical **Wiki schema**
- A **Wiki schema** is a **Living schema** with fixed top-level sections
- A **Living schema** must conform to the **Schema skeleton**
- A **Living schema** may evolve generic rules and subsections, but must not contain entry-specific exceptions
- Adding an exception-like rule to a **Living schema** requires human review and approval
- **Schema proposals** live beside the **Wiki schema**, not under **Wiki pages**
- Agents may append to **Schema proposals** but need human approval before applying exception-like changes to the **Wiki schema**
- **Schema proposals** are maintained as a **Schema proposal queue**
- Agents may add proposals to `Pending`, but may only move proposals to `Approved` or `Rejected` after explicit human approval or rejection
- Each item in the **Schema proposal queue** must use a **Schema proposal block**
- **Schema proposal block** IDs are sequential, such as `P-0001` and `P-0002`
- A **Schema proposal block** status must agree with its queue section
- `Schema skeleton change` and `Exception-like rule` proposal types always require explicit human approval
- An **LLM Wiki starter wiki** stores **Wiki pages** separately from raw sources and the **Wiki schema**
- V1 **Wiki pages** layout requires `index.md`, `log.md`, `questions.md`, `sources/`, `entities/`, `concepts/`, and `synthesis/`
- An **LLM Wiki starter wiki** stores **Wiki records** separately from **Wiki pages**
- An **LLM Wiki starter wiki** includes **Platform pointer files** for supported agents
- A **Platform pointer file** must refer to the **Wiki schema** instead of duplicating schema rules
- An **LLM Wiki starter wiki** preserves raw sources while exposing maintained wiki pages
- A raw source has a separate **Source record** and **Source summary** in v1
- A **Source record** owns stable provenance and identity; a **Source summary** owns readable explanation
- A v1 **Source record** is a **YAML source record**
- A **Source record** uses a **Source record ID**
- A **Source record** stores its ID in the universal `record_id` field
- A **Wiki record** uses **Record type** instead of overloading page `type`
- A **Source summary** may use a readable slug while linking to its **Source record ID**
- A **Source record** uses **Processed date** for the source-processing milestone
- A **Source record** may include a blank **Content fingerprint**
- When present, a **Content fingerprint** must include an algorithm prefix such as `sha256:`
- **Source dates** use ISO format `YYYY-MM-DD`
- `added_date` is required in **Source records**
- `processed_date` is required once `page_path` points to an existing Source summary
- `published_date` is optional
- The **Structured/unstructured split** is a core design principle
- **Lean extensibility** allows only required v1 record types while reserving a clear path for future record types through schema approval
- The **Machine/human readability balance** favors stable IDs for records and readable names for pages
- The **Universal field preference** favors `record_id` over type-specific page fields such as `source_id`
- **Mirrored page properties** exist only for Obsidian-compatible lookup and display
- **Mirrored page properties** must stay minimal, unique per note, flat, and limited to Obsidian-supported property types
- V1 **Mirrored page properties** are limited to `record_id`, `page_type`, `title`, and `tags`
- V1 **Mirrored page properties** use **Page type** instead of generic `type`
- `processed_date` belongs in authoritative **Wiki records** and is not mirrored by default
- **Explicit short field names** apply to both records and page properties
- `tags` live only in **Mirrored page properties** in v1 for Obsidian browsing
- `aliases` live only in **Mirrored page properties** in v1 for Obsidian linking and lookup
- **Wiki records** do not use `tags` in v1
- **Wiki records** avoid **Human navigation metadata**
- `title` is a **Foundational record field** for Source records
- `title` is authoritative in the **Source record** and mirrored into **Mirrored page properties**
- `authors` is a **Universal authors field** in **Source records**
- Unknown `authors` are represented as an empty list
- **Source storage mode** is required in **Source records**
- V1 **Source storage mode** values are only `local` and `external`
- If `source_storage` is `local`, `raw_path` is required and must point under `raw/`
- If `source_storage` is `external`, `source_url` is required and `raw_path` may be blank
- Hybrid source-storage modes are excluded in v1 to avoid extra parsing and filtering complexity
- **Source type** is required in **Source records**
- V1 **Source type** values are `article`, `paper`, `book`, `chapter`, `transcript`, `note`, `image`, `dataset`, `video`, `audio`, `report`, `documentation`, and `other`
- `article` covers prose-first web or print pieces, including blog posts, essays, news articles, and generic web articles
- `documentation` covers reference, help, and API docs
- `report` covers institutional, business, government, and analyst reports
- `paper` covers academic or research papers and preprints
- **Source format** is optional in **Source records**
- V1 **Source format** values are `markdown`, `pdf`, `html`, `text`, `image`, `audio`, `video`, `csv`, `spreadsheet`, `json`, `yaml`, and `other`
- V1 **Source record** fields are `record_id`, `record_type`, `status`, `duplicate_of`, `superseded_by`, `source_storage`, `raw_path`, `source_url`, `page_path`, `source_type`, `source_format`, `title`, `authors`, `added_date`, `processed_date`, `published_date`, and `content_fingerprint`
- `record_id`, `record_type`, `status`, `source_storage`, `source_type`, `title`, `authors`, and `added_date` are required
- `record_type` must be `source` for **Source records**
- `page_path` may be blank until processed
- `source_format`, `published_date`, and `content_fingerprint` are optional
- **Source status** is required in **Source records**
- New **Source records** default to `active`
- If **Source status** is `duplicate`, `duplicate_of` is required
- If **Source status** is `superseded`, `superseded_by` is required
- `duplicate_of` and `superseded_by` are **Source status relations**
- A **Source relation** records a source-to-source edge independently from either Source summary page
- A **Managed related source link** must correspond to exactly one **Source relation**
- Ordinary Obsidian links outside the managed `Related sources` section are not **Managed related source links**
- **Managed related source links** are organized under **Relation type groups**
- A **Relation section renderer** may mechanically update **Managed related source links** without changing source-summary prose
- **Wiki records** remain authoritative when **Mirrored page properties** disagree
- V1 **Competitive edges** are portability, model choice, version history, maintenance automation, custom schemas, Obsidian-native organization, local/private operation, longitudinal records, and auditability
- **Competitive edges** are **Guiding principles**, not absolute constraints
- Operational artifacts use **Competitor-neutral positioning**
- **Guiding principles** live under the `Purpose` section of the **Wiki schema**
- The **Validator boundary** limits validation to concrete files, schemas, references, mirrors, and links
- V1 validation checks required files/directories, schema skeleton, schema proposal queue shape, source record contracts, minimal page frontmatter, mirrored fields, Obsidian links, and source-record footnote references
- V1 validation does not semantically judge whether every durable claim has a citation
- Starter initialization uses **Merge-safe init** by default
- Forced initialization may overwrite starter-managed files but must not delete user files
- Initialization reports created, skipped, and overwritten files
- The **Ingest output contract** requires one Source record, one Source summary unless explicitly record-only, an index update, and a log entry
- Entity, concept, synthesis, and question updates are optional but expected when the source supports them
- Ingest reports must list records/pages created or updated, unresolved questions, and validation result
- **Subagent-driven synthesis drafting** may prepare target paths, draft bodies, citations, index entries, and log entries
- **Subagent-driven synthesis drafting** must not write durable Wiki pages without human approval
- **Subagent-driven synthesis drafting** is an advanced reference workflow in v1 and a likely separate skill in a future plugin
- Future plugin packaging is documented in plans, not runtime skill instructions
- The **Lint boundary** allows automatic mechanical fixes such as index updates, unambiguous link fixes, frontmatter normalization, mirrored-field sync, and lint log entries
- The **Lint boundary** requires approval for duplicate merges, superseding sources, evidence changes, schema rules, new synthesis pages, deletion, archival, and substantive rewrites
- Durable claims in **Wiki pages** use **Source record citations**
- `index.md`, `log.md`, and `questions.md` are exempt from **Source record citations** unless they make substantive claims

## Example dialogue

> **Dev:** "Should the first version be a Codex skill?"
> **Domain expert:** "No. It should be a **Portable LLM Wiki skill** that can be copied into any compatible agent skill folder."

> **Dev:** "Should the workflow live in `SKILL.md`?"
> **Domain expert:** "No. Put shared behavior in the **Portable core** and keep `SKILL.md` as an **Agent adapter**."

> **Dev:** "Should the skill folder be flat?"
> **Domain expert:** "No. Use the **Portable skill layout** with shared core files and thin adapters."

> **Dev:** "Does portable mean every agent must execute the scripts?"
> **Domain expert:** "No. The **Host-agent contract** requires the agent to benefit from the markdown instructions and inspect scripts; script execution is optional but recommended."

> **Dev:** "Should the canonical schema be `AGENTS.md`, `CLAUDE.md`, `WIKI.md`, or `WIKI_SCHEMA.md`?"
> **Domain expert:** "Use `WIKI_SCHEMA.md` as the **Wiki schema** because the schema is the central piece everything else revolves around."

> **Dev:** "Should generated pages live under `wiki/`, `pages/`, or `wiki_pages/`?"
> **Domain expert:** "Use `wiki_pages/` so the maintained **Wiki pages** are explicit and distinct from raw sources and schema."

> **Dev:** "Which Wiki page directories are required in v1?"
> **Domain expert:** "Use `sources/`, `entities/`, `concepts/`, and `synthesis/`, plus `index.md`, `log.md`, and `questions.md`."

> **Dev:** "Should starter wikis include `AGENTS.md` and `CLAUDE.md`?"
> **Domain expert:** "Yes, but only as **Platform pointer files**. The **Wiki schema** remains the brain of the wiki agent on every platform."

> **Dev:** "Can the schema evolve as the wiki grows?"
> **Domain expert:** "Yes, but as a **Living schema**: top-level sections stay fixed, rules stay generic, and entry-specific exceptions require human approval."

> **Dev:** "Can agents add or rename top-level schema sections?"
> **Domain expert:** "No. The **Schema skeleton** is fixed and validators should fail on missing, renamed, duplicated, or reordered top-level headings."

> **Dev:** "Where should proposed schema changes live?"
> **Domain expert:** "In `WIKI_SCHEMA_PROPOSALS.md`, beside `WIKI_SCHEMA.md`, because schema governance is not ordinary wiki content."

> **Dev:** "Is `WIKI_SCHEMA_PROPOSALS.md` an append-only log?"
> **Domain expert:** "No. It is a **Schema proposal queue** with pending, approved, and rejected proposal sections."

> **Dev:** "Can agents write schema proposals as plain prose?"
> **Domain expert:** "No. Use a **Schema proposal block** so proposals are reviewable and machine-checkable."

> **Dev:** "Should source provenance live in the same page as the source summary?"
> **Domain expert:** "No. Split **Source record** and **Source summary** in v1 to avoid a larger migration later."

> **Dev:** "Can source records contain human-readable processing notes?"
> **Domain expert:** "Not in v1. A **Source record** is a **YAML source record**; explanation belongs in **Wiki pages**."

> **Dev:** "Where do structured source records live?"
> **Domain expert:** "Under **Wiki records**, separate from **Wiki pages**, because structured and unstructured data should be split by default."

> **Dev:** "Should v1 create every possible record folder?"
> **Domain expert:** "No. Use **Lean extensibility**: create only required v1 structures, but make later expansion deliberate and straightforward."

> **Dev:** "Should source records use titles, hashes, or sequential IDs?"
> **Domain expert:** "Use **Source record IDs** like `SRC-0001`; they balance stable machine identity with human readability."

> **Dev:** "Should source records use `id` or `record_id`?"
> **Domain expert:** "Use universal `record_id`, and use **Record type** for the record category."

> **Dev:** "Should page frontmatter use `type`?"
> **Domain expert:** "No. Use **Page type** because field names should be explicit when they remain short."

> **Dev:** "Should authoritative records contain tags?"
> **Domain expert:** "No. In v1, tags live only on **Wiki pages** as Obsidian browsing metadata."

> **Dev:** "What should differentiate this from hosted notebook ecosystems?"
> **Domain expert:** "Optimize for **Competitive edges** centered on portable files, model choice, schema control, maintenance, records, and auditability."

> **Dev:** "Are competitive edges hard constraints?"
> **Domain expert:** "No. Treat them as **Guiding principles**: strong defaults that can be bent deliberately."

> **Dev:** "Should `WIKI_SCHEMA.md` name competing products?"
> **Domain expert:** "No. Use **Competitor-neutral positioning** and express principles without name-dropping."

> **Dev:** "Should guiding principles add a new top-level schema section?"
> **Domain expert:** "No. Put **Guiding principles** under `Purpose` so the **Schema skeleton** stays fixed."

> **Dev:** "Should validators enforce competitive guiding principles directly?"
> **Domain expert:** "No. The **Validator boundary** says validators enforce concrete structure and consistency."

> **Dev:** "Should v1 validation judge citation adequacy semantically?"
> **Domain expert:** "No. V1 validation is deterministic; semantic citation adequacy belongs to lint."

> **Dev:** "Should citations point to raw files, page paths, or source records?"
> **Domain expert:** "Use **Source record citations** so durable claims cite stable provenance records."

> **Dev:** "Should initialization fail when the target directory is non-empty?"
> **Domain expert:** "No. Use **Merge-safe init** by default and reserve overwrites for explicit force."

> **Dev:** "What must source processing produce?"
> **Domain expert:** "Follow the **Ingest output contract**: Source record, Source summary, index update, log entry, and relevant derived page updates."

> **Dev:** "Can a background agent pre-draft synthesis from a query answer?"
> **Domain expert:** "Yes. Use **Subagent-driven synthesis drafting**, but require human approval before filing."

> **Dev:** "Should future plugin packaging be mentioned in the runtime skill?"
> **Domain expert:** "No. Keep plugin evolution in plans; runtime skill instructions should stay focused."

> **Dev:** "Can lint change the wiki automatically?"
> **Domain expert:** "Only across the **Lint boundary**: mechanical fixes are allowed, semantic or destructive changes require approval."

> **Dev:** "Should authoritative records contain aliases?"
> **Domain expert:** "No. `aliases` are **Human navigation metadata** and belong on **Wiki pages**."

> **Dev:** "Should `title` be page-only because it is human-readable?"
> **Domain expert:** "No. `title` is a **Foundational record field** because it identifies the source."

> **Dev:** "Should source records use `authors`, `creators`, or medium-specific contributor fields?"
> **Domain expert:** "Use the **Universal authors field** across source kinds to keep records readable and parseable."

> **Dev:** "Must every source be stored under `raw/`?"
> **Domain expert:** "No. Use **Source storage mode** so local-first and external-only sources are both explicit."

> **Dev:** "Should source storage include a hybrid or partial mode?"
> **Domain expert:** "No. V1 only uses `local` and `external`; hybrid modes add complexity and parsing cost."

> **Dev:** "Should the source category field be `source_kind`, `source_type`, or `source_form`?"
> **Domain expert:** "Use **Source type** because it is conventional, explicit, and short."

> **Dev:** "Should v1 keep the source type vocabulary very small?"
> **Domain expert:** "No. Include common source media and document categories in the initial **Source type** vocabulary."

> **Dev:** "After removing `webpage`, where do generic web articles go?"
> **Domain expert:** "Use `article` for prose-first web or print pieces."

> **Dev:** "Should source type also encode file format?"
> **Domain expert:** "No. Use optional **Source format** when artifact format matters."

> **Dev:** "What is the v1 Source record contract?"
> **Domain expert:** "Use the fixed Source record field set with required identity, lifecycle, storage, type, title, authors, and added date fields."

> **Dev:** "Should the duplicate status be called `duplicate` or `duplicated`?"
> **Domain expert:** "Use `duplicate` because it names the current state; `duplicated` sounds like an event."

> **Dev:** "Should duplicate and superseded records use noun-style pointers?"
> **Domain expert:** "No. Use **Source status relations** like `duplicate_of` and `superseded_by` because they encode the relationship directly."

> **Dev:** "Should the source-processing timestamp be called `ingested_date`?"
> **Domain expert:** "No. Use **Processed date** because it is clearer to non-technical users."

> **Dev:** "Should source records require content hashes in v1?"
> **Domain expert:** "No. Include optional **Content fingerprint** support, but allow it to be blank."

> **Dev:** "Which source dates are required?"
> **Domain expert:** "`added_date` is required, `processed_date` is required after a Source summary exists, and `published_date` is optional."

> **Dev:** "Should Wiki page frontmatter duplicate full records?"
> **Domain expert:** "No. Use **Mirrored page properties** only for minimal Obsidian-compatible lookup and display fields."

> **Dev:** "Should page frontmatter use `source_id` for source summaries?"
> **Domain expert:** "No. Use universal `record_id`; if something can be universal, it should be universal."

> **Dev:** "Should `processed_date` appear in Wiki page frontmatter?"
> **Domain expert:** "No. Keep `processed_date` in authoritative **Wiki records** unless a future schema proposal adds date filtering to page properties."

## Flagged ambiguities

- "skill" could mean a Codex-specific skill or a portable skill folder — resolved: the first deliverable is a **Portable LLM Wiki skill**.
- "adapter" could mean a forked implementation — resolved: an **Agent adapter** is only a thin entrypoint over the **Portable core**.
- "out of the box" could imply universal runtime behavior — resolved: it means useful under the **Host-agent contract**, with scripts optional when the host cannot execute them.
- "wiki" is too broad for the skill name and too vague for the central schema file — resolved: the skill remains `llm-wiki`, and the canonical **Wiki schema** is `WIKI_SCHEMA.md`.
- Platform-specific markdown files could become competing schemas — resolved: they are **Platform pointer files** and must point to `WIKI_SCHEMA.md`.
- "living schema" could become a dumping ground for one-off page behavior — resolved: the **Living schema** only accepts generic rules, and exception-like additions require human approval.
- "fixed top-level sections" could be treated as guidance — resolved: the **Schema skeleton** is mandatory and validator-enforced.
- `SCHEMA.md` and `SCHEMA_PROPOSALS.md` were considered too generic — resolved: keep the `WIKI_` prefix in `WIKI_SCHEMA.md` and `WIKI_SCHEMA_PROPOSALS.md`.
- `WIKI_SCHEMA_PROPOSALS.md` could become an unstructured log — resolved: it is a **Schema proposal queue**.
- Freeform schema proposals could hide vague or exception-like changes — resolved: every proposal must use a **Schema proposal block**.
- Combining source identity with source prose would make a later split more expensive — resolved: v1 has separate **Source records** and **Source summaries**.
- Allowing prose in source records would blur the **Structured/unstructured split** — resolved: v1 records are **YAML source records**.
- Mixing structured records with readable pages would blur responsibilities — resolved: the **Structured/unstructured split** keeps **Wiki records** separate from **Wiki pages**.
- Avoiding speculative structure should not create future migration pain — resolved: **Lean extensibility** keeps v1 small while requiring schema-approved expansion points.
- Title-based source identity is readable but brittle, while hash identity is stable but opaque — resolved: use **Source record IDs**.
- `ingested_date` is agent jargon — resolved: use `processed_date`.
- Source hashing is useful but not required for manual v1 workflows — resolved: **Content fingerprint** is optional and nullable.
- Dates can mean different lifecycle events — resolved: use explicit **Source dates** with ISO values.
- Page frontmatter could become a second record system — resolved: **Mirrored page properties** are minimal and non-authoritative.
- Obsidian accepts custom dates but does not own LLM Wiki processing dates — resolved: `processed_date` is not mirrored into page frontmatter by default.
- Type-specific ID fields would fragment queries without adding meaning — resolved: use universal `record_id`.
- Generic `id` would conflict with external identifiers — resolved: use universal `record_id`.
- Generic `type` would be ambiguous across records and pages — resolved: use **Record type** and **Page type**.
- Tags are a browsing affordance rather than provenance in v1 — resolved: keep `tags` out of **Wiki records**.
- Human-facing navigation fields can complicate machine records — resolved: keep **Human navigation metadata** in **Wiki pages**.
- `title` is human-readable but foundational to source identity — resolved: keep it authoritative in **Source records** and mirror it to pages.
- Medium-specific contributor fields would complicate records — resolved: use `authors` universally.
- The original pattern is local-first but not always local-only — resolved: **Source storage mode** supports `local` and `external`.
- `source_kind` is informal and `source_form` suggests media format — resolved: use `source_type`.
- A too-small source type vocabulary would force common materials into `other`, but `webpage` is too broad — resolved: include common source media and document categories in v1, excluding `webpage`.
- Without `webpage`, prose web sources need a home — resolved: classify them as `article`.
- Source category and artifact format answer different questions — resolved: use **Source type** and optional **Source format**.
- Hybrid source storage would require extra attention and filtering — resolved: v1 excludes hybrid modes.
- Source lifecycle state needs structured filtering — resolved: **Source status** uses `active`, `archived`, `superseded`, and `duplicate`.
- Generic relation fields would hide status semantics — resolved: use status-specific **Source status relations**.
