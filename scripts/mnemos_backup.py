"""MNEMOS cloud backup (Raven-directed 2026-06-10) — the spine's durable copy in the core.

JarvisMain is git-versioned; the CLOUD is the unbacked surface. This exports the
irreplaceable Supabase tables — the ones NOT derivable from the repo — into
JarvisMain/Backups/cloud/ as sorted JSONL (stable diffs, latest snapshot).
jd_entries/jnl_registry are intentionally excluded: the repo seed regenerates them
(files are truth; the mirror is derived).

Run by .github/workflows/mnemos-backup.yml (weekly cron + dispatch), which commits
the snapshot when it changed. Stdlib only. Skips cleanly without secrets.
"""
from __future__ import annotations
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "JarvisMain" / "Backups" / "cloud"

CANONICAL_URL = "https://oexghfsvhnggddllgvrt.supabase.co"
# Irreplaceable: memory spine, governance events, proposal history, Grid identity + mail.
TABLES = ["mnemos_memories", "dex_events", "jd_proposals", "node_keys", "node_messages"]
PAGE = 1000


def norm_url(u: str) -> str:
    u = (u or "").strip().rstrip("/")
    if not u:
        return CANONICAL_URL
    if "://" not in u:
        u = f"https://{u}"
    host = u.split("://", 1)[1].split("/", 1)[0]
    if "." not in host:
        u = u.replace(host, f"{host}.supabase.co", 1)
    return u if u.startswith("https://") and ".supabase.co" in u else CANONICAL_URL


def fetch_all(base: str, key: str, table: str) -> list[dict]:
    rows: list[dict] = []
    offset = 0
    while True:
        req = urllib.request.Request(
            f"{base}/rest/v1/{table}?select=*&order=id&limit={PAGE}&offset={offset}",
            headers={"apikey": key, "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            page = json.loads(r.read().decode())
        rows.extend(page)
        if len(page) < PAGE:
            return rows
        offset += PAGE


def main() -> int:
    base = norm_url(os.environ.get("SUPABASE_URL", ""))
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not key:
        print("backup: SUPABASE_SERVICE_KEY unset — skipping (no backup taken).")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"exported_at": datetime.now(timezone.utc).isoformat(), "tables": {}}
    for table in TABLES:
        try:
            rows = fetch_all(base, key, table)
        except Exception as e:  # noqa: BLE001 — one table failing must not lose the rest
            print(f"backup: {table} FAILED ({e}) — continuing")
            manifest["tables"][table] = {"error": str(e)[:160]}
            continue
        path = OUT / f"{table}.jsonl"
        path.write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows))
        manifest["tables"][table] = {"rows": len(rows)}
        print(f"backup: {table} -> {len(rows)} rows")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("backup: complete — JarvisMain/Backups/cloud/ holds the latest spine snapshot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
