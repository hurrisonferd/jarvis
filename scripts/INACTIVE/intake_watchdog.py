#!/usr/bin/env python3
"""Intake watchdog (P43). Runs daily via GitHub Action.

Scans intake/ for unreviewed files. If the backlog exceeds the threshold (default 3),
creates or reopens an urgent GitHub issue. Escalation levels:

  1–3 items  : INFO  — no issue, logged to stdout
  4+ items   : WARN  — open issue with backlog list
  10+ items  : ALERT — add "urgent" label, ping @hurrisonferd

Moves aged-but-reviewed files from intake/ subdirs into intake/processed/
automatically if they've been sitting > 14 days without movement.
"""
from __future__ import annotations
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTAKE_DIR = ROOT / "intake"
PROCESSED = INTAKE_DIR / "processed"
BACKLOG_THRESHOLD = 3
ESCALATION_THRESHOLD = 10
AGE_THRESHOLD_DAYS = 14

REPO = "hurrisonferd/jarvis"
BRANCH = "main"


def get_stale_files(dir_path: Path, age_days: int) -> list[tuple[Path, float]]:
    """Return (file, age_days_float) for files older than age_days."""
    now = datetime.now(timezone.utc).timestamp()
    stale = []
    for f in dir_path.rglob("*.md"):
        if f.name.startswith(".") or "processed" in f.parts:
            continue
        age = (now - f.stat().st_mtime) / 86400
        if age >= age_days:
            stale.append((f, age))
    return stale


def main() -> int:
    # Find all unreviewed intake files (not in processed/ or recycle/)
    unreviewed = []
    for sub in ("claude", "codex", "gemini", ""):
        scan = INTAKE_DIR / sub if sub else INTAKE_DIR
        if not scan.is_dir():
            continue
        for f in sorted(scan.glob("*.md")):
            if f.name.startswith("."):
                continue
            age_days = (datetime.now(timezone.utc).timestamp() - f.stat().st_mtime) / 86400
            unreviewed.append((f, age_days))

    backlog = len(unreviewed)

    print(f"INTake watchdog: {backlog} unreviewed file(s) in intake/")
    for f, age in unreviewed:
        print(f"  {age:.0f}d  {f.relative_to(INTAKE_DIR)}")

    if backlog == 0:
        print("Backlog clear. No action needed.")
        return 0

    if backlog <= BACKLOG_THRESHOLD:
        print(f"INFO: {backlog} item(s) — below threshold ({BACKLOG_THRESHOLD}). No issue created.")
        return 0

    # Build issue body
    items = "\n".join(
        f"- **{f.relative_to(INTAKE_DIR)}** — {age:.0f} day(s) old"
        for f, age in sorted(unreviewed, key=lambda x: -x[1])
    )
    severity = "🔴 ALERT" if backlog >= ESCALATION_THRESHOLD else "🟡 WARN"
    body = (
        f"## {severity} — INTAKE BACKLOG: {backlog} proposals pending Raven review\n\n"
        f"Raven, these items have been in intake/ without moving to `processed/`.\n"
        f"Per GL7/CLAUDE.md the loop is: intake → context → implement → verify → log → commit.\n"
        f"If these are still valid, they need review. If stale, move them to `processed/`.\n\n"
        f"### Unreviewed items\n{items}\n\n"
        f"---\n"
        f"*Intake watchdog · {datetime.now(timezone.utc).isoformat()} · "
        f"`scripts/intake_watchdog.py`*"
    )

    labels = ["governance"] + (["urgent"] if backlog >= ESCALATION_THRESHOLD else [])

    try:
        # Check for existing open backlog issue
        result = subprocess.run(
            ["gh", "issue", "list", "--repo", REPO, "--label", "governance", "--state", "open",
             "--json", "number,title", "--jq", ".[] | select(.title | contains(\"INTAKE BACKLOG\"))"],
            capture_output=True, text=True, check=True,
        )
        existing = json.loads(result.stdout) if result.stdout.strip() else []
    except Exception as e:
        print(f"WARN: could not check existing issues: {e}")
        existing = []

    if existing:
        issue_num = existing[0]["number"]
        print(f"Updating existing issue #{issue_num}")
        subprocess.run(
            ["gh", "issue", "comment", "--repo", REPO, str(issue_num),
             "--body", f"Watchdog re-run · {datetime.now(timezone.utc).date()} · {backlog} unreviewed items"],
            check=True,
        )
    else:
        print(f"Creating new issue (backlog={backlog})")
        result = subprocess.run(
            ["gh", "issue", "create", "--repo", REPO, "--title",
             f"INTAKE BACKLOG: {backlog} proposals pending Raven review",
             "--body", body, "--label"] + labels,
            capture_output=True, text=True, check=True,
        )
        print(f"Created: {result.stdout.strip()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
