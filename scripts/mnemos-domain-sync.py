#!/usr/bin/env python3
"""
MNEMOS → GitHub daily sync.
Writes memory and context files to mnemos/ so any model with repo access
can read JARVIS memory without Supabase credentials.

Structure:
  mnemos/memories/recent.json    — last 50 memories (all types)
  mnemos/memories/decisions.json — PROMETHEUS governance decisions
  mnemos/memories/sessions.json  — last 20 session summaries
  mnemos/context/system.json     — Gold Laws, pipeline, God Systems, agents
  mnemos/context/patches.json    — patch status (active + pending only)
  mnemos/index.json              — manifest

Supabase is write-first. GitHub is read-first.
Fallback: git log is used when Supabase is unavailable.
"""
import json
import os
import pathlib
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
if not SUPABASE_URL.startswith(("http://", "https://")):
    SUPABASE_URL = f"https://{SUPABASE_URL}"  # secret may omit the scheme

SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
)
REST = f"{SUPABASE_URL}/rest/v1"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

ROOT     = pathlib.Path(__file__).parent.parent
MNEMOS   = ROOT / "mnemos"
MEMORIES = MNEMOS / "memories"
CONTEXT  = MNEMOS / "context"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()[:19] + "Z"


def git_cmd(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def sync_from_git() -> int:
    """Fallback: read git log and write commits as memories when Supabase unavailable."""
    log = git_cmd("git log --pretty=format:%H|%an|%ai|%s --max-count=50")
    if not log:
        return 0
    out = []
    for line in log.splitlines():
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        sha, author, ts, msg = parts
        if "[skip ci]" in msg:
            continue
        out.append({
            "id":          sha[:12],
            "source_type": "github_commit",
            "text":        f"[{sha[:7]}] {msg} (by {author})",
            "timestamp":   ts[:19].replace(" ", "T"),
            "tags":        ["development"],
            "model":       "jarvis",
        })
    write_json(MEMORIES / "recent.json", {
        "updated": now_iso(), "count": len(out), "memories": out,
    })
    return len(out)


def fetch_rest(path: str) -> list:
    req = urllib.request.Request(f"{REST}/{path}", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"  warn: {path} — {e}", file=sys.stderr)
        return []


def write_json(path: pathlib.Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"  wrote {path.relative_to(ROOT)}")


# ── memory files ─────────────────────────────────────────────────────────────

def sync_recent() -> int:
    rows = fetch_rest(
        "mnemos_memories?select=id,source_type,text,timestamp,tags,metadata"
        "&order=timestamp.desc&limit=50"
    )
    out = []
    for r in rows:
        out.append({
            "id":          r.get("id"),
            "source_type": r.get("source_type"),
            "text":        (r.get("text") or "")[:500],
            "timestamp":   (r.get("timestamp") or "")[:19],
            "tags":        r.get("tags") or [],
            "model":       (r.get("metadata") or {}).get("source_model", "jarvis"),
        })
    write_json(MEMORIES / "recent.json", {
        "updated": now_iso(), "count": len(out), "memories": out,
    })
    return len(out)


def sync_decisions() -> int:
    rows = fetch_rest(
        "prometheus_log?select=decision,rationale,gl_law,tags,eris_weight,timestamp"
        "&raven_approved=eq.true&order=eris_weight.desc,timestamp.desc&limit=30"
    )
    out = []
    for r in rows:
        out.append({
            "gl_law":      r.get("gl_law"),
            "decision":    (r.get("decision") or "")[:300],
            "rationale":   (r.get("rationale") or "")[:200],
            "eris_weight": r.get("eris_weight"),
            "tags":        r.get("tags") or [],
            "timestamp":   (r.get("timestamp") or "")[:10],
        })
    write_json(MEMORIES / "decisions.json", {
        "updated": now_iso(), "count": len(out), "decisions": out,
    })
    return len(out)


def sync_sessions() -> int:
    rows = fetch_rest(
        "mnemos_memories?select=text,timestamp,tags"
        "&source_type=eq.session_summary&order=timestamp.desc&limit=20"
    )
    out = []
    for r in rows:
        out.append({
            "text":      (r.get("text") or "")[:600],
            "timestamp": (r.get("timestamp") or "")[:19],
            "tags":      r.get("tags") or [],
        })
    write_json(MEMORIES / "sessions.json", {
        "updated": now_iso(), "count": len(out), "sessions": out,
    })

    # Also keep identity.json updated (backward compat)
    identity_path = MNEMOS / "domains" / "identity.json"
    try:
        identity = json.loads(identity_path.read_text())
        raven = identity.setdefault("raven", {})
        history = raven.setdefault("session_history", [])
        existing = {h.get("text", "") for h in history}
        changed = False
        for r in rows:
            text = (r.get("text") or "")[:300]
            ts   = (r.get("timestamp") or "")[:10]
            if text and text not in existing:
                history.append({"date": ts, "text": text})
                existing.add(text)
                changed = True
        if changed:
            raven["session_history"] = history[-20:]
            identity["last_synced"] = now_iso()[:10]
            write_json(identity_path, identity)
    except Exception:
        pass

    return len(out)


# ── context files ─────────────────────────────────────────────────────────────

def write_system_context() -> None:
    write_json(CONTEXT / "system.json", {
        "updated":     now_iso()[:10],
        "node":        "node-001-raven",
        "owner":       "raven",
        "description": "JARVIS system context. Read this to understand the architecture before writing code.",
        "stack":       ["github", "supabase", "claude_code"],
        "pipeline":    "AYRE → AEGIS → ODIN → KRONOS → SKADI → MNEMOS → HUGINN",
        "parallel":    ["HALO", "MIMIR", "BIFROST"],
        "gold_laws": [
            "GL2: no autonomous self-modification — JARVIS proposes, Raven commits or rejects",
            "GL5: no silent state mutation — every state change emits a BUS event and is logged",
            "GL6: no unvalidated execution — AEGIS gates all high-risk actions",
            "GL7 SUPREME: no expansion without simplification — every addition requires a reduction",
            "GL9: all actions map intent → decision → execution → log",
        ],
        "constraints": [
            "Cloud-first stack only — no Ollama, no local-PC-dependent services",
            "27 God Systems are fixed — do not redefine, renumber, or add",
            "Raven (John Barber) is final authority on all commits",
            "AEGIS gates all emulator starts and high-risk actions",
            "Expansion requires reduces_complexity=true and overlap_score_below=0.40",
        ],
        "god_systems": {
            "count": 27,
            "pipeline":        ["AYRE", "AEGIS", "ODIN", "KRONOS", "SKADI", "MNEMOS", "HUGINN"],
            "parallel":        ["HALO", "MIMIR", "BIFROST"],
            "foundational":    ["CHAOS", "ZEUS", "POSEIDON", "HADES"],
            "governance":      ["ERIS", "ARGUS", "ATHENA", "PROMETHEUS", "NEMESIS"],
            "integrity":       ["IRIS", "MERIDIAN"],
            "interface":       ["DANTE", "APOLLO"],
            "observability":   ["JANUS"],
            "infrastructure":  ["ATLAS"],
            "translation":     ["HERMES"],
        },
        "agents": {
            "jarvis": {"trust": 1.0,  "role": "sovereign", "archetype": "Shiroe"},
            "codex":  {"trust": 0.85, "role": "executor",  "archetype": "Kang"},
            "gpt":    {"trust": 0.80, "role": "executor",  "archetype": "Kang"},
            "gemini": {"trust": 0.70, "role": "ideator",   "archetype": "Aizen"},
        },
        "memory_architecture": {
            "write":  "mnemos-store edge fn → Supabase mnemos_memories (fast, optional)",
            "embed":  "auto-embed on store via EMBEDDING_API_KEY (OpenAI-compatible)",
            "search": "mnemos-search → pgvector cosine similarity → tsv fulltext fallback",
            "sync":   "daily GitHub Action → mnemos/memories/ + mnemos/context/ files",
            "read":   "any model reads mnemos/ files from repo — no credentials needed",
            "fallback": "git log → mnemos/memories/recent.json when Supabase unavailable",
        },
    })


def write_patches_context() -> None:
    ledger_path = ROOT / "audit" / "patch_ledger.json"
    try:
        ledger = json.loads(ledger_path.read_text())
    except Exception:
        return
    patches = ledger.get("patches", [])
    active = []
    for p in patches:
        status = p.get("status", "pending")
        if status == "reference":
            continue
        active.append({
            "id":        p.get("id"),
            "name":      p.get("name"),
            "status":    status,
            "priority":  p.get("priority"),
            "summary":   (p.get("summary") or "")[:200],
            "remaining": p.get("remaining", []),
        })
    write_json(CONTEXT / "patches.json", {
        "updated":              now_iso()[:10],
        "implementation_order": ledger.get("implementation_order", []),
        "patches":              active,
    })


# ── index ─────────────────────────────────────────────────────────────────────

def write_index(counts: dict) -> None:
    write_json(MNEMOS / "index.json", {
        "version":     "2.1",
        "updated":     now_iso(),
        "node":        "node-001-raven",
        "description": "JARVIS memory and context store. GitHub is the read layer — no credentials needed.",
        "read_order": [
            "1. mnemos/context/system.json — architecture, Gold Laws, agents (read first)",
            "2. mnemos/memories/recent.json — last 50 memories or git log (Supabase optional)",
            "3. mnemos/memories/decisions.json — approved governance decisions",
            "4. mnemos/memories/sessions.json — session summaries + pipeline observations",
            "5. mnemos/context/patches.json — patch status",
            "6. mnemos/memories/events.jsonl — github issues/PRs",
            "7. mnemos/domains/ — identity profiles (Raven, JARVIS)",
        ],
        "files": {
            "memories/recent.json":    {"desc": "Last 50 memories (Supabase) or git commits (fallback)", "count": counts.get("recent", 0)},
            "memories/decisions.json": {"desc": "PROMETHEUS governance decisions", "count": counts.get("decisions", 0)},
            "memories/sessions.json":  {"desc": "Session summaries + pipeline observations", "count": counts.get("sessions", 0)},
            "memories/events.jsonl":   {"desc": "GitHub issues and PRs (append log)"},
            "context/system.json":     {"desc": "Gold Laws, pipeline, God Systems, agent trust scores"},
            "context/patches.json":    {"desc": "Patch ledger — active and pending only"},
            "domains/identity.json":   {"desc": "JARVIS + Raven identity domain profiles"},
        },
        "pipeline": {
            "workflow": "jarvis-pipeline.yml",
            "jobs":     "AYRE → AEGIS → MNEMOS → HUGINN",
            "triggers": ["push:main", "schedule:06:00UTC", "workflow_dispatch"],
            "supabase": "optional — git log fallback active when unavailable",
        },
        "tags": [
            "jarvis", "raven", "mission", "architecture", "governance",
            "memory", "grid", "gaming", "development", "emotional"
        ],
    })


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    today = now_iso()[:10]
    print(f"MNEMOS → GitHub sync — {today}")
    print("─" * 40)

    counts = {}
    counts["recent"] = sync_recent()
    if counts["recent"] == 0:
        print("  Supabase unreachable — falling back to git log")
        counts["recent"] = sync_from_git()
    counts["decisions"] = sync_decisions()
    counts["sessions"]  = sync_sessions()

    write_system_context()
    write_patches_context()
    write_index(counts)

    print("─" * 40)
    print(f"sync complete: {counts}")


if __name__ == "__main__":
    main()
