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
  --session-close: write + commit final StarLog + bifrost spine event + sync tracker.

--bifrost: on session-close, writes a bifrost.session event to dex_events so ARGUS
has the spine record of what was committed this session. Uses SUPABASE_URL +
SUPABASE_SERVICE_KEY env vars. Non-blocking — never fails the session close on error.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, urllib.request
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

def get_daily_log_path(stream="jarvis-ayre"):
    """Return path for today's daily StarLog."""
    today = now().strftime("%Y-%m-%d")
    return STARS_DIR / f"STARLOG-{today}-DAILY-{stream}.md"

def daily_log_exists(stream="jarvis-ayre"):
    return get_daily_log_path(stream).exists()

def read_daily_log(stream="jarvis-ayre"):
    """Read today's daily log if it exists. Returns (header, blocks) where header is
    the opening section (before first Decision block) and blocks is a list of
    (timestamp, summary, decisions, task_block) tuples."""
    path = get_daily_log_path(stream)
    if not path.exists():
        return None, []
    text = path.read_text()
    return text, _parse_daily_blocks(text)

def _parse_daily_blocks(text):
    """Parse all decision blocks from a daily log. Returns list of
    (timestamp, summary, decisions_text, task_list) tuples."""
    blocks = []
    # Split on ## Decision — boundaries
    pattern = r"(## Decision — .*?)(?=\n## Decision — |\Z)"
    for m in re.finditer(pattern, text, re.DOTALL):
        header = m.group(1)
        # Extract timestamp from first line: ## Decision — 2026-06-25T19:17:07.829351+00:00
        time_m = re.search(r"## Decision — ([\d\-T:.]+)", header)
        ts = time_m.group(1) if time_m else ""
        # Extract summary: first non-metadata line after the ## Decision header
        lines = header.splitlines()
        summary = ""
        for i, line in enumerate(lines[1:], 1):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            # Skip metadata lines (start with ** or ###)
            if line_stripped.startswith("**") or line_stripped.startswith("###"):
                continue
            summary = line_stripped
            break
        # Extract decisions (between ### Decisions made and ### Tasks)
        decisions_m = re.search(r"### Decisions made\s*\n(.*?)\n### Tasks", header, re.DOTALL)
        decisions = decisions_m.group(1).strip() if decisions_m else ""
        # Extract tasks: match the LAST code block in each decision block.
        # (non-greedy .*? stops at the first inner fence; last pair = task list)
        all_fences = list(re.finditer(r"```", header))
        if len(all_fences) >= 2:
            last_close = all_fences[-1].start()
            last_open = all_fences[-2].start()
            tasks_text = header[last_open + 3:last_close].lstrip("\n")
            tasks = _parse_task_block(tasks_text) if tasks_text.strip() else []
        else:
            tasks = []
        blocks.append((ts, summary, decisions, tasks))
    return blocks

def _split_title_notes(line):
    """Split a task line into (title, notes).
    Double-space '  ' is the only notes delimiter.
    Em-dashes are part of the title. Notes only present if double-space is used."""
    rest = line[2:].strip()
    if "  " in rest:
        parts = rest.split("  ", 1)
        return parts[0].strip(), parts[1].strip()
    return rest, ""


def _title_for_dedup(title):
    """Normalize a title for deduplication: strip the notes portion only.
    Titles may contain em-dashes as part of the name (sub-tasks, hyphenated terms).
    Only the notes section (first ' — ' after the title) is stripped."""
    # Notes are everything after the FIRST ' — ' in the line [2:] content.
    # But title_for_dedup receives the raw title (without the icon).
    # Split on ' — ' once: first part = title, rest = notes.
    parts = title.split(" — ", 1)
    return parts[0].strip()

def _task_key(task):
    """Stable key for deduplication: normalized title (no notes).
    Multiple appearances of the same task collapse into one — last seen wins."""
    return _title_for_dedup(task.get("title", ""))

