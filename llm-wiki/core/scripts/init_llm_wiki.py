#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class InitSummary:
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    overwritten: list[Path] = field(default_factory=list)


def starter_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "starter-wiki"


def copy_starter(source: Path, target: Path, force: bool) -> InitSummary:
    summary = InitSummary()
    target.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source.rglob("*")):
        relative_path = source_path.relative_to(source)
        target_path = target / relative_path

        if source_path.is_dir():
            if not target_path.exists():
                target_path.mkdir(parents=True)
                summary.created.append(relative_path)
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists():
            if force:
                shutil.copy2(source_path, target_path)
                summary.overwritten.append(relative_path)
            else:
                summary.skipped.append(relative_path)
            continue

        shutil.copy2(source_path, target_path)
        summary.created.append(relative_path)

    return summary


def print_summary(summary: InitSummary) -> None:
    for label, paths in (
        ("created", summary.created),
        ("skipped", summary.skipped),
        ("overwritten", summary.overwritten),
    ):
        print(f"{label}: {len(paths)}")
        for path in paths:
            print(f"  {path.as_posix()}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize an LLM Wiki from the bundled starter wiki.")
    parser.add_argument("target", type=Path, help="Target directory for the initialized wiki.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing starter-managed files.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = starter_dir()
    if not source.is_dir():
        print(f"error: bundled starter wiki is missing: {source}", file=sys.stderr)
        return 1

    summary = copy_starter(source, args.target, args.force)
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
