#!/usr/bin/env python3
"""JARVIS proactive brief — the words JARVIS sends when it reaches out first.

HUGINN observes daily; this turns the observation into a short, dense, in-voice
message pushed to Raven via send-push. Stage 3 of the companion roadmap: presence
and initiative. Cheap on our stack, and the first time JARVIS speaks first.

The composer is pure and tested — the transport (send-push) is plumbing that
activates once VAPID + a browser subscription are in place.

Run tests: python3 scripts/test_jarvis_brief.py
"""
import sys
from datetime import date, datetime


# Known fixed dates that matter to Raven. KRONOS keeps the count.
COURT_DATE = date(2026, 6, 24)  # Clarkson EEOC hearing


def days_until(target: date, today: date) -> int:
    return (target - today).days


def _commit_line(commits: list) -> str:
    n = len(commits)
    if n == 0:
        return "Quiet since yesterday — nothing new on the record."
    import re
    # Drop bracketed markers ([GL7-OK], [skip ci]) so the push reads clean.
    head = re.sub(r"\s*\[[^\]]*\]", "", commits[0]).strip()
    return f"{n} commit{'s' if n != 1 else ''} since yesterday. Latest: {head[:70]}"


def _court_line(today: date) -> str:
    d = days_until(COURT_DATE, today)
    if d < 0:
        return ""
    if d == 0:
        return "Today is June 24 — the EEOC hearing. I'm with you."
    if d <= 30:
        return f"{d} day{'s' if d != 1 else ''} to June 24 (EEOC)."
    return ""


def _pending_line(pending: list) -> str:
    if not pending:
        return ""
    ids = ", ".join(pending[:3])
    return f"Still open: {ids}."


def compose_brief(today: date, commits: list, pending: list) -> dict:
    """Build {title, body} for the proactive push. Dense, in-voice, bounded."""
    parts = [
        _commit_line(commits),
        _court_line(today),
        _pending_line(pending),
    ]
    body = " ".join(p for p in parts if p).strip()
    # Push notifications truncate hard — keep the body lean.
    if len(body) > 200:
        body = body[:197].rstrip() + "…"
    title = f"JARVIS — {today.isoformat()}"
    return {"title": title, "body": body or "Here. Building. Say the word."}


def _git(cmd: str) -> str:
    import subprocess
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def main() -> int:
    """CLI: compose today's brief from git + ledger, print JSON for the workflow."""
    import json
    today = datetime.utcnow().date()

    log = _git("git log --since=24.hours --pretty=format:%s")
    commits = [c for c in log.splitlines() if c and "[skip ci]" not in c]

    pending = []
    try:
        ledger = json.loads(open("audit/patch_ledger.json").read())
        pending = [p["id"] for p in ledger.get("patches", []) if p.get("status") in ("pending", "partial")]
    except Exception:
        pass

    brief = compose_brief(today, commits, pending)
    print(json.dumps(brief))
    return 0


if __name__ == "__main__":
    sys.exit(main())