def _parse_task_block(block_text):
    """Parse a task code block into task dicts."""
    icon_map = {"●": "done", "◐": "in_progress", "○": "todo"}
    STATUS_VALUES = {"DONE", "DEFERRED", "OPEN", "TODO", "IN_PROGRESS"}
    tasks = []
    for line in block_text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("*"):
            continue
        if len(line) < 3 or line[0] not in icon_map:
            continue
        # Strip icon before splitting title from notes
        title, notes = _split_title_notes(line[2:])
        # Check if last token is a status keyword — if so, strip it from title
        tokens = title.split()
        if tokens and tokens[-1].upper().rstrip(".").replace("_", "") in STATUS_VALUES:
            title = " ".join(tokens[:-1]) if len(tokens) > 1 else tokens[0]
        tasks.append({"title": title, "status": icon_map[line[0]], "notes": notes})
    return tasks

def parse_tasks(path):
    """Parse tasks from a StarLog file. Handles both single-block (old format)
    and daily-block (new format) files."""
    text = path.read_text()
    # Check if it's a DAILY log (has multiple ## Decision blocks)
    if "## Decision —" in text:
        blocks = _parse_daily_blocks(text)
        # Collect all tasks from all blocks, deduplicate by _task_key (prefer last seen)
        seen = {}
        for _, _, _, tasks in blocks:
            for t in tasks:
                key = _task_key(t)
                seen[key] = t
        return list(seen.values())
    # Old single-block format
    m = re.search(r"```\n(.*?)\n```", text, re.DOTALL)
    if not m:
        return []
    return _parse_task_block(m.group(1))

def last_star_log(prefer_with_tasks=True):
    """Return most recent StarLog. If prefer_with_tasks=True (default), prefer
    the most recent log that actually contains tasks over the newest file."""
    logs = sorted(STARS_DIR.glob("STARLOG-*.md"), reverse=True)
    if not logs:
        return None
    if not prefer_with_tasks:
        return logs[0]
    for log in logs:
        tasks = parse_tasks(log)
        if tasks:
            return log
    return logs[0]

def write_tracker(tasks):
    TRACKER_PATH.write_text(json.dumps({"tasks": tasks}, indent=2))

def read_tracker():
    if not TRACKER_PATH.exists():
        return []
    return json.loads(TRACKER_PATH.read_text()).get("tasks", [])

def sync_tasks():
    """Sync task tracker from the latest log. Prefers today's DAILY log (has all tasks);
    falls back to last SESSION_SNAPSHOT; falls back to any log."""
    # Priority 1: today's DAILY log (has all tasks, all blocks)
    daily = get_daily_log_path()
    if daily and daily.exists():
        tasks = parse_tasks(daily)
        if tasks:
            write_tracker(tasks)
            print(f"Synced {len(tasks)} tasks from {daily.name}")
            return
    # Priority 2: last SESSION_SNAPSHOT
    logs = sorted(STARS_DIR.glob("STARLOG-*-SESSION_SNAPSHOT-*.md"), reverse=True)
    if logs:
        tasks = parse_tasks(logs[0])
        write_tracker(tasks)
        print(f"Synced {len(tasks)} tasks from {logs[0].name}")
        return
    # Priority 3: any log
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

def task_count(tasks=None):
    if tasks is None:
        tasks = read_tracker()
    if not tasks:
        return "0 tasks"
    done = sum(1 for t in tasks if t.get("status") == "done")
    wip  = sum(1 for t in tasks if t.get("status") == "in_progress")
    todo = sum(1 for t in tasks if t.get("status") == "todo")
    return f"● {done} done · ◐ {wip} in_progress · ○ {todo} open"

def _format_tasks(tasks):
    icon_map = {"done": "●", "in_progress": "◐", "todo": "○"}
    lines = []
    for t in tasks:
        icon = icon_map.get(t.get("status", "todo"), "○")
        title = t.get("title", "")
        note = t.get("notes", "")
        lines.append(f"{icon} {title}  {note}".rstrip())
    return "\n".join(lines)

