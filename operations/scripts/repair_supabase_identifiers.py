#!/usr/bin/env python3
from pathlib import Path

REPLACEMENTS = {
    "jsr:@core/supabase/functions-js/edge-runtime.d.ts": "jsr:@supabase/functions-js/edge-runtime.d.ts",
    "jsr:@core/supabase/supabase-js@2": "jsr:@supabase/supabase-js@2",
    "https://esm.sh/@core/supabase/supabase-js@2": "https://esm.sh/@supabase/supabase-js@2",
    "https://cdn.jsdelivr.net/npm/@core/supabase": "https://cdn.jsdelivr.net/npm/@supabase",
    "uses: core/supabase/setup-cli": "uses: supabase/setup-cli",
    "actions/checkout@v4": "actions/checkout@v6",
}

roots = [Path("core"), Path("app"), Path(".github")]
files = [Path("index.html")]
for root in roots:
    if root.exists():
        files.extend(path for path in root.rglob("*") if path.is_file())

changed = []
for path in sorted(set(files)):
    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    updated = original
    for old, new in REPLACEMENTS.items():
        updated = updated.replace(old, new)
    if path == Path(".github/workflows/deploy-edge-functions.yml"):
        updated = updated.replace(
            'supabase link --project-ref "$PROJECT_REF"',
            'supabase link --project-ref "$PROJECT_REF" --workdir core',
        )
        updated = updated.replace(
            'supabase functions deploy "$NAME" --project-ref "$REF" --no-verify-jwt',
            'supabase functions deploy "$NAME" --project-ref "$REF" --no-verify-jwt --workdir core',
        )
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed.append(str(path))

print("\n".join(changed) if changed else "No changes required")
