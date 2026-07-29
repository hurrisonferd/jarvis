#!/usr/bin/env python3
from pathlib import Path
import sys

FORBIDDEN = (
    "jsr:@core/supabase",
    "https://esm.sh/@core/supabase",
    "https://cdn.jsdelivr.net/npm/@core/supabase",
    "uses: core/supabase/setup-cli",
)

roots = [Path("core"), Path("app"), Path(".github")]
files = [Path("index.html")]
for root in roots:
    if root.exists():
        files.extend(path for path in root.rglob("*") if path.is_file())

errors = []
for path in sorted(set(files)):
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for token in FORBIDDEN:
        if token in text:
            errors.append(f"{path}: forbidden external identifier {token}")

if errors:
    print("External identifier guard failed:")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)

print("External identifiers verified.")
