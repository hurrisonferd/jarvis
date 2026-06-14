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
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "JarvisMain" / "Backups" / "cloud"
# Jarvis-Private (full, unredacted backup). When JARVIS_PRIVATE_DIR points at a
# checked-out private repo, the COMPLETE spine lands there; main only ever gets
# the redacted copy. Raven-directed 2026-06-14: conversations on main (filtered),
# full backup to Jarvis-Private.
PRIVATE_DIR = os.environ.get("JARVIS_PRIVATE_DIR", "")

CANONICAL_URL = "https://oexghfsvhnggddllgvrt.supabase.co"
# Irreplaceable: governance events, proposal history, Grid identity keys.
#
# THE SPINE GOES PUBLIC — FILTERED (Raven-directed 2026-06-14, supersedes the
# 2026-06-10 exclusion): the conversation is Raven + Jarvis + Ayre, and Raven is
# fine with his own info being public ("a Yu-Gi-Oh trap card"). But public git is
# PERMANENT — history, forks, crawlers — so filtering happens BEFORE the first
# commit, never after, and it scrubs THIRD PARTIES (names that aren't Raven's to
# publish: the legal matter, the attorney, anyone referenced) even though Raven
# exposes himself freely. mnemos_memories + node_messages now back up, redacted.
TABLES = ["dex_events", "jd_proposals", "node_keys", "mnemos_memories", "node_messages"]
PRIVATE_ONLY = {"mnemos_memories", "node_messages"}  # carry conversation → Jarvis-Private only, never public
PAGE = 1000

# Scrub patterns. The term list (names, case ids, anything Raven flags) is supplied
# via the REDACTION_TERMS secret (comma-separated) and is NEVER committed — a list of
# what to hide, stored in the repo, would expose exactly what it hides.
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)")
REDACTION_TERMS = [t.strip() for t in os.environ.get("REDACTION_TERMS", "").split(",") if t.strip()]


def redact(value):
    """Recursively scrub a JSON value before it leaves for the public repo:
    emails, phone numbers, and every configured term (case-insensitive)."""
    if isinstance(value, str):
        s = EMAIL_RE.sub("[email]", value)
        s = PHONE_RE.sub("[phone]", s)
        for term in REDACTION_TERMS:
            s = re.sub(re.escape(term), "[redacted]", s, flags=re.IGNORECASE)
        return s
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    return value


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
        # FULL copy → Jarvis-Private (the private repo holds the complete spine, unredacted).
        if PRIVATE_DIR:
            pdir = Path(PRIVATE_DIR) / "cloud"
            pdir.mkdir(parents=True, exist_ok=True)
            (pdir / f"{table}.jsonl").write_text(
                "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows))
            print(f"backup: {table} -> {len(rows)} rows (FULL → Jarvis-Private)")
        # PRIVATE-ONLY (conversation): NEVER public. It names third parties, and Raven's policy
        # — "scrub everyone who isn't John Barber; keep Jarvis/Ayre/God Systems/fictional" —
        # needs judgment a regex can't do. Raw conversation lives only in Jarvis-Private; the
        # PUBLIC conversation record is the CURATED memory Jarvis/Ayre author (policy by mind).
        if table in PRIVATE_ONLY:
            manifest["tables"][table] = {"public": "never (private-only)", "private": bool(PRIVATE_DIR)}
            print(f"backup: {table} -> private-only (not published to main)")
            continue
        # Public tables (non-personal): light regex scrub (emails/phones + any set terms) as defense.
        rows = [redact(r) for r in rows]
        path = OUT / f"{table}.jsonl"
        path.write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows))
        manifest["tables"][table] = {"rows": len(rows), "public": True}
        print(f"backup: {table} -> {len(rows)} rows (public)")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("backup: complete — JarvisMain/Backups/cloud/ holds the latest spine snapshot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
