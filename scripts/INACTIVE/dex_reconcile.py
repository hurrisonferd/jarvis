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
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JD_DIR = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
DYN = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "dynamic.json"
CODES = ROOT / "JarvisMain" / "yggdrasil" / "jfs" / "project-codes.json"

# Fields a dynamic entry carries (the rest is derived by seed.py).
KEEP = ("jnl", "name", "type", "definition", "purpose", "source", "related", "tags", "status", "aliases")
PROJECT_TYPES = ("JGPP", "JIP", "JD", "BIO")


def materialize_project(row: dict) -> bool:
    """Connector-approved project artifacts become real files in the project node
    (FMT §3 filename grammar + self-describing frontmatter), not dynamic.json pointers —
    seed.py adopts the file through the same intake path new.py uses. Files = truth."""
    jnl = row.get("jnl", "")
    parts = jnl.split("-")
    if len(parts) < 4 or parts[0] != "PROJ" or parts[2] not in PROJECT_TYPES:
        return False
    info = json.loads(CODES.read_text())["codes"].get(parts[1]) if CODES.exists() else None
    if not info:
        return False  # unknown project code — falls back to dynamic.json
    folder = ROOT / info["folder"] / parts[2]
    folder.mkdir(parents=True, exist_ok=True)
    proj = Path(info["folder"]).name.upper()
    subject = re.sub(r"[^A-Za-z0-9]+", "-", row.get("name", "")).strip("-").upper() or "UNTITLED"
    path = folder / f"{proj}{parts[2]}-{date.today().strftime('%m%d%y')}-{parts[3]}-{subject}.md"
    path.write_text("\n".join([
        "---",
        f"name: {row.get('name', jnl)}",
        f"type: {parts[2]}",
        f"jnl: {jnl}",
        f"status: {row.get('status', 'ACTIVE')}",
        f"created: {date.today().isoformat()}",
        f"tags: [{', '.join(row.get('tags') or [])}]",
        f"definition: {row.get('definition', '')}",
        f"purpose: {row.get('purpose', '')}",
        f"related: [{', '.join(row.get('related') or [])}]",
        "---",
        "",
        f"# {jnl} — {row.get('name', '')}",
        "",
    ]))
    print(f"dex_reconcile: materialized {jnl} -> {path.relative_to(ROOT)}")
    return True


def fetch_active() -> list[dict]:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    if url and not url.startswith(("http://", "https://")):
        url = f"https://{url}"  # secret may omit the scheme
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
    added, added_dyn = [], []
    for row in active:
        jnl = row.get("jnl")
        if not jnl or jnl in local or jnl in have:
            continue  # already in files (hardcoded manifest or already reconciled)
        added.append(jnl)
        if materialize_project(row):
            continue  # file is its own manifest — seed.py scan adopts it
        dyn["entries"].append({k: row.get(k) for k in KEEP if row.get(k) is not None})
        added_dyn.append(jnl)

    if not added:
        print(f"dex_reconcile: in sync ({len(active)} ACTIVE entries, nothing new).")
        return 0

    if added_dyn:
        dyn["entries"].sort(key=lambda e: e["jnl"])
        DYN.write_text(json.dumps(dyn, indent=2) + "\n")
    print(f"dex_reconcile: reconciled {len(added)} new entr(y/ies): {', '.join(added)}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
