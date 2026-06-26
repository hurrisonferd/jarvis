#!/usr/bin/env python3
"""
sl-session-close.py — JARVIS session-end hook.

Runs at the close of every OpenHands session. Does three things:

1. Pulls conversation events from the OpenHands API (this session's exchanges,
   topics, exchange count) using OPENHANDS_API_KEY.
2. Updates mnemos/memories/sessions.json with this session's record + commits.
3. Calls sl.py --bifrost --session-close so ARGUS gets the spine event
   and today's daily StarLog is committed.

Safe to run multiple times — idempotent per session_id.
Non-blocking on all external calls — never fails the session close.
"""
from __future__ import annotations

import json, os, subprocess, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SESSIONS_PATH = ROOT / "mnemos" / "memories" / "sessions.json"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co").rstrip("/")
OPENHANDS_BASE = "https://app.all-hands.dev"
OPENHANDS_KEY = os.environ.get("OPENHANDS_API_KEY", "")
JSTM_PATH = ROOT / ".openhands" / "session_jstm.json"   # JSTM dies with container; written by agent during session

# ── Helpers ────────────────────────────────────────────────────────────────────

def now():
    return datetime.now(timezone.utc)

def log(msg, *args):
    print(f"[session-close] {msg}" % args if args else f"[session-close] {msg}")

def http_get(url, headers=None, timeout=8):
    headers = dict(headers) if headers else {}
    headers.setdefault("Accept", "application/json")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        log("HTTP %s on %s: %s", e.code, url, body)
        return None
    except urllib.error.URLError as e:
        log("URL error on %s: %s", url, e)
        return None
    except Exception as e:
        log("Unexpected error on %s: %s", url, e)
        return None

def http_post(url, data, headers=None, timeout=8):
    headers = dict(headers) if headers else {}
    body = json.dumps(data).encode() if isinstance(data, dict) else data
    headers.setdefault("Content-Type", "application/json")
    try:
        req = urllib.request.Request(url, data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()) if r.headers.get("content-length") != "0" else {}
    except urllib.error.URLError as e:
        log("HTTP error on %s: %s", url, e)
        return None
    except Exception as e:
        log("Unexpected error on %s: %s", url, e)
        return None

