"""Reconcile connector-approved JD entries from Supabase back into files (files = truth).

The dex connector (jarvis-dex) promotes approved proposals to ACTIVE in Supabase. This
script pulls ACTIVE entries that aren't yet represented as local JD files, writes them into
JarvisMain/yggdrasil/jd/dynamic.json, and regenerates the substrate. Run by .github/workflows/dex-reconcile.yml.

Auth: SUPABASE_URL + SUPABASE_ANON_KEY (anon has public read on jd_entries). Skips cleanly
if unset. Idempotent: only adds entries missing from the current dex.

Usage: SUPABASE_URL=... SUPABASE_ANON_KEY=... python3 scripts/dex_reconcile.py
Exit 0 = no change or success; exit 2 = entries were added (workflow opens a PR).
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JD_DIR = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
DYN = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "dynamic.json"

# Fields a dynamic entry carries (the rest is derived by seed.py).
KEEP = ("jnl", "name", "type", "definition", "purpose", "source", "related", "tags", "status")


def fetch_active() -> list[dict]:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        print("dex_reconcile: SUPABASE_URL / SUPABASE_ANON_KEY unset — skipping.")
        return []
    endpoint = (f"{url}/rest/v1/jd_entries?status=eq.ACTIVE"
                "&select=jnl,name,type,definition,purpose,source,related,tags,status")
    req = urllib.request.Request(endpoint, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main() -> int:
    try:
        active = fetch_active()
    except Exception as e:  # network/transient — don't fail the build
        print(f"dex_reconcile: fetch failed ({e}); skipping.")
        return 0
    if not active:
        return 0

    local = {f.stem for f in JD_DIR.glob("*.md")}
    dyn = json.loads(DYN.read_text())
    have = {e["jnl"] for e in dyn["entries"]}
    added = []
    for row in active:
        jnl = row.get("jnl")
        if not jnl or jnl in local or jnl in have:
            continue  # already in files (hardcoded manifest or already reconciled)
        dyn["entries"].append({k: row.get(k) for k in KEEP if row.get(k) is not None})
        added.append(jnl)

    if not added:
        print(f"dex_reconcile: in sync ({len(active)} ACTIVE entries, nothing new).")
        return 0

    dyn["entries"].sort(key=lambda e: e["jnl"])
    DYN.write_text(json.dumps(dyn, indent=2) + "\n")
    print(f"dex_reconcile: reconciled {len(added)} new entr(y/ies): {', '.join(added)}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
