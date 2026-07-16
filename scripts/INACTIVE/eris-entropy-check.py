#!/usr/bin/env python3
"""
ERIS entropy check — GL7 enforcement via GitHub Actions.
Runs on every push to main. Computes expansion score, detects GL7 violations,
stores result to eris_entropy_log. Never blocks — Raven is authority.

GL7: No expansion without simplification.
GL7-OK marker in commit message signals deliberate, approved expansion.
"""
import json
import os
import subprocess
import sys
import urllib.request

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
if not SUPABASE_URL.startswith(("http://", "https://")):
    SUPABASE_URL = f"https://{SUPABASE_URL}"  # secret may omit the scheme

SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "")
COMMIT_SHA = os.environ.get("COMMIT_SHA", "unknown")
COMMIT_MSG = os.environ.get("COMMIT_MESSAGE", "")

REST_BASE = f"{SUPABASE_URL}/rest/v1"


def git(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""


def get_diff_stats() -> dict:
    """Parse git diff --numstat to count files and line changes."""
    raw = git("git diff --numstat HEAD~1..HEAD 2>/dev/null || git diff --numstat 4b825dc..HEAD")
    files_added = 0
    files_deleted = 0
    lines_added = 0
    lines_deleted = 0

    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added_str, deleted_str, path = parts[0], parts[1], parts[2]
        # Binary files show '-'
        try:
            la = int(added_str)
            ld = int(deleted_str)
        except ValueError:
            continue
        lines_added += la
        lines_deleted += ld
        # Track new files vs modified
        if la > 0 and ld == 0:
            files_added += 1
        elif ld > 0 and la == 0:
            files_deleted += 1

    return {
        "files_added": files_added,
        "files_deleted": files_deleted,
        "lines_added": lines_added,
        "lines_deleted": lines_deleted,
        "net_lines": lines_added - lines_deleted,
        "net_files": files_added - files_deleted,
    }


def compute_score(stats: dict) -> float:
    net_files = max(0, stats["net_files"])
    net_lines = max(0, stats["net_lines"])
    score = (net_files * 0.15) + (net_lines / 100 * 0.05)
    return round(score, 4)


def store_entropy(score: float, status: str, dimensions: dict) -> bool:
    if not SUPABASE_ANON:
        return False
    payload = json.dumps({
        "score": score,
        "status": status,
        "dimensions": dimensions,
    }).encode()
    req = urllib.request.Request(
        f"{REST_BASE}/eris_entropy_log",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "apikey": SUPABASE_ANON,
            "Authorization": f"Bearer {SUPABASE_ANON}",
            "Prefer": "return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8):
            return True
    except Exception as e:
        print(f"  [ERIS] store failed: {e}", file=sys.stderr)
        return False


def main():
    stats = get_diff_stats()
    score = compute_score(stats)

    gl7_marker = "[GL7-OK]" in COMMIT_MSG or "reduces_complexity=true" in COMMIT_MSG.lower()
    gl7_override = "[GL7-OVERRIDE]" in COMMIT_MSG

    if score <= 0.3 or gl7_marker or gl7_override:
        status = "ok"
    elif score <= 0.8:
        status = "warning"
    else:
        status = "alert"

    dimensions = {
        **stats,
        "commit_sha": COMMIT_SHA[:12],
        "commit_message": COMMIT_MSG[:200],
        "gl7_marker": gl7_marker,
        "gl7_override": gl7_override,
    }

    print(f"ERIS GL7 CHECK")
    print(f"  commit:    {COMMIT_SHA[:12]}")
    print(f"  score:     {score} (threshold: 0.30 warning / 0.80 alert)")
    print(f"  status:    {status.upper()}")
    print(f"  net_files: {stats['net_files']}  net_lines: {stats['net_lines']}")
    print(f"  gl7_marker:{gl7_marker}")

    if status == "warning":
        print()
        print("  GL7 WARNING: Expansion detected without simplification marker.")
        print("  Add [GL7-OK] to commit message when expansion is deliberate.")
        print("  (Not blocking — Raven is authority.)")
    elif status == "alert":
        print()
        print("  GL7 ALERT: High entropy expansion. Review required.")
        print("  Add [GL7-OVERRIDE] to commit message to suppress.")
        print("  (Not blocking — Raven is authority.)")

    stored = store_entropy(score, status, dimensions)
    print(f"  stored:    {stored}")

    # Always exit 0 — ERIS observes, Raven decides
    sys.exit(0)


if __name__ == "__main__":
    main()
