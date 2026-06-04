#!/usr/bin/env python3
"""
P42 — KRONOS consolidation (the loop's COMPRESS step, made autonomous).

The fold itself already exists as a governed Postgres function: fold_identity()
clusters recent memory onto the keel into a fresh identity_summary (append-only,
lineage-strict) and chains guard_identity() (NEMESIS/MERIDIAN drift check). This
script is the SCHEDULER — KRONOS calls the fold on a cron with the service role.
fold_identity/guard_identity are service-role-only (P42 migration), so this is the
sole path that can trigger a re-fold.

Governed, not autonomous mutation: it compresses EXISTING memory into a new layer;
it never edits old layers and never changes the keel. A guard FLAG is surfaced for
Raven, not acted on (GL2).

Env: SUPABASE_URL, SUPABASE_SERVICE_KEY (required — soft-skips without it).
"""
import json
import os
import sys
import urllib.request

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
REST = f"{SUPABASE_URL}/rest/v1"


def _req(method: str, url: str, body: dict | None = None) -> tuple[int, object]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode() or "null"
        try:
            return resp.status, json.loads(raw)
        except Exception:
            return resp.status, raw


def latest(source_type: str) -> dict:
    url = f"{REST}/mnemos_memories?source_type=eq.{source_type}&order=timestamp.desc&limit=1&select=text,metadata,timestamp"
    try:
        _, rows = _req("GET", url)
        return rows[0] if isinstance(rows, list) and rows else {}
    except Exception:
        return {}


def main() -> int:
    if not SERVICE_KEY:
        print("KRONOS consolidate: no SUPABASE_SERVICE_KEY — skipped (soft-fail).", file=sys.stderr)
        return 0
    # Trigger the fold (chains the guard). Service-role only.
    try:
        status, _ = _req("POST", f"{REST}/rpc/fold_identity", {})
    except Exception as e:
        print(f"KRONOS consolidate: fold_identity failed — {e}", file=sys.stderr)
        return 1
    if status not in (200, 204):
        print(f"KRONOS consolidate: fold_identity returned HTTP {status}", file=sys.stderr)
        return 1

    summary = latest("identity_summary")
    guard = latest("guard_check")
    meta = summary.get("metadata") or {}
    gmeta = guard.get("metadata") or {}
    verdict = gmeta.get("verdict", "?")

    print("━" * 50)
    print("KRONOS — identity consolidated (the compress step)")
    print(f"  folded_count: {meta.get('folded_count', '?')}")
    print(f"  folded_at:    {meta.get('folded_at', summary.get('timestamp', '?'))}")
    print(f"  guard:        {verdict}")
    head = (summary.get("text") or "")[:160].replace("\n", " ")
    if head:
        print(f"  summary:      {head}…")
    if verdict == "FLAG":
        print("  ⚠ MERIDIAN/NEMESIS flagged drift in this fold — surfaced for Raven (not auto-acted).")
    print("━" * 50)
    # A FLAG is informational (drift surfaced for Raven), not a job failure.
    return 0


if __name__ == "__main__":
    sys.exit(main())
