#!/usr/bin/env python3
"""
sl.py — Star Log generator. SL = Star Log.
Filename: STARLOG-{date}-{time}-{type}-{stream}-{title-slug}.md
Always timestamped. Always sortable. Always groupable.

Usage:
  python3 scripts/sl.py --session-start
  python3 scripts/sl.py --session-close "What happened"
  python3 scripts/sl.py --sync-tasks
  python3 scripts/sl.py -b "Did X and Y"
  python3 scripts/sl.py -t BUILD -b "Shipped Z" --commit

Cross-session persistence:
  StarLogs are committed to git (source of truth).
  .openhands/task_tracker.json is session-local (not committed).
  --session-start: sync tracker from last committed StarLog.
  --session-close: write + commit final StarLog, then re-sync tracker for next session.
"""
from __future__ import annotations
import argparse, json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STARS_DIR = ROOT / "audit" / "starlogs"
STARS_DIR.mkdir(parents=True, exist_ok=True)
TRACKER_PATH = ROOT / ".openhands" / "task_tracker.json"
TRACKER_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_TYPES = [
    "SESSION_SNAPSHOT", "DECISION", "RESEARCH", "BUILD",
    "GOVERNANCE", "ARCHITECTURAL_CHANGE", "IDENTITY_EVENT", "IDEA", "CONVERSATION",
]

def now():
    return datetime.now(timezone.utc)

def slug(text):
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"^-|-$", "", s)
    return s[:48] or "entry"

def make_filename(ts, log_type, stream, title):
    date = ts.strftime("%Y-%m-%d")
    time = ts.strftime("%H%M%S")
    suff = f"-{slug(title)}" if title else ""
    return f"STARLOG-{date}-{time}-{log_type}-{stream}{suff}.md"

def last_star_log(prefer_with_tasks=True):
    """Return most recent StarLog. If prefer_with_tasks=True (default), prefer
    the most recent log that actually contains tasks over the newest file."""
    logs = sorted(STARS_DIR.glob("STARLOG-*.md"), reverse=True)
    if not logs:
        return None
    if not prefer_with_tasks:
        return logs[0]
    # Try newest first, fall back to older ones that have task content
    for log in logs:
        tasks = parse_tasks(log)
        if tasks:
            return log
    return logs[0]  # all empty, return newest anyway

def parse_tasks(path):
    text = path.read_text()
    # Match the task fence: opening ```, content, closing ```
    # Use greedy .* between fences so we capture the full block
    # (non-greedy .*? would stop at first ``` inside the content)
    m = re.search(r"```\n(.*)\n```", text, re.DOTALL)
    if not m:
        return []
    icon_map = {"●": "done", "◐": "in_progress", "○": "todo"}
    tasks = []
    for line in m.group(1).strip().splitlines():
        line = line.strip()
        if not line or line.startswith("*"):
            continue
        # Guard: line must be long enough and start with a known icon
        if len(line) < 3 or line[0] not in icon_map:
            continue
        icon = line[0]
        rest = line[2:].strip()
        tokens = rest.split()
        if not tokens:
            continue
        # Last token is status (strip trailing period)
        status = icon_map.get(icon, "todo")
        title = " ".join(tokens[:-1]) if len(tokens) > 1 else tokens[0]
        tasks.append({"title": title, "status": status, "notes": ""})
    return tasks

def write_tracker(tasks):
    TRACKER_PATH.write_text(json.dumps({"tasks": tasks}, indent=2))

def read_tracker():
    if not TRACKER_PATH.exists():
        return []
    return json.loads(TRACKER_PATH.read_text()).get("tasks", [])

def sync_tasks():
    log = last_star_log()
    if log:
        tasks = parse_tasks(log)
        write_tracker(tasks)
        print(f"Synced {len(tasks)} tasks from {log.name}")
    else:
        print("No StarLog found — tracker empty")
        write_tracker([])

def task_summary():
    tasks = read_tracker()
    if not tasks:
        return "*No task tracker found*"
    lines = []
    for t in tasks:
        icon = {"todo": "○", "in_progress": "◐", "done": "●"}.get(t.get("status", "○"), "○")
        note = t.get("notes", "").split(".")[0] if t.get("notes", "") else ""
        title = t.get("title", "")
        lines.append(f"{icon} {title} {note}")
    return "\n".join(lines)

def task_count():
    tasks = read_tracker()
    if not tasks:
        return "0 tasks"
    done = sum(1 for t in tasks if t.get("status") == "done")
    wip  = sum(1 for t in tasks if t.get("status") == "in_progress")
    todo = sum(1 for t in tasks if t.get("status") == "todo")
    return f"● {done} done · ◐ {wip} in_progress · ○ {todo} open"

def build_log(brief, log_type, title, tasks_summary, stream):
    ts = now()
    nav = task_count() if tasks_summary else ""
    stardate = ts.strftime("%Y.%j")
    body = [
        f"## Star Log — {ts.isoformat()}",
        f"**Stardate:** {stardate}  ·  **Type:** {log_type}  ·  **Stream:** {stream}",
        "",
        "### Summary",
        brief, "",
    ]
    if tasks_summary:
        body += ["### Tasks", f"*{nav}*", "", "```", task_summary(), "```", ""]
    body += ["---", "*Generated by sl.py · audit/starlogs/*"]
    return "\n".join(body)

def commit(paths, msg):
    for p in paths:
        subprocess.run(["git", "-C", str(ROOT), "add", str(p)], check=True)
    r = subprocess.run(
        ["git", "-C", str(ROOT), "commit", "-m", msg, "--allow-empty"],
        check=False, capture_output=True, text=True
    )
    if r.returncode and "nothing to commit" not in r.stderr.lower():
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()

def main():
    p = argparse.ArgumentParser(description="SL — Star Log generator")
    p.add_argument("--session-start", action="store_true")
    p.add_argument("--session-close", "-x", metavar="TEXT")
    p.add_argument("--sync-tasks", action="store_true")
    p.add_argument("--brief", "-b", metavar="TEXT")
    p.add_argument("--type", "-t", default="SESSION_SNAPSHOT", choices=LOG_TYPES)
    p.add_argument("--no-tasks", action="store_true")
    p.add_argument("--stream", "-s", default="jarvis-ayre")
    p.add_argument("--commit", "-c", metavar="MSG")
    p.add_argument("--stardate", action="store_true")
    args = p.parse_args()

    if args.stardate:
        print(now().strftime("%Y.%j"))
        return
    if args.session_start or args.sync_tasks:
        sync_tasks()
        return

    ts = now()
    brief = args.brief or ""

    if args.session_close:
        path = STARS_DIR / make_filename(ts, args.type, args.stream, args.session_close)
        path.write_text(build_log(args.session_close, args.type, args.session_close,
                                  not args.no_tasks, args.stream))
        print(f"Wrote: {path}")
        sha = commit([path], f"chore(audit): SL — session close {ts.date()}")
        print(f"Committed: {sha.strip()}")
        sync_tasks()
        return

    path = STARS_DIR / make_filename(ts, args.type, args.stream, brief)
    path.write_text(build_log(brief, args.type, brief, not args.no_tasks, args.stream))
    print(f"Wrote: {path}")
    if args.commit:
        sha = commit([path], f"chore(audit): SL — {args.commit}")
        print(f"Committed: {sha.strip()}")

if __name__ == "__main__":
    main()
