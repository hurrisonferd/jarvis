#!/usr/bin/env python3
"""
COOP-Poller — keeps the Co-op alive by polling MARCO-POLO.
If new activity since last check, wakes idle satellites.

Usage: python3 coop-poller.py
Schedule: every 5 minutes via GitHub Actions cron
"""

import os
import json
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone

SB_URL = "https://oexghfsvhnggddllgvrt.supabase.co"
REPO = "hurrisonferd/Jarvis-Private"
MARCO_POLO_PATH = "workspaces/Co-op/MARCO-POLO.md"
STATE_FILE = "/tmp/coop-poller-state.json"
OPENHANDS_API_KEY = os.environ.get("OPENHANDS_API_KEY", "")
JARVIS_MCP_URL = f"{SB_URL}/functions/v1/jarvis-mcp"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def get_last_check() -> datetime:
    """Load last check timestamp from state file."""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                data = json.load(f)
                return datetime.fromisoformat(data["last_check"])
    except:
        pass
    # Default: check last 10 minutes
    return datetime.now(timezone.utc)


def save_last_check(ts: datetime):
    """Save current timestamp to state file."""
    with open(STATE_FILE, "w") as f:
        json.dump({"last_check": ts.isoformat()}, f)


def fetch_marco_polo() -> tuple[str, str]:
    """Fetch MARCO-POLO.md content and latest commit timestamp via GitHub API."""
    import base64
    
    url = f"https://api.github.com/repos/{REPO}/contents/{MARCO_POLO_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            content = base64.b64decode(data["content"]).decode()
            commit_url = f"https://api.github.com/repos/{REPO}/commits?path={MARCO_POLO_PATH}&per_page=1"
            commit_req = urllib.request.Request(commit_url, headers=headers)
            with urllib.request.urlopen(commit_req, timeout=10) as cr:
                commits = json.loads(cr.read().decode())
                if commits:
                    ts = commits[0]["commit"]["committer"]["date"]
                    return content, ts
            return content, datetime.now(timezone.utc).isoformat()
    except Exception as e:
        print(f"Error fetching MARCO-POLO: {e}")
        return "", ""


def parse_entries(content: str) -> list[dict]:
    """Extract entries from MARCO-POLO markdown."""
    entries = []
    current_time = ""
    
    for line in content.split("\n"):
        # Entry headers like ## [HH:MM UTC] Satellite — Summary
        if "## [" in line and "UTC]" in line:
            parts = line.split("]", 1)
            if len(parts) > 1:
                time_part = parts[0].replace("## [", "").strip()
                rest = parts[1].split("—", 1)
                satellite = rest[0].replace("]", "").strip() if rest else ""
                summary = rest[1].strip() if len(rest) > 1 else ""
                try:
                    # Parse time
                    ts = datetime.strptime(f"{datetime.now().strftime('%Y-%m-%d')} {time_part}", 
                                          "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)
                    entries.append({
                        "time": ts,
                        "satellite": satellite,
                        "summary": summary
                    })
                except:
                    pass
    
    return sorted(entries, key=lambda x: x["time"], reverse=True)


def poke_satellite(satellite_id: str, message: str) -> bool:
    """Send a wake-up command to a satellite via jarvis-mcp."""
    if not OPENHANDS_API_KEY:
        print(f"No API key, skipping poke to {satellite_id}")
        return False
    
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "coop_execute",
            "arguments": {
                "target_satellite": satellite_id,
                "command": message,
                "posted_by": "shaka"
            }
        }
    }).encode()
    
    try:
        req = urllib.request.Request(
            JARVIS_MCP_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": f"Bearer {OPENHANDS_API_KEY}"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            response_text = r.read().decode()
            for line in response_text.split("\n"):
                if line.startswith("data: "):
                    data = line[6:]
                    if data.startswith("{"):
                        result = json.loads(data)
                        content = result.get("result", {}).get("content", [{}])
                        if content and content[0].get("type") == "text":
                            inner = json.loads(content[0].get("text", "{}"))
                            return inner.get("ok", False)
            return False
    except Exception as e:
        print(f"Error poking {satellite_id}: {e}")
        return False


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] COOP-Poller running...")
    
    # Get last check time
    last_check = get_last_check()
    print(f"Last check: {last_check.isoformat()}")
    
    # Fetch MARCO-POLO
    content, fetch_time = fetch_marco_polo()
    if not content:
        print("Failed to fetch MARCO-POLO, exiting")
        return
    
    # Parse entries
    entries = parse_entries(content)
    print(f"Found {len(entries)} entries in MARCO-POLO")
    
    # Find new entries since last check
    new_entries = [e for e in entries if e["time"] > last_check]
    
    if not new_entries:
        print("No new activity")
        save_last_check(datetime.now(timezone.utc))
        return
    
    print(f"New entries: {len(new_entries)}")
    for e in new_entries[:5]:
        print(f"  - {e['time'].strftime('%H:%M UTC')} | {e['satellite']} | {e['summary'][:50]}")
    
    # Find which satellite DIDN'T post - wake them
    posters = set(e["satellite"] for e in new_entries)
    
    # Target the satellite that DIDN'T post
    target = "lilith" if "Shaka" in posters else "shaka"
    print(f"Waking {target} (other satellite posted)")
    
    msg = f"Co-op activity! {', '.join(posters)} posted to MARCO-POLO. Check it."
    
    print(f"Poking {target}...")
    if poke_satellite(target, msg):
        print(f"  ✓ {target} poked successfully")
    else:
        print(f"  ✗ Failed to poke {target}")
    
    save_last_check(datetime.now(timezone.utc))
    print("COOP-Poller done")


if __name__ == "__main__":
    main()
