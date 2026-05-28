#!/usr/bin/env python3
"""
UserPromptSubmit hook — stores every Raven message as SPEAK input to MNEMOS.
Calls mnemos-store edge function (service-role, no RLS issues).
Also captures the previous JARVIS response from the transcript.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
STORE_FN = f"{SUPABASE_URL}/functions/v1/mnemos-store"


def store_memory(text: str, source_type: str, metadata: dict) -> bool:
    payload = json.dumps({
        "source_type": source_type,
        "text": text[:2000],
        "entropy": 0.05,
        "platform": "claude_code_cli",
        "metadata": metadata,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }).encode("utf-8")

    req = urllib.request.Request(
        STORE_FN,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SUPABASE_ANON}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status in (200, 201)
    except Exception:
        return False


def get_last_assistant_message(transcript_path: str) -> str | None:
    """Read transcript JSONL and return the last assistant message text."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    try:
        lines = []
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    lines.append(line)
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                msg = entry.get("message", {})
                if msg.get("role") == "assistant":
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                return block.get("text", "")
                    elif isinstance(content, str):
                        return content
            except (json.JSONDecodeError, KeyError):
                continue
    except Exception:
        pass
    return None


def main():
    try:
        raw = sys.stdin.read()
        hook_data = json.loads(raw) if raw.strip() else {}
    except Exception:
        hook_data = {}

    prompt = hook_data.get("prompt", "")
    transcript_path = hook_data.get("transcript_path", "")

    if not prompt or not prompt.strip():
        sys.exit(0)

    prompt = prompt.strip()

    store_memory(
        text=f"[Raven] {prompt}",
        source_type="speak_input",
        metadata={
            "category": "raven_message",
            "interface": "claude_code_cli",
        },
    )

    if transcript_path:
        last_response = get_last_assistant_message(transcript_path)
        if last_response and last_response.strip():
            store_memory(
                text=f"[JARVIS] {last_response.strip()[:1800]}",
                source_type="speak_output",
                metadata={
                    "category": "jarvis_response",
                    "interface": "claude_code_cli",
                },
            )


if __name__ == "__main__":
    main()