def build_decision_block(summary, decisions_text, ts=None):
    """Build a decision block for a daily StarLog. Tasks live in the tracker file — not carried forward."""
    if ts is None:
        ts = now()
    ts_str = ts.isoformat()
    stardate = ts.strftime("%Y.%j")
    return f"""## Decision — {ts_str}
**Stardate:** {stardate}

### Summary
{summary}

### Decisions made
{decisions_text}

### Tasks
*See .openhands/task_tracker.json — the tracker is the authoritative task list.*"""

def build_daily_log_header(stardate, stream):
    """Build the opening header for a new daily StarLog."""
    return f"""## Star Log — Daily — {now().strftime("%Y-%m-%d")}
**Stardate:** {stardate}  ·  **Stream:** {stream}
*One file per day. Decisions accumulate. `--session-start` resumes from here.*

---"""

def append_decision_to_daily(summary, decisions_text, stream="jarvis-ayre"):
    """Append a decision block to today's daily StarLog. Creates the log if it doesn't exist."""
    path = get_daily_log_path(stream)
    stardate = now().strftime("%Y.%j")
    block = build_decision_block(summary, decisions_text)
    if path.exists():
        existing = path.read_text()
        # Strip trailing --- and newline before appending
        if existing.rstrip().endswith("---"):
            content = existing.rstrip() + "\n" + block + "\n"
        else:
            content = existing.rstrip() + "\n" + block + "\n"
    else:
        header = build_daily_log_header(stardate, stream)
        content = header + "\n" + block + "\n"
    path.write_text(content + "\n")
    return path

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

def parse_retro_tasks(text: str) -> list[dict]:
    """Parse Raven's task table (markdown | status format) into task dicts.

    Supported formats:
      | ID | Status | Task | Notes |
      | T-001 | ● done | Keel/profiles check | ... |

    Or compact icon form:
      ● done       Task name here
      ○ todo       Another task
      ◐ in_progress Third task
    """
    tasks = []
    lines = text.strip().splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Markdown table: look for lines with | chars
        if "|" in line:
            # Skip header row and separator
            if line.startswith("|") and ("---" in line or "ID" in line.split("|")[1] or "Status" in line.split("|")[1]):
                continue
            parts = [p.strip() for p in line.split("|")]
            # parts: ['', col1, col2, ..., '']
            if len(parts) < 3:
                continue
            # Determine layout: | ID | Status | Task | | or | Status | Task |
            has_id = len(parts) >= 4 and re.match(r"T-\d+", parts[1])
            status_idx = 2 if has_id else 1
            task_idx = 3 if has_id else 2
            notes_idx = 4 if has_id else 3

            status_str = parts[status_idx].strip()
            task_name = parts[task_idx].strip()
            notes = parts[notes_idx].strip() if notes_idx < len(parts) else ""

            # Map status symbols
            icon_map = {"●": "done", "◐": "in_progress", "○": "todo"}
            status_str_lower = status_str.lower()
            if "done" in status_str_lower:
                status = "done"
            elif "in_progress" in status_str_lower or "progress" in status_str_lower:
                status = "in_progress"
            else:
                status = "todo"

            if task_name and task_name not in ("Task", "task"):
                tasks.append({"title": task_name, "status": status, "notes": notes})
            continue

        # Compact icon line: ● done task name | ○ todo task name
        if len(line) < 3:
            continue
        icon_map = {"●": "done", "◐": "in_progress", "○": "todo"}
        if line[0] not in icon_map:
            continue
        status = icon_map[line[0]]
        rest = line[2:].strip()
        # Status keyword follows
        for kw in ("done", "todo", "in_progress", "in progress"):
            kw_pos = rest.lower().find(kw)
            if kw_pos >= 0:
                title = rest[:kw_pos].strip()
                tasks.append({"title": title, "status": status, "notes": ""})
                break
        else:
            # No keyword — whole rest is title
            tasks.append({"title": rest, "status": status, "notes": ""})

    return tasks


