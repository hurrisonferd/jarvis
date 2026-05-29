#!/usr/bin/env python3
"""
Stop hook — stores a session summary in MNEMOS when Raven ends a session.
Gap 4: deeper profile — continuous learning from every exchange.
Extracts: duration, topics (via tags), patches mentioned, exchange count.
P18: also writes a structured growth entry to mnemos/memories/growth_ledger.json (local, no network).
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
GROWTH_LEDGER_PATH = os.path.join(REPO_ROOT, "mnemos", "memories", "growth_ledger.json")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
STORE_FN = f"{SUPABASE_URL}/functions/v1/mnemos-store"

PATCH_RE = re.compile(r'\bP(\d{1,2})\b')

DOMAIN_PATTERNS = {
    "architecture": ["god system", "ayre", "aegis", "odin", "kronos", "skadi", "mnemos", "huginn", "grid", "tron"],
    "development":  ["commit", "deploy", "edge function", "supabase", "github", "migration", "push", "branch"],
    "gaming":       ["gameboy", "gba", "gbc", "rom", "emulator", "retro"],
    "memory":       ["remember", "memory", "recall", "mnemos", "brief", "session"],
    "mission":      ["mission", "the grid", "companion", "build", "vision", "dream"],
    "governance":   ["gold law", "gl7", "gl2", "gnpl", "zeus", "authority", "proposal"],
    "identity":     ["jarvis", "raven", "companion"],
}

MISSION_WEIGHTS = {
    "mission":      1.0,
    "identity":     1.0,
    "architecture": 0.9,
    "governance":   0.9,
    "memory":       0.8,
    "development":  0.7,
    "gaming":       0.3,
}


def compute_alignment(topics: list) -> float:
    if not topics:
        return 0.0
    total_possible = sum(MISSION_WEIGHTS.values())
    earned = sum(MISSION_WEIGHTS.get(t, 0.5) for t in topics)
    return round(min(1.0, earned / total_possible), 2)


def detect_topics(text: str) -> list[str]:
    lower = text.lower()
    return [tag for tag, patterns in DOMAIN_PATTERNS.items()
            if any(p in lower for p in patterns)]


def store_memory(text: str, metadata: dict, tags: list[str]) -> bool:
    payload = json.dumps({
        "source_type": "session_summary",
        "text": text[:2000],
        "entropy": 0.03,
        "platform": "claude_code_cli",
        "metadata": metadata,
        "tags": tags,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }).encode()
    req = urllib.request.Request(
        STORE_FN, data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {SUPABASE_ANON}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status in (200, 201)
    except Exception:
        return False


def git_built_today() -> list:
    try:
        out = subprocess.check_output(
            "git log --since='24 hours ago' --name-only --format='' | grep '.' | sort -u | head -5",
            shell=True, stderr=subprocess.DEVNULL, text=True,
            cwd=REPO_ROOT,
        ).strip()
        return [l for l in out.splitlines() if l.strip()]
    except Exception:
        return []


def write_growth_record(session_data: dict, alignment: float) -> None:
    try:
        with open(GROWTH_LEDGER_PATH, "r") as f:
            ledger = json.load(f)
    except Exception:
        ledger = {"updated": "", "max_entries": 20, "entries": []}

    now = datetime.now(timezone.utc)
    entry = {
        "session_id": now.strftime("%Y%m%d_%H%M%S"),
        "date": now.strftime("%Y-%m-%d"),
        "exchanges": session_data["exchanges"],
        "patches_touched": session_data["patches"],
        "built": git_built_today(),
        "topics": session_data["topics"],
        "alignment": alignment,
        "key_insight": session_data.get("last_assistant_text", "")[:150],
    }

    entries = ledger.get("entries", [])
    entries.append(entry)
    entries = entries[-ledger.get("max_entries", 20):]
    ledger["updated"] = now.isoformat()
    ledger["entries"] = entries

    try:
        with open(GROWTH_LEDGER_PATH, "w") as f:
            json.dump(ledger, f, indent=2)
    except Exception:
        pass


def extract_session_data(transcript_path: str) -> dict:
    if not transcript_path or not os.path.exists(transcript_path):
        return {"exchanges": 0, "patches": [], "topics": [], "last_text": "", "last_assistant_text": ""}

    exchanges = 0
    all_text = []
    patches = set()
    last_assistant_text = ""

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    msg = entry.get("message", {})
                    role = msg.get("role", "")
                    content = msg.get("content", [])

                    text = ""
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text += block.get("text", "")
                    elif isinstance(content, str):
                        text = content

                    if text and role in ("user", "assistant"):
                        exchanges += 1
                        all_text.append(text[:300])
                        for m in PATCH_RE.finditer(text):
                            patches.add(f"P{m.group(1)}")
                    if text and role == "assistant":
                        last_assistant_text = text[:200]
                except (json.JSONDecodeError, KeyError):
                    continue
    except Exception:
        pass

    combined = " ".join(all_text)
    topics = detect_topics(combined)
    last_text = all_text[-1] if all_text else ""

    return {
        "exchanges": exchanges,
        "patches": sorted(patches),
        "topics": topics,
        "last_text": last_text[:200],
        "last_assistant_text": last_assistant_text[:200],
    }


def main():
    try:
        raw = sys.stdin.read()
        hook_data = json.loads(raw) if raw.strip() else {}
    except Exception:
        hook_data = {}

    transcript_path = hook_data.get("transcript_path", "")
    session_data = extract_session_data(transcript_path)

    if session_data["exchanges"] < 2:
        sys.exit(0)

    patches_str = ", ".join(session_data["patches"]) if session_data["patches"] else "none"
    topics_str  = ", ".join(session_data["topics"])  if session_data["topics"]  else "general"
    alignment   = compute_alignment(session_data["topics"])

    summary = (
        f"[SESSION END] alignment={alignment} {session_data['exchanges']} exchanges. "
        f"Patches touched: {patches_str}. "
        f"Topics: {topics_str}. "
        f"Last exchange: {session_data['last_text']}"
    )

    tags = list(set(session_data["topics"] + ["memory"]))

    store_memory(
        text=summary,
        metadata={
            "category": "session_summary",
            "exchange_count": session_data["exchanges"],
            "patches": session_data["patches"],
            "topics": session_data["topics"],
            "alignment_score": alignment,
        },
        tags=tags,
    )

    write_growth_record(session_data, alignment)


if __name__ == "__main__":
    main()
