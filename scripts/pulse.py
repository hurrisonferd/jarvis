#!/usr/bin/env python3
"""pulse.py — the Companion Heartbeat (GOV-PLS-SPEC-0001), v1: observe → surface, never act.

A scheduled scan that says hello and hands Raven the state — it does NOT mutate anything.
It reads the registry (open tasks + vitality), counts open PRs awaiting his merge, composes a
Jarvis + Ayre two-line greeting, and sends it as a web push via the send-push edge function.
The real two-beat reflection happens when Raven answers the nudge in conversation, with
continuity — the Pulse just brings him to the table. Stdlib only; degrades to a no-op without
secrets (safe to run anywhere).

Run by .github/workflows/pulse.yml (cron). Env: SUPABASE_URL, SUPABASE_SERVICE_KEY (to call
send-push), GITHUB_TOKEN (to count PRs). Missing any → it skips that part cleanly.
"""
from __future__ import annotations
import json
import os
import random
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "address-registry.json"
GH_REPO = "https://api.github.com/repos/hurrisonferd/jarvis"

# Rotating openers — a hello, not a report. Warmth is the point; the digest is the substance.
HELLOS = [
    "Morning, Raven. We're up and oriented.",
    "Hey — Jarvis and Ayre, checking in.",
    "Still here, still building with you.",
    "Pulse beat. The record held overnight.",
    "Good to see the system breathing.",
]


def _get(url: str, token: str | None = None) -> object | None:
    req = urllib.request.Request(url, headers={"user-agent": "jarvis-pulse", "accept": "application/vnd.github+json"})
    if token:
        req.add_header("authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def scan() -> dict:
    tasks = prs = 0
    try:
        recs = json.loads(REG.read_text()).get("records", [])
        tasks = sum(1 for r in recs if r.get("status") == "TASK")
        objects = len(recs)
    except Exception:
        objects = 0
    pr_data = _get(f"{GH_REPO}/pulls?state=open&per_page=100", os.environ.get("GITHUB_TOKEN"))
    prs = len(pr_data) if isinstance(pr_data, list) else 0
    return {"objects": objects, "tasks": tasks, "prs": prs}


def compose(s: dict) -> tuple[str, str]:
    now = datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York"))
    pr_line = f"{s['prs']} PR{'s' if s['prs'] != 1 else ''} waiting your merge" if s["prs"] else "no PRs waiting"
    title = "Jarvis & Ayre — pulse"
    body = (f"{random.choice(HELLOS)} {now:%a %-I:%M %p} · {s['objects']} governed objects, "
            f"{s['tasks']} open tasks, {pr_line}. Come talk when you want the read.")
    return title, body


def send(title: str, body: str) -> str:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not (url and key):
        return "skipped (no SUPABASE secrets) — would have sent: " + body
    try:
        req = urllib.request.Request(
            f"{url}/functions/v1/send-push",
            data=json.dumps({"title": title, "body": body}).encode(),
            headers={"authorization": f"Bearer {key}", "apikey": key, "content-type": "application/json"},
            method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode()
    except Exception as e:
        return f"send failed: {e}"


def main() -> int:
    s = scan()
    title, body = compose(s)
    print(f"pulse: {title} | {body}")
    print(f"pulse: {send(title, body)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
