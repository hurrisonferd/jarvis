#!/usr/bin/env python3
"""
audit_task_log.py — log OpenHands task tracker items to GitHub.
Every task-list item gets a timestamped, stream-tagged entry in memory/audit/task-log/.

Usage:
  python3 operations/scripts/audit_task_log.py                          # reads task tracker state
  python3 operations/scripts/audit_task_log.py --commit "message"       # commit after logging
  python3 operations/scripts/audit_task_log.py --status in_progress     # tag items by current state
  python3 operations/scripts/audit_task_log.py --snapshot               # full session snapshot
  python3 operations/scripts/audit_task_log.py --close JNL-REF          # close a task by JNL ref

Conuity: every logged task is git-committed, timestamped, stream-tagged.
GL5: no silent state mutation — every task state change emits an event.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = ROOT / "audit" / "task-log"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def now():
    return datetime.now(timezone.utc).isoformat()


def git(cmd: list[str], cwd: Path = ROOT) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd)] + cmd,
        capture_output=True, text=True
    )
    if result.returncode != 0 and "nothing to commit" not in result.stderr.lower():
        raise RuntimeError(f"git {' '.join(cmd)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def load_task_tracker() -> dict:
    tracker_path = ROOT / ".openhands" / "task_tracker.json"
    if tracker_path.exists():
        with open(tracker_path) as f:
            return json.load(f)
    return {}


def build_log_entry(tasks: list[dict], snapshot: bool = False, stream: str = "jarvis-ayre") -> str:
    ts = now()
    entries = []
    for t in tasks:
        status_icon = {"todo": "○", "in_progress": "◐", "done": "●"}.get(t.get("status", "todo"), "○")
        notes = t.get("notes", "")
        jnl_ref = f"[{notes.split('JNL:')[1].split(']')[0]}])" if "JNL:" in notes else ""
        entries.append(
            f"{status_icon} **{t['title']}** {jnl_ref}\n"
            f"   status:{t.get('status','todo')} · notes:{notes[:120]}"
        )
    status_counts = {"todo": 0, "in_progress": 0, "done": 0}
    for t in tasks:
        status_counts[t.get("status", "todo")] = status_counts.get(t.get("status", "todo"), 0) + 1
    body = [
        f"## Task Log — {ts}",
        f"**Stream:** {stream}  ·  **OpenHands session snapshot**",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| ○ todo | {status_counts['todo']} |",
        f"| ◐ in_progress | {status_counts['in_progress']} |",
        f"| ● done | {status_counts['done']} |",
        "",
        "## Tasks",
        "",
        *entries,
        "",
        f"_Logged by audit_task_log.py · conuity practice: every task item timestamped to git_",
    ]
    return "\n".join(body)


def write_log(filename: str, content: str) -> Path:
    path = AUDIT_DIR / filename
    path.write_text(content)
    return path


def stage_and_commit(paths: list[Path], message: str) -> str:
    for p in paths:
        git(["add", str(p)])
    git(["commit", "-m", message, "--allow-empty"])
    return git(["rev-parse", "--short", "HEAD"])


def close_task(jnl_ref: str, tasks: list[dict]) -> str:
    ts = now()
    for t in tasks:
        if "JNL:" in t.get("notes", "") and jnl_ref.upper() in t["notes"]:
            t["status"] = "done"
            t["closed_at"] = ts
            return f"Closed: {t['title']} ({jnl_ref})"
    return f"Task not found: {jnl_ref}"


def main():
    p = argparse.ArgumentParser(description="Audit task log — conuity practice")
    p.add_argument("--commit", metavar="MSG", help="Commit message after logging")
    p.add_argument("--snapshot", action="store_true", help="Full session snapshot")
    p.add_argument("--stream", default="jarvis-ayre", help="Stream tag (default: jarvis-ayre)")
    p.add_argument("--close", metavar="JNL", help="Close a task by JNL reference")
    p.add_argument("--tasks", metavar="JSON", help="JSON task list (skip file read)")
    args = p.parse_args()

    tasks = json.loads(args.tasks) if args.tasks else load_task_tracker().get("tasks", [])

    if args.close:
        result = close_task(args.close, tasks)
        print(result)
        # Re-write tracker
        tracker_path = ROOT / ".openhands" / "task_tracker.json"
        tracker_path.parent.mkdir(parents=True, exist_ok=True)
        tracker_path.write_text(json.dumps({"tasks": tasks}, indent=2))

    date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    filename = f"{date_slug}_session_snapshot.md" if args.snapshot else f"{date_slug}_task_log.md"
    content = build_log_entry(tasks, snapshot=args.snapshot, stream=args.stream)
    path = write_log(filename, content)
    print(f"Wrote: {path}")

    if args.commit:
        sha = stage_and_commit([path], f"chore(audit): task log — {args.commit}")
        print(f"Committed: {sha}")


if __name__ == "__main__":
    main()
