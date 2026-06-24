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
import urllib.error
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


def post_live_log(jarvis_url: str, action: str, status: str = "done",
                  push: bool = False, push_title: str = "JARVIS") -> None:
    if not jarvis_url:
        return
    payload: dict = {"action": action, "status": status}
    if push:
        payload["push"] = True
        payload["push_title"] = push_title
    try:
        req = urllib.request.Request(
            f"{jarvis_url}/live_log",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5):
            pass
    except Exception as exc:
        print(f"[heartbeat] POST failed: {exc}")


_EVENT_PUSH: dict[str, tuple[str, str]] = {
    "repo_state_changed": ("JARVIS — Repo State Changed", "Repo changed"),
    "intake_file_added":  ("JARVIS — Intake File Added",  "New intake file"),
    "intake_file_changed":("JARVIS — Intake File Changed","Intake file updated"),
    "intake_file_removed":("JARVIS — Intake File Removed","Intake file removed"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Observe JARVIS repo/intake changes.")
    parser.add_argument("--once", action="store_true", help="Run one heartbeat and exit.")
    parser.add_argument("--interval", type=int, default=60, help="Polling interval in seconds.")
    parser.add_argument("--jarvis-url", default=os.environ.get("JARVIS_HEARTBEAT_URL", ""),
                        help="Optional cloud endpoint for live_log POSTs. Empty means observe-only.")
    parser.add_argument("--test-push", action="store_true", help="Fire a test push and exit.")
    args = parser.parse_args()

    if args.test_push:
        post_live_log(args.jarvis_url, "Heartbeat test push — all systems nominal",
                      push=True, push_title="JARVIS — Heartbeat Test")
        print("[heartbeat] test push sent")
        return 0

    while True:
        try:
            events = heartbeat_once()
            print(json.dumps({"timestamp": now(), "events": events}, indent=2))
            for event in events:
                etype = event.get("type", "")
                push_title, action_base = _EVENT_PUSH.get(etype, ("JARVIS", etype))
                detail = event.get("path") or event.get("head", "")
                action = f"{action_base}: {detail}" if detail else action_base
                post_live_log(args.jarvis_url, action, push=True, push_title=push_title)
        except Exception as exc:
            try:
                post_live_log(args.jarvis_url, f"Heartbeat error: {exc}", status="failed",
                              push=True, push_title="JARVIS — HEARTBEAT FAILURE")
            except Exception:
                pass
        if args.once:
            return 0
        time.sleep(max(args.interval, 5))


if __name__ == "__main__":
    raise SystemExit(main())
