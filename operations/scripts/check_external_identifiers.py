#!/usr/bin/env python3
"""Fail CI when live source contains corrupted external Supabase identifiers."""

from pathlib import Path
import sys

BAD = (
    "jsr:@core/supabase/functions-js/edge-runtime.d.ts",
    "jsr:@core/supabase/supabase-js@2",
    "https://esm.sh/@core/supabase/supabase-js@2",
    "https://cdn.jsdelivr.net/npm/@core/supabase",
    "uses: core/supabase/setup-cli",
)

ROOTS = (Path("core"), Path("app"), Path(".github"), Path("index.html"))
SUFFIXES = {".ts", ".tsx", ".js", ".mjs", ".html", ".yml", ".yaml"}


def candidates():
    for root in ROOTS:
        if root.is_file():
            yield root
        elif root.exists():
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in SUFFIXES:
                    yield path


failures: list[tuple[Path, str]] = []
for path in candidates():
    if path.name.endswith(".source.html"):
        continue
    if "memory/audit" in path.as_posix():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for token in BAD:
        if token in text:
            failures.append((path, token))

if failures:
    print("Corrupted external identifiers found:")
    for path, token in failures:
        print(f"- {path}: {token}")
    sys.exit(1)

print("External dependency identifiers: clean")