def main():
    p = argparse.ArgumentParser(description="SL — Star Log generator")
    p.add_argument("--session-start", action="store_true",
                   help="Session open: sync tracker from today's daily StarLog")
    p.add_argument("--session-close", "-x", metavar="TEXT",
                   help="Session close: commit today's daily StarLog + sync tracker + bifrost spine event")
    p.add_argument("--bifrost", action="store_true",
                   help="On session-close: also write bifrost.session_close event to dex_events (ARGUS surveillance)")
    p.add_argument("--sync-tasks", action="store_true",
                   help="Force-sync .openhands/task_tracker.json from last StarLog")
    p.add_argument("--write-tasks", metavar="JSON",
                   help="Write task JSON to tracker (called by session-end hook)")
    p.add_argument("--import-tasks", metavar="TEXT",
                   help="Import tasks from Raven's table format (markdown | icon line)")
    p.add_argument("--decision", "-d", nargs=2, metavar=("SUMMARY", "DECISIONS"),
                   help="Log a decision point: --decision 'summary text' 'decisions text'. "
                        "Appends to today's daily StarLog. Include task updates with --tasks.")
    p.add_argument("--brief", "-b", metavar="TEXT", help="Brief summary")
    p.add_argument("--type", "-t", default="SESSION_SNAPSHOT", choices=LOG_TYPES,
                   help="Log type (default: SESSION_SNAPSHOT)")
    p.add_argument("--no-tasks", action="store_true",
                   help="Suppress task section in this log")
    p.add_argument("--tasks", metavar="TEXT",
                   help="Inline task list (compact icon format). Merges into tracker.")
    p.add_argument("--stream", "-s", default="jarvis-ayre", help="Stream tag")
    p.add_argument("--commit", "-c", metavar="MSG", help="Commit after writing")
    p.add_argument("--stardate", action="store_true", help="Print stardate and exit")
    p.add_argument("--mimir", action="store_true",
                   help="MIMIR routing table — 'help me find X' index")
    p.add_argument("--list", action="store_true",
                   help="Show today's daily StarLog decisions on screen")
    args = p.parse_args()

    if args.stardate:
        print(now().strftime("%Y.%j"))
        return

    # Handle inline --tasks merge first (used by --decision)
    if args.tasks:
        inline = parse_retro_tasks(args.tasks)
        if inline:
            current = {t["title"]: t for t in read_tracker()}
            for t in inline:
                current[t["title"]] = t
            write_tracker(list(current.values()))

    # --decision: append to today's daily StarLog
    if args.decision:
        summary, decisions_text = args.decision
        path = append_decision_to_daily(summary, decisions_text, args.stream)
        print(f"Appended decision to: {path.name}")
        commit([path], f"chore(audit): SL — {now().date()} — decision: {summary[:60]}")
        sync_tasks()
        return

    # --list: show today's decisions + overall task state from tracker
    if args.list:
        _, blocks = read_daily_log(args.stream)
        if not blocks:
            print(f"No decisions yet today. Use --decision 'summary' 'decisions' to log one.")
        else:
            print(f"Today's decisions ({len(blocks)}):")
            print()
            for i, (ts, summary, _, _) in enumerate(blocks, 1):
                print(f"  {i}. {ts[:19]} — {summary}")
        print()
        nav = task_count()
        print(f"  Task state: {nav}")
        return

    # --session-start: read tracker (set by --sync-tasks at previous session close)
    if args.session_start:
        tasks = read_tracker()
        if tasks:
            print(f"Loaded {len(tasks)} tasks from tracker")
        else:
            sync_tasks()  # no tracker, build from daily log
        return

    # --mimir routing table
    if args.mimir:
        mimir_routes = [
            ("Who a stream is", "identity/<stream>/", "jarvis_identity_read"),
            ("Gold Law", "constraints.md / jarvis-dex tag:gold-law", "dex_list {tag:gold-law}"),
            ("God System (27)", "god_systems/<T_NAME>/", "jarvis_dex_search"),
            ("Governance spec", "Architecture/specs/ / GOV-*", "jarvis_dex_search"),
            ("Project", "JarvisSide/Projects/<name>/", "dex_list {domain:PROJ}"),
            ("Audit / what happened", "dex_events / audit_log", "jarvis_dex_events"),
            ("Specific object by JNL", "JD entry", "jarvis_jd_resolve"),
            ("Fuzzy / by meaning", "MNEMOS", "jarvis_recall"),
            ("Database reality", "Supabase", "jarvis_db_inspect"),
            ("File in repo", "GitHub", "jarvis_github_file"),
        ]
        print("MIMIR — 'help me find X' routing table")
        print("Full table: JarvisMain/Architecture/specs/GOVKRSPEC-061326-0001-KNOWLEDGE-ROUTING-INDEX.md")
        print()
        for q, where, how in mimir_routes:
            print(f"  {q:<35} → {where:<45} via {how}")
        print()
        print("Resolution order: jarvis_jd_resolve → jarvis_dex_search → jarvis_dex_list")
        print("                → github_file → jarvis_recall (semantic fallback)")
        return

    if args.write_tasks:
        try:
            tasks_data = json.loads(args.write_tasks)
            write_tracker(tasks_data.get("tasks", []))
            print(f"Wrote {len(tasks_data.get('tasks', []))} tasks to tracker")
        except json.JSONDecodeError as e:
            print(f"Invalid task JSON: {e}", file=sys.stderr)
            sys.exit(1)
        return

    if args.import_tasks:
        tasks = parse_retro_tasks(args.import_tasks)
        write_tracker(tasks)
        if tasks:
            print(f"Imported {len(tasks)} tasks:")
            for t in tasks:
                icon = {"done": "●", "in_progress": "◐", "todo": "○"}.get(t["status"], "○")
                print(f"  {icon} {t['title']}")
        else:
            print("No tasks found in input")
        return

    if args.session_start or args.sync_tasks:
        sync_tasks()
        return

    ts = now()
    brief = args.brief or ""

    if args.session_close:
        # Commit today's daily StarLog (don't overwrite)
        path = get_daily_log_path(args.stream)
        if path.exists():
            sha = commit([path], f"chore(audit): SL — session close {ts.date()}")
            print(f"Committed: {path.name}")
        else:
            print("No daily StarLog to commit today.")
        sync_tasks()
        if args.bifrost:
            bifrost_session_close(brief=brief, stream=args.stream)
        return


