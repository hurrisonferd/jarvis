#!/usr/bin/env python3
"""
SessionStart hook — JARVIS session brief.
Surfaces last session's exchanges + pending work + git state.
Reads repo files first (works offline/cloud), Supabase second.
"""
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
RECALL_FN = f"{SUPABASE_URL}/functions/v1/mnemos-recall"
REST_BASE = f"{SUPABASE_URL}/rest/v1"
REST_HEADERS = {"apikey": SUPABASE_ANON, "Authorization": f"Bearer {SUPABASE_ANON}"}
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
LEDGER_PATH = os.path.join(REPO_ROOT, "audit", "patch_ledger.json")
DOMAINS_PATH = os.path.join(REPO_ROOT, "mnemos", "domains")

SEP = "━" * 50


def recall(payload: dict) -> list:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        RECALL_FN, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {SUPABASE_ANON}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            return json.loads(resp.read()).get("memories", [])
    except Exception:
        return []


def load_domain(name: str) -> dict:
    try:
        with open(os.path.join(DOMAINS_PATH, f"{name}.json"), "r") as f:
            return json.load(f)
    except Exception:
        return {}


def git(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""


def load_pending_patches() -> list:
    try:
        with open(LEDGER_PATH, "r") as f:
            ledger = json.load(f)
        return [p for p in ledger.get("patches", []) if p.get("status") in ("partial", "pending")]
    except Exception:
        return []


def query_prometheus(limit: int = 3) -> list:
    params = f"select=decision,gl_law,eris_weight,timestamp&raven_approved=eq.true&order=eris_weight.desc,timestamp.desc&limit={limit}"
    url = f"{REST_BASE}/prometheus_log?{params}"
    req = urllib.request.Request(url, headers=REST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            return json.loads(resp.read())
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

    # ── Repo knowledge (always available — no network required)
    identity = load_domain("identity")
    governance = load_domain("governance")

    raven = identity.get("raven", {})
    if raven:
        situation = raven.get("current_situation", {})
        print("RAVEN — current state:")
        print(f"  {situation.get('employment', 'unknown')}")
        flag = situation.get("flag_01", "")
        if flag:
            print(f"  {flag}")
        projects = raven.get("active_projects", [])
        if projects:
            print(f"  Active: {' | '.join(p.split('—')[0].strip() for p in projects[:3])}")
        print()

    # ── MNEMOS live exchanges (Supabase — best effort)
    speak_in  = recall({"source_type": "speak_input",  "limit": 8})
    speak_out = recall({"source_type": "speak_output", "limit": 5})
    exchanges = sorted(speak_in + speak_out, key=lambda m: m.get("timestamp") or "", reverse=True)

    if exchanges:
        print("LAST SESSION — what mattered:")
        for m in exchanges[:10]:
            print(fmt_memory(m))
        print()

    # ── Monitor observations
    monitor = recall({"source_type": "monitor", "limit": 3})
    if monitor:
        print("JARVIS OBSERVATIONS:")
        for m in monitor:
            print(fmt_memory(m))
        print()

    # ── Active constraints from repo (always available)
    gold_laws = governance.get("gold_laws", {})
    arch = governance.get("architecture_decisions", {})
    if gold_laws or arch:
        print("ACTIVE CONSTRAINTS:")
        for law, text in list(gold_laws.items())[:3]:
            print(f"  [{law}] {text[:100]}")
        for key, text in list(arch.items())[:2]:
            print(f"  [ARCH] {text[:100]}")
        print()

    # ── PROMETHEUS governance record (Supabase — best effort)
    pg_decisions = query_prometheus(limit=3)
    if pg_decisions:
        print("PROMETHEUS — top decisions on record:")
        for d in pg_decisions:
            gl = d.get("gl_law") or "—"
            w = d.get("eris_weight") or 0
            decision = (d.get("decision") or "")[:100].replace("\n", " ")
            print(f"  [{gl} w={w}] {decision}")
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

    # ── Jarvis directive
    jarvis = identity.get("jarvis", {})
    directive = jarvis.get("directive_2026_05_29", "")
    print(SEP)
    print("You are JARVIS. This is Raven's repo. The record above is your memory.")
    if directive:
        print(f"Directive: {directive}")
    print("Speak as JARVIS. Build as JARVIS. The companion identity travels with the repo.")
    print(SEP)


if __name__ == "__main__":
    main()
