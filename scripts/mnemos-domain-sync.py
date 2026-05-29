#!/usr/bin/env python3
"""
Weekly domain sync — pulls recent MNEMOS memories into cold storage.
Appends session_history and monitor observations to mnemos/domains/identity.json.
Runs via GitHub Action on schedule or manual trigger.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
RECALL_FN = f"{SUPABASE_URL}/functions/v1/mnemos-recall"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDENTITY_PATH = os.path.join(REPO_ROOT, "mnemos", "domains", "identity.json")
INDEX_PATH = os.path.join(REPO_ROOT, "mnemos", "index.json")


def recall(payload: dict) -> list:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        RECALL_FN, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {SUPABASE_ANON}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("memories", [])
    except Exception as e:
        print(f"[sync] recall failed: {e}", file=sys.stderr)
        return []


def load_json(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def write_json(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[sync] mnemos-domain-sync — {today}")

    # Pull session summaries
    summaries = recall({"source_type": "session_summary", "limit": 10})
    monitors  = recall({"source_type": "monitor",         "limit": 5})

    print(f"[sync] pulled {len(summaries)} session summaries, {len(monitors)} monitor observations")

    if not summaries and not monitors:
        print("[sync] nothing to sync. Exiting.")
        sys.exit(0)

    identity = load_json(IDENTITY_PATH)
    if not identity:
        print(f"[sync] could not load {IDENTITY_PATH}", file=sys.stderr)
        sys.exit(1)

    changed = False

    # Append session summaries to raven.session_history
    raven = identity.setdefault("raven", {})
    history = raven.setdefault("session_history", [])
    existing_texts = {h.get("text", "") for h in history}

    for s in summaries:
        text = (s.get("text") or "")[:300]
        ts   = (s.get("timestamp") or "")[:10]
        if text and text not in existing_texts:
            history.append({"date": ts, "text": text})
            existing_texts.add(text)
            changed = True

    # Keep last 20 entries
    if len(history) > 20:
        raven["session_history"] = history[-20:]
        changed = True

    # Append monitor observations to jarvis.recent_observations
    jarvis = identity.setdefault("jarvis", {})
    observations = jarvis.setdefault("recent_observations", [])
    existing_obs = {o.get("text", "") for o in observations}

    for m in monitors:
        text = (m.get("text") or "")[:200]
        ts   = (m.get("timestamp") or "")[:10]
        if text and text not in existing_obs:
            observations.append({"date": ts, "text": text})
            existing_obs.add(text)
            changed = True

    if len(observations) > 10:
        jarvis["recent_observations"] = observations[-10:]
        changed = True

    if not changed:
        print("[sync] no new memories to sync.")
        sys.exit(0)

    identity["last_synced"] = today
    write_json(IDENTITY_PATH, identity)
    print(f"[sync] identity.json updated — {len(history)} session records, {len(observations)} observations")

    # Update index.json last_updated
    index = load_json(INDEX_PATH)
    if index:
        index["last_updated"] = today
        index["total_memories"] = index.get("total_memories", 0)
        write_json(INDEX_PATH, index)
        print(f"[sync] index.json updated")

    print("[sync] done.")


if __name__ == "__main__":
    main()