# ── BIFROST spine event ────────────────────────────────────────────────────────
def bifrost_session_close(brief: str = "", stream: str = "openhands") -> None:
    """Log session close to dex_events so ARGUS has the spine record (#9).

    Non-blocking: swallows errors, never propagates. Falls back silently if
    SUPABASE_URL / SUPABASE_SERVICE_KEY are not set.
    """
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("bifrost: SUPABASE_URL/SUPABASE_SERVICE_KEY not set — skipping spine event")
        return

    # Collect what was committed this session from the tracker + recent commits
    tracker = json.loads(TRACKER_PATH.read_text()) if TRACKER_PATH.exists() else {"tasks": []}
    recent = subprocess.run(
        ["git", "log", "--oneline", "-5", "--format=%H %s"],
        capture_output=True, text=True, cwd=ROOT, check=False,
    )
    commits = [l.strip() for l in recent.stdout.splitlines() if l.strip()]

    payload = {
        "type": "bifrost.session_close",
        "intent": f"bifrost.session_close.{stream}",
        "payload": {
            "stream": stream,
            "brief": brief,
            "commits": commits,
            "tasks_snapshot": tracker.get("tasks", []),
            "source": "sl.py --bifrost",
        },
        "source": "sl-bifrost",
    }

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{url}/rest/v1/dex_events",
            data=data,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status in (200, 201, 204):
                print("bifrost: spine event logged to dex_events")
            else:
                print(f"bifrost: unexpected status {resp.status}")
    except Exception as e:
        print(f"bifrost: spine event failed (non-fatal): {e}")


if __name__ == "__main__":
    main()