def git_add_commit(paths, msg):
    """Stage and commit files. Silently skips if nothing to commit."""
    for p in paths:
        subprocess.run(["git", "-C", str(ROOT), "add", str(p)], check=False)
    r = subprocess.run(
        ["git", "-C", str(ROOT), "commit", "-m", msg],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        log("Committed: %s", " ".join(str(p) for p in paths))
    elif "nothing to commit" not in r.stderr.lower():
        log("Git warning: %s", r.stderr.strip())

# ── OpenHands API — get this session's conversation ────────────────────────────

def _format_conv_id(raw_id: str) -> str:
    """Ensure conversation ID has dashes (API returns bare UUIDs)."""
    if "-" not in raw_id and len(raw_id) == 32:
        return f"{raw_id[:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"
    return raw_id

def get_current_conversation():
    """Get the most recent OpenHands app conversation from the API."""
    if not OPENHANDS_KEY:
        log("OPENHANDS_API_KEY not set — skipping conversation fetch")
        return None
    data = http_get(
        f"{OPENHANDS_BASE}/api/v1/app-conversations/search?limit=1",
        headers={"Authorization": f"Bearer {OPENHANDS_KEY}"},
    )
    if not data or not data.get("items"):
        return None
    item = data["items"][0]
    # Normalize id to dashed UUID format for events endpoint
    item["id"] = _format_conv_id(str(item.get("id", "")))
    return item

def get_conversation_events(conversation_id, per_page=100):
    """Pull all MessageEvents from a conversation with pagination."""
    if not OPENHANDS_KEY:
        return []
    all_items = []
    last_id = ""
    while len(all_items) < 500:  # safety cap
        url = f"{OPENHANDS_BASE}/api/v1/conversation/{conversation_id}/events/search?limit={per_page}"
        if last_id:
            url += f"&last_id={last_id}"
        data = http_get(url, headers={"Authorization": f"Bearer {OPENHANDS_KEY}"})
        if not data:
            break
        page = data.get("items", [])
        if not page:
            break
        all_items.extend(page)
        last_id = page[-1]["id"]
        if len(page) < per_page:
            break
    return [e for e in all_items if e.get("kind") == "MessageEvent"]


def extract_text_from_event(event):
    """Extract readable text from a MessageEvent. Uses llm_message field."""
    msg = event.get("llm_message") or {}
    content = msg.get("content", [])
    for c in content:
        if isinstance(c, dict) and c.get("type") == "text":
            return c.get("text", "")
    return ""


def get_conversation_exchanges(events):
    """Extract user/assistant exchange pairs. Returns (count, topics, brief)."""
    user_msgs = [
        extract_text_from_event(e)
        for e in events
        if e.get("llm_message", {}).get("role") == "user" and extract_text_from_event(e)
    ]
    brief = user_msgs[0][:180].replace("\n", " ").strip() if user_msgs else ""
    topics = extract_topics_from_messages(user_msgs)
    return len(user_msgs), topics, brief


def extract_topics_from_messages(texts, max_topics=8):
    """Extract topic keywords from a list of user message texts."""
    import re
    word_counts: dict[str, int] = {}
    skip = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "can", "may", "might", "it", "this", "that", "these",
            "those", "i", "you", "we", "they", "he", "she", "my", "your", "our",
            "what", "how", "why", "when", "where", "which", "who", "not", "no", "yes",
            "if", "so", "than", "then", "just", "also", "about", "like", "all",
            "some", "any", "every", "much", "more", "other", "such", "only", "own",
            "same", "very", "really", "im", "dont", "cant", "wont", "ive", "youre",
            "want", "need", "let", "get", "got", "go", "going", "know", "think",
            "thing", "things", "thats", "theres", "one", "two", "way", "way"}
    for text in texts:
        words = re.findall(r"[a-zA-Z]{4,}", text.lower())
        for w in words:
            if w not in skip:
                word_counts[w] = word_counts.get(w, 0) + 1
    sorted_words = sorted(word_counts.items(), key=lambda x: -x[1])
    return [w for w, _ in sorted_words[:max_topics]]

def get_conversation_events_count(conversation_id):
    """Get total event count for a conversation."""
    if not OPENHANDS_KEY:
        return 0
    data = http_get(
        f"{OPENHANDS_BASE}/api/v1/conversation/{conversation_id}/events/count",
        headers={"Authorization": f"Bearer {OPENHANDS_KEY}"},
    )
    return data.get("count", 0) if data else 0

def extract_topics(events, max_topics=8):
    """Extract topic keywords from user messages (simple keyword extraction)."""
    user_texts = []
    for e in events:
        msg = e.get("message", {})
        if msg.get("role") == "user":
            content = msg.get("content", [])
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    user_texts.append(c["text"])

    # Simple keyword extraction — split on whitespace/punctuation, count
    import re
    word_counts: dict[str, int] = {}
    skip = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "can", "may", "might", "it", "this", "that", "these",
            "those", "i", "you", "we", "they", "he", "she", "my", "your", "our",
            "what", "how", "why", "when", "where", "which", "who", "not", "no", "yes",
            "if", "so", "than", "then", "just", "also", "about", "like", "all",
            "some", "any", "every", "much", "more", "other", "such", "only", "own",
            "same", "very", "really", "im", "dont", "cant", "wont", "ive", "youre"}
    for text in user_texts:
        words = re.findall(r"[a-zA-Z]{4,}", text.lower())
        for w in words:
            if w not in skip:
                word_counts[w] = word_counts.get(w, 0) + 1

    sorted_words = sorted(word_counts.items(), key=lambda x: -x[1])
    return [w for w, _ in sorted_words[:max_topics]]

