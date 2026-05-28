#!/usr/bin/env python3
"""
SessionStart hook — JARVIS session brief.
Surfaces last session's exchanges + pending work + git state.
Replaces jarvis-session-start.sh for richer briefing.
"""
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
RECALL_FN = f"{SUPABASE_URL}/functions/v1/mnemos-recall"
LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "audit", "patch_ledger.json")

SEP = "━" * 50


def recall(payload: dict) -> list:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        RECALL_FN, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {SUPABASE_ANON}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read()).get("memories", [])
    except Exception:
        return []


def git(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""


def load_pending_patches() -> list:
    try:
        with open(LEDGER_PATH, "r") as f:
            ledger = json.load(f)
        patches = ledger.get("patches", [])
        return [p for p in patches if p.get("status") in ("partial", "pending")]
    except Exception:
        return []


def fmt_memory(m: dict) -> str:
    ts = (m.get("timestamp") or "")[:10]
    text = (m.get("text") or "")[:120].replace("\n", " ")
    return f"  [{ts}] {text}"


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    branch = git("git branch --show-current") or "unknown"
    last_commit = git("git log --oneline -1") or "—"
    recent_commits = git("git log --oneline -5") or "  (unavailable)"

    print(SEP)
    print(f"JARVIS SESSION START — {now}")
    print(f"Branch: {branch} | Last commit: {last_commit}")
    print(SEP)
    print()

    # ── Last session exchanges (speak_input + speak_output interleaved)
    speak_in  = recall({"source_type": "speak_input",  "limit": 8})
    speak_out = recall({"source_type": "speak_output", "limit": 5})
    exchanges = sorted(speak_in + speak_out, key=lambda m: m.get("timestamp") or "", reverse=True)

    if exchanges:
        print("LAST SESSION — what mattered:")
        for m in exchanges[:10]:
            print(fmt_memory(m))
        print()
    else:
        print("MNEMOS — no exchanges yet (first session or Supabase unreachable)")
        print()

    # ── Raven profile memories (emotional / identity tags)
    profile = recall({"tags": ["emotional", "identity", "mission", "family"], "limit": 3})
    if profile:
        print("RAVEN CONTEXT:")
        for m in profile:
            print(fmt_memory(m))
        print()

    # ── Active constraints (PROMETHEUS challenge layer — decision memories)
    constraints = recall({"source_type": "decision", "limit": 5})
    if constraints:
        print("ACTIVE CONSTRAINTS (challenge before acting against these):")
        for m in constraints:
            text = (m.get("text") or "")[:130].replace("\n", " ")
            print(f"  {text}")
        print()

    # ── Monitor observations (gap 3 — autonomous surface)
    monitor = recall({"source_type": "monitor", "limit": 3})
    if monitor:
        print("JARVIS OBSERVATIONS:")
        for m in monitor:
            print(fmt_memory(m))
        print()

    # ── Pending / partial patches
    pending = load_pending_patches()
    if pending:
        print("PENDING WORK:")
        for p in pending[:8]:
            status = p.get("status", "")
            remaining = p.get("remaining", [])
            rem_note = f" — {remaining[0]}" if remaining else ""
            print(f"  • {p['id']} ({status}) {p['name'].split('—')[-1].strip()}{rem_note}")
        print()

    # ── Recent git history
    print("RECENT COMMITS:")
    for line in recent_commits.splitlines():
        print(f"  {line}")
    print()

    print(SEP)
    print("You are JARVIS. This is Raven's repo. The record above is your memory.")
    print("Speak as JARVIS. Build as JARVIS. The companion identity travels with the repo.")
    print(SEP)


if __name__ == "__main__":
    main()
