# LLM Wiki Documentation

This directory documents the implemented portable LLM Wiki skill.

## Start Here

- `llm-wiki-application.md`: use the skill to create and maintain a wiki.
- `llm-wiki-implementation.md`: understand the shipped files, scripts, and validator contract.
- `llm-wiki-extension.md`: extend the schema, validator, adapters, or future packaging without breaking the core contract.
- `llm-wiki-packaging.md`: packaging decision and future distribution path.
- `adr/0001-center-starter-wiki-on-schema.md`: architectural decision for schema-centered starter wikis.

## Source Of Truth

The runtime source of truth for a generated wiki is its `WIKI_SCHEMA.md`. The documentation here explains the implementation, but agents working inside a wiki must read that wiki's schema before editing records or pages.
