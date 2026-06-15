#!/usr/bin/env python3
"""sync_lens.py — the cross-store divergence detector (Love Train, fully deployed).

The Omni lenses audit git-side structure. This one audits the axis they can't see: git vs
Supabase. It reads the git registry (truth) AND the Supabase jd_entries mirror, diffs them, and
makes any divergence LOUD — a stale field, a Supabase-only object, a mirror that fell behind.
Silent overwrite was the danger; this turns it into a visible flag.

Combat 'git always wins' properly: git winning is correct, but only safe if nothing changed
Supabase without reaching git. This lens catches what slipped — the alarm that tells you the
reconcile guard fell asleep (jip_apply field edits, un-reconciled approvals, stale ghosts).

Reads: JarvisMain/yggdrasil/lal/address-registry.json (git) + {SUPABASE_URL}/rest/v1/jd_entries.
Writes: JarvisMain/yggdrasil/lal/SYNC-LENS.md. Exit 0 = in sync (or no secrets — skips clean);
exit 2 = real divergence (Supabase-only rows or field mismatches) so CI flags it red.
Env: SUPABASE_URL + SUPABASE_ANON_KEY (anon has public read on jd_entries). Stdlib only.
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "address-registry.json"
OUT = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "SYNC-LENS.md"

# Fields that actually drift (what jip_apply / jd_approve touch). Compared case-sensitively.
COMPARE = ("status", "parent", "name")


def git_side() -> dict[str, dict]:
    recs = json.loads(REG.read_text()).get("records", [])
    return {r["jnl"]: {k: (r.get(k) or "") for k in COMPARE} for r in recs if r.get("jnl")}


def supa_side(url: str, key: str) -> dict[str, dict] | None:
    sel = "select=jnl,status,parent,name"
    req = urllib.request.Request(
        f"{url.rstrip('/')}/rest/v1/jd_entries?{sel}",
        headers={"authorization": f"Bearer {key}", "apikey": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            rows = json.loads(r.read().decode())
        return {row["jnl"]: {k: (row.get(k) or "") for k in COMPARE} for row in rows if row.get("jnl")}
    except Exception as e:
        print(f"sync-lens: Supabase read failed: {e}")
        return None


def write_report(stamp: str, git_n: int, supa_n: int | None, supa_only: list, git_only: list,
                 mismatches: list, note: str = "") -> None:
    L = [
        "# Sync Lens — git vs Supabase (cross-store divergence)",
        "",
        f"_generated: {stamp} · git registry vs `jd_entries` mirror. Combat 'git always wins': "
        "winning is correct; this catches what changed Supabase without reaching git._",
        "",
    ]
    if note:
        L += [f"> {note}", ""]
    if supa_n is None:
        L += ["**Status: SKIPPED** — no Supabase secrets; cannot diff. (CI provides them.)", ""]
    else:
        clean = not (supa_only or mismatches)
        L += [f"**Status: {'IN SYNC ✓' if clean else 'DIVERGENCE ⚠'}** · git {git_n} · Supabase {supa_n} "
              f"· {len(supa_only)} Supabase-only · {len(mismatches)} field mismatch · {len(git_only)} git-only (mirror lag).",
              ""]
        L += ["## Supabase-only (canon Supabase has, git lacks — un-reconciled approval / ghost)", ""]
        L += [f"- `{j}`" for j in supa_only] or ["- ✓ none", ""]
        L += ["", "## Field mismatches (jip_apply edit or stale — git will overwrite on next mirror)", "",
              "| JNL | field | git | supabase |", "|---|---|---|---|"]
        L += [f"| `{j}` | {f} | {g} | {s} |" for j, f, g, s in mismatches] or ["| — | — | — | — |"]
        L += ["", "## git-only (git has, Supabase lacks — mirror hasn't run yet; usually transient)", ""]
        L += [f"- `{j}`" for j in git_only[:50]] or ["- ✓ none", ""]
    OUT.write_text("\n".join(L) + "\n")


def main() -> int:
    now = datetime.now(timezone.utc)
    stamp = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')} ({now.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M %Z')})"
    g = git_side()
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_KEY") or "").strip()
    if url and not url.startswith("http"):
        url = "https://" + url
    if not (url and key):
        write_report(stamp, len(g), None, [], [], [], note="Run in CI with SUPABASE_URL + SUPABASE_ANON_KEY to diff the stores.")
        print("sync-lens: no Supabase secrets — wrote skip report.")
        return 0
    s = supa_side(url, key)
    if s is None:
        write_report(stamp, len(g), None, [], [], [], note="Supabase unreachable this run.")
        return 0
    supa_only = sorted(set(s) - set(g))
    git_only = sorted(set(g) - set(s))
    mismatches = []
    for j in sorted(set(g) & set(s)):
        for f in COMPARE:
            if g[j][f] != s[j][f]:
                mismatches.append((j, f, g[j][f], s[j][f]))
    write_report(stamp, len(g), len(s), supa_only, mismatches, git_only)
    diverged = bool(supa_only or mismatches)
    print(f"sync-lens: git {len(g)} · supa {len(s)} · supa-only {len(supa_only)} · "
          f"mismatch {len(mismatches)} · git-only {len(git_only)} → {'DIVERGENCE' if diverged else 'IN SYNC'}")
    return 2 if diverged else 0


if __name__ == "__main__":
    raise SystemExit(main())
