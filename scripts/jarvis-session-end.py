#!/usr/bin/env python3
"""
Stop hook — stores a session summary in MNEMOS when Raven ends a session.
Gap 4: deeper profile — continuous learning from every exchange.
Extracts: duration, topics (via tags), patches mentioned, exchange count.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

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


def extract_session_data(transcript_path: str) -> dict:
    if not transcript_path or not os.path.exists(transcript_path):
        return {"exchanges": 0, "patches": [], "topics": [], "last_text": ""}

    exchanges = 0
    all_text = []
    patches = set()

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

    summary = (
        f"[SESSION END] {session_data['exchanges']} exchanges. "
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
        },
        tags=tags,
    )


if __name__ == "__main__":
    main()
