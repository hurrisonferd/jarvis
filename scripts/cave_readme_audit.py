#!/usr/bin/env python3
"""Find folders that may need README cave signs."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".temp",
    "grid_images",
    "rooms/repos",
}


def is_excluded(path: Path, root: Path, excludes: set[str]) -> bool:
    rel = path.relative_to(root).as_posix()
    parts = set(rel.split("/"))
    if parts & excludes:
        return True
    return any(rel == item or rel.startswith(item.rstrip("/") + "/") for item in excludes)


def has_sign(path: Path) -> bool:
    return (path / "README.md").exists() or (path / "INDEX.md").exists()


def should_report(path: Path) -> bool:
    files = [p for p in path.iterdir() if p.is_file()]
    dirs = [p for p in path.iterdir() if p.is_dir()]
    if not files and not dirs:
        return False
    if len(files) + len(dirs) <= 1 and path.name.startswith("."):
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit folders missing README/INDEX signs.")
    parser.add_argument("--root", default=".", help="Root to scan.")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum folder depth.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    missing: list[Path] = []
    for path in sorted(p for p in root.rglob("*") if p.is_dir()):
        if is_excluded(path, root, DEFAULT_EXCLUDES):
            continue
        depth = len(path.relative_to(root).parts)
        if depth > args.max_depth:
            continue
        if has_sign(path):
            continue
        if should_report(path):
            missing.append(path)

    for path in missing:
        print(path.relative_to(root).as_posix())
    print(f"\nmissing_signs={len(missing)} max_depth={args.max_depth}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