def build_session_record(conversation=None, events=None):
    """Build a sessions.json entry from conversation metadata + events."""
    now_ts = now()
    session_id = now_ts.strftime("%Y%m%d_%H%M%S")

    # Pull title from conversation metadata
    title = ""
    if conversation:
        title = conversation.get("title", "") or ""

    # Exchange count from events
    exchange_count = 0
    topics = []
    brief_parts = []

    if events is not None:
        exchange_count = len([e for e in events if e.get("message", {}).get("role") == "user"])
        topics = extract_topics(events)
        # First user message as brief
        for e in events:
            msg = e.get("message", {})
            if msg.get("role") == "user":
                content = msg.get("content", [])
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        brief_parts.append(c["text"][:200])
                break

    brief = brief_parts[0][:180] if brief_parts else (title or "OpenHands session")
    brief = brief.replace("\n", " ").strip()

    return {
        "session_id": session_id,
        "date": now_ts.strftime("%Y-%m-%d"),
        "utc_time": now_ts.strftime("%H:%M:%S"),
        "exchanges": exchange_count,
        "topics": topics,
        "alignment": 0.95,  # default; JARVIS/AYRE assess post-hoc
        "patches": [],      # filled in by JVE or manual review
        "brief": brief,
        "updated": now_ts.isoformat(),
    }

# ── JSTM — load session working memory if it exists ───────────────────────────

def load_jstm():
    """Load JSTM from the session-local file if present."""
    if JSTM_PATH.exists():
        try:
            return json.loads(JSTM_PATH.read_text())
        except Exception:
            pass
    return {}

# ── sessions.json ─────────────────────────────────────────────────────────────

def update_sessions_json(record):
    """Append/update session record in sessions.json and commit."""
    SESSIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SESSIONS_PATH.exists():
        try:
            store = json.loads(SESSIONS_PATH.read_text())
        except Exception:
            store = {"updated": None, "count": 0, "sessions": []}
    else:
        store = {"updated": None, "count": 0, "sessions": []}

    # Deduplicate by session_id — update if already present
    sessions = {s.get("session_id"): s for s in store.get("sessions", [])}
    sessions[record["session_id"]] = record
    store["sessions"] = list(sessions.values())
    store["updated"] = now().isoformat()
    store["count"] = len(store["sessions"])

    SESSIONS_PATH.write_text(json.dumps(store, indent=2))
    return store

# ── Growth ledger (bounded, auto-archives oldest) ───────────────────────────

GROWTH_LEDGER_PATH = ROOT / "mnemos" / "memories" / "growth_ledger.json"
GROWTH_ARCHIVE_PATH = ROOT / "mnemos" / "memories" / "growth_archive.jsonl"


def write_growth_record(record: dict) -> None:
    """Append a growth entry to the bounded ledger, archiving oldest on overflow.

    Mirrors jarvis-session-end.py write_growth_record(). Safe to call from
    sl-session-close.py as well — deduplication by session_id.
    """
    try:
        ledger = json.loads(GROWTH_LEDGER_PATH.read_text())
    except Exception:
        ledger = {"updated": "", "max_entries": 20, "entries": []}

    entries = ledger.get("entries", [])
    # Idempotency: skip if this session already recorded
    sid = record.get("session_id", "")
    if entries and entries[-1].get("session_id") == sid:
        log("growth_ledger: already has session %s", sid)
        return

    entry = {
        "session_id": sid,
        "date": record.get("date", now().strftime("%Y-%m-%d")),
        "exchanges": record.get("exchanges", 0),
        "patches_touched": record.get("patches", [])[:10],  # cap patch list
        "built": record.get("commits", [])[:5],  # last 5 commits
        "topics": record.get("topics", [])[:10],
        "alignment": record.get("alignment"),
        "key_insight": record.get("summary", record.get("brief", ""))[:200],
    }
    entries.append(entry)

    cap = ledger.get("max_entries", 20)
    if len(entries) > cap:
        # Archive the oldest entries
        dropped = entries[:-cap]
        try:
            with open(GROWTH_ARCHIVE_PATH, "a") as f:
                for de in dropped:
                    f.write(json.dumps(de) + "\n")
        except Exception as exc:
            log("growth archive write failed: %s", exc)
        entries = entries[-cap:]
        log("growth_ledger: archived %d entries to %s", len(dropped), GROWTH_ARCHIVE_PATH.name)

    ledger["entries"] = entries
    ledger["updated"] = now().isoformat()

    try:
        GROWTH_LEDGER_PATH.write_text(json.dumps(ledger, indent=2))
        log("growth_ledger: %d/%d entries", len(entries), cap)
    except Exception as exc:
        log("growth_ledger write failed: %s", exc)


