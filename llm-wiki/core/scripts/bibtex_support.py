#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ARXIV_ID_RE = re.compile(r"^(?P<base>\d{4}\.\d{4,5})(?:v\d+)?$")
PROVIDER_ORDER = ["inspire", "ads"]


def normalize_arxiv_id(value: str) -> str:
    match = ARXIV_ID_RE.match(value.strip())
    if match is None:
        return value.strip()
    return match.group("base")


def normalize_bibtex_entry(entry_text: str) -> str:
    return entry_text.strip() + "\n"


def extract_bibtex_key(entry_text: str) -> str:
    match = re.search(r"@\w+\{([^,\s]+)\s*,", entry_text)
    if match is None:
        raise ValueError("BibTeX entry key not found")
    return match.group(1).strip()


def rewrite_bibtex_key(entry_text: str, new_key: str) -> str:
    normalized = normalize_bibtex_entry(entry_text)
    return re.sub(r"^(@\w+\{)([^,\s]+)(\s*,)", rf"\g<1>{new_key}\3", normalized, count=1)


def source_identifier_candidates(data: dict[str, object]) -> list[str]:
    candidates: list[str] = []

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
    raw_stem = Path(Path(raw_path).name).stem
    if ARXIV_ID_RE.match(raw_stem):
        candidates.append(f"arxiv:{normalize_arxiv_id(raw_stem)}")

    return list(dict.fromkeys(candidates))


def is_eligible_bibtex_source(data: dict[str, object]) -> bool:
    return (
        str(data.get("status") or "") == "active"
        and str(data.get("source_type") or "") == "paper"
        and bool(source_identifier_candidates(data))
    )
