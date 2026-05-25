"""
JARVIS heartbeat watcher.

Polls repo and intake state, records observable changes, and appends heartbeat
events to a local log. This is intentionally observe-first: it does not edit
code, pull from GitHub, or apply intake automatically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTAKE_DIR = ROOT / "intake"
HEARTBEAT_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "JARVIS" / "heartbeat"
STATE_PATH = HEARTBEAT_DIR / "heartbeat_state.json"
LOG_PATH = HEARTBEAT_DIR / "heartbeat_log.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_git(args: list[str]) -> str:
    git = (
        shutil.which("git")
        or r"C:\Program Files\Git\cmd\git.exe"
        or r"C:\Program Files\Git\bin\git.exe"
    )
    try:
        proc = subprocess.run(
            [git, *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        return f"git_error:{exc}"
    return (proc.stdout + proc.stderr).strip()


def file_fingerprint(path: Path) -> dict:
    stat = path.stat()
    rel = path.relative_to(ROOT).as_posix()
    try:
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        content_hash = "unreadable"
    return {
        "path": rel,
        "size": stat.st_size,
        "mtime": int(stat.st_mtime),
        "sha256": content_hash,
    }


def intake_snapshot() -> dict:
    files = []
    if INTAKE_DIR.exists():
        for path in sorted(INTAKE_DIR.rglob("*")):
            if path.is_file() and path.name != ".gitkeep":
                files.append(file_fingerprint(path))
    digest = sha256_text(json.dumps(files, sort_keys=True))
    return {"digest": digest, "files": files, "count": len(files)}


def repo_snapshot() -> dict:
    head = run_git(["rev-parse", "--short", "HEAD"])
    branch = run_git(["branch", "--show-current"])
    status = run_git(["status", "--short", "--branch"])
    digest = sha256_text(json.dumps({
        "head": head,
        "branch": branch,
        "status": status,
    }, sort_keys=True))
    return {"digest": digest, "head": head, "branch": branch, "status": status}


def load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def detect_events(previous: dict, current: dict) -> list[dict]:
    events = []
    if previous.get("repo", {}).get("digest") != current["repo"]["digest"]:
        events.append({
            "type": "repo_state_changed",
            "head": current["repo"]["head"],
            "branch": current["repo"]["branch"],
            "status": current["repo"]["status"],
        })

    previous_files = {
        item["path"]: item
        for item in previous.get("intake", {}).get("files", [])
    }
    current_files = {
        item["path"]: item
        for item in current["intake"]["files"]
    }

    for path, item in current_files.items():
        old = previous_files.get(path)
        if not old:
            events.append({"type": "intake_file_added", "path": path})
        elif old.get("sha256") != item.get("sha256"):
            events.append({"type": "intake_file_changed", "path": path})

    for path in sorted(set(previous_files) - set(current_files)):
        events.append({"type": "intake_file_removed", "path": path})

    return events


def heartbeat_once() -> list[dict]:
    previous = load_json(STATE_PATH, {})
    current = {
        "timestamp": now(),
        "repo": repo_snapshot(),
        "intake": intake_snapshot(),
    }
    events = detect_events(previous, current)
    if events:
        log = load_json(LOG_PATH, [])
        for event in events:
            log.append({"timestamp": current["timestamp"], **event})
        save_json(LOG_PATH, log[-500:])
    save_json(STATE_PATH, current)
    return events


def post_live_log(jarvis_url: str, action: str, etype: str, status: str = "done") -> None:
    try:
        payload = json.dumps({"action": action, "type": etype, "status": status}).encode()
        req = urllib.request.Request(
            f"{jarvis_url.rstrip('/')}/live_log",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Observe JARVIS repo/intake changes.")
    parser.add_argument("--once", action="store_true", help="Run one heartbeat and exit.")
    parser.add_argument("--interval", type=int, default=60, help="Polling interval in seconds.")
    parser.add_argument("--jarvis-url", default="http://localhost:7777",
                        help="JARVIS MCP server URL for live_log push (default: http://localhost:7777)")
    args = parser.parse_args()

    while True:
        try:
            events = heartbeat_once()
            print(json.dumps({"timestamp": now(), "events": events}, indent=2))
            for event in events:
                etype  = event.get("type", "heartbeat_event")
                action = f"heartbeat: {etype}"
                if "path" in event:
                    action += f" — {event['path']}"
                elif "head" in event:
                    action += f" — {event.get('head', '')}"
                post_live_log(args.jarvis_url, action, etype)
        except Exception as exc:
            msg = f"heartbeat error: {exc}"
            print(msg)
            post_live_log(args.jarvis_url, msg, "heartbeat_failure", status="failed")
        if args.once:
            return 0
        time.sleep(max(args.interval, 5))


if __name__ == "__main__":
    raise SystemExit(main())