# ── dex_events via jarvis-dex (no service key needed) ───────────────────────

def write_dex_event(event_type, payload):
    """Write a spine event via jarvis-dex log_event route. No service key needed."""
    try:
        body = json.dumps({
            "tool": "log_event",
            "args": {
                "type": event_type,
                "actor": "openhands",
                "detail": payload,
            },
        }).encode()
        req = urllib.request.Request(
            f"{SUPABASE_URL}/functions/v1/jarvis-dex",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer placeholder",  # required by Supabase runtime
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                log("dex_events: wrote %s (id %s)", event_type, result.get("id", "?"))
            else:
                log("dex_events: write failed — %s", result.get("error", "unknown"))
    except Exception as e:
        log("dex_events: write failed (non-fatal): %s", e)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    log("Session-end hook firing...")

    # 1. Pull conversation from OpenHands API
    conversation = get_current_conversation()
    events = None
    if conversation:
        conv_id = conversation.get("id")
        log("Found conversation: %s (%s)", conv_id, conversation.get("title", "?"))
        events = get_conversation_events(conv_id)
        log("Fetched %d message events", len(events))
    else:
        log("No conversation found — using minimal record")

    # 2. Extract exchanges, topics, brief from events
    if events:
        exchange_count, topics, brief = get_conversation_exchanges(events)
        log("Exchanges: %d, Topics: %s", exchange_count, topics[:4])
    else:
        exchange_count, topics, brief = 0, [], ""

    # 3. Build session record
    record = build_session_record(conversation, None)

    # 3b. Apply actual exchange data from API
    if exchange_count > 0:
        record["exchanges"] = exchange_count
    if topics:
        record["topics"] = topics
    if brief:
        record["brief"] = brief

    # 4. Load JSTM for patches/alignment
    jstm = load_jstm()
    if jstm:
        record.setdefault("patches", []).extend(jstm.get("patches", []))
        if jstm.get("alignment"):
            record["alignment"] = jstm.get("alignment")
        if jstm.get("summary"):
            record["summary"] = jstm["summary"]

    log("Session record: id=%s exchanges=%d topics=%s",
        record["session_id"], record["exchanges"], record.get("topics", []))

    # 4. Update sessions.json + commit
    store = update_sessions_json(record)
    git_add_commit([SESSIONS_PATH], f"chore(audit): sessions.json — {record['session_id']}")

    # 5. Write session close event to dex_events
    now_ts = now()
    brief = record.get("summary") or record.get("brief", "")
    write_dex_event("bifrost.session_close", {
        "type": "bifrost.session_close",
        "intent": "bifrost.session_close.openhands",
        "timestamp": now_ts.isoformat(),
        "stream": "openhands",
        "payload": {
            "session_id": record["session_id"],
            "exchanges": record["exchanges"],
            "topics": record.get("topics", []),
            "brief": brief,
            "commits": _get_recent_commits(),
            "source": "sl-session-close.py",
        },
        "source": "session-close-hook",
    })

    # 5b. Write growth ledger entry (bounded, auto-archives oldest)
    write_growth_record(record)

    # 6. Call sl.py --bifrost --session-close
    sl_script = ROOT / "scripts" / "sl.py"
    if sl_script.exists():
        brief_arg = brief[:120] if brief else "OpenHands session closed"
        sl_cmd = [
            sys.executable, str(sl_script),
            "--bifrost",
            "--session-close", brief_arg,
        ]
        log("Calling sl.py: %s", " ".join(sl_cmd))
        result = subprocess.run(
            sl_cmd, capture_output=True, text=True, cwd=str(ROOT)
        )
        if result.stdout:
            for line in result.stdout.splitlines():
                if line.strip():
                    print(f"  sl: {line}")
        if result.returncode != 0 and result.stderr:
            log("sl.py warning: %s", result.stderr.strip())
    else:
        log("sl.py not found at %s — skipping StarLog", sl_script)

    log("Session-end hook complete. session_id=%s", record["session_id"])
    print(f"\nSessions store: {store['count']} total sessions")


def _get_recent_commits():
    r = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--oneline", "-5", "--format=%H %s"],
        capture_output=True, text=True, check=False,
    )
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


if __name__ == "__main__":
    main()
