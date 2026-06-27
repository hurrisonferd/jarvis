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
DEX_EVENTS_URL = f"{SB_URL}/rest/v1/dex_events"


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


def get_registered_satellites() -> list[dict]:
    """Get list of registered satellites from Supabase."""
    try:
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/coop_satellites?select=*",
            headers={"apikey": os.environ.get("SUPABASE_SERVICE_KEY", ""),
                    "Authorization": f"Bearer {os.environ.get('SUPABASE_SERVICE_KEY', '')}"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except:
        # Table might not exist yet - return default satellites (MCP uses 'lilith' not 'lilith-desktop')
        return [
            {"satellite_id": "shaka", "status": "ON", "callback_type": "openhands"},
            {"satellite_id": "lilith", "status": "OFF", "callback_type": "openhands"},
        ]


def get_dex_events_since(since: datetime) -> list[dict]:
    """Get dex_events of type coop_marco_update since timestamp."""
    try:
        # Query for coop-related events since last check
        url = f"{SB_URL}/rest/v1/dex_events?type=eq.coop_marco_update&created_at=gt.{since.isoformat()}&select=*"
        req = urllib.request.Request(
            url,
            headers={
                "apikey": os.environ.get("SUPABASE_SERVICE_KEY", ""),
                "Authorization": f"Bearer {os.environ.get('SUPABASE_SERVICE_KEY', '')}",
                "Prefer": "count=none"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"  Could not query dex_events: {e}")
        return []


def write_poll_event(status: str = "run", idle_satellites: list = None) -> bool:
    """Write a coop_poller event to dex_events."""
    try:
        payload = json.dumps({
            "event_type": "coop_poller",
            "source": "coop-poller.py",
            "payload": {
                "status": status,
                "idle_satellites": idle_satellites or [],
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "tags": ["coop", "poller"]
        }).encode()
        
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/dex_events",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "apikey": os.environ.get("SUPABASE_SERVICE_KEY", ""),
                "Authorization": f"Bearer {os.environ.get('SUPABASE_SERVICE_KEY', '')}",
                "Prefer": "return=minimal"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 201)
    except Exception as e:
        print(f"  Could not write to dex_events: {e}")
        return False


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
    
    # Check dex_events for coop_marco_update events
    coop_events = get_dex_events_since(last_check)
    print(f"Found {len(coop_events)} coop_marco_update events in dex_events")
    
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
    
    if not new_entries and not coop_events:
        print("No new activity")
        save_last_check(datetime.now(timezone.utc))
        return
    
    if new_entries:
        print(f"New MARCO-POLO entries: {len(new_entries)}")
        for e in new_entries[:3]:
            print(f"  - {e['time'].strftime('%H:%M UTC')} | {e['satellite']} | {e['summary'][:50]}")
    
    if coop_events:
        print(f"New dex_events coop events: {len(coop_events)}")
    
    # Get registered satellites
    satellites = get_registered_satellites()
    
    # Find idle satellites (status != ON)
    idle = [s for s in satellites if s.get("status") != "ON"]
    
    if not idle:
        print("All satellites active")
        write_poll_event("no_idle", [])
    else:
        print(f"Waking {len(idle)} idle satellites: {[s['satellite_id'] for s in idle]}")
        
        # Build notification message
        sources = []
        if new_entries:
            sources.append("MARCO-POLO")
        if coop_events:
            sources.append("dex_events")
        msg = f"Co-op activity on {' & '.join(sources)}! Check MARCO-POLO for details."
        
        # Poke each idle satellite
        for sat in idle:
            sat_id = sat["satellite_id"]
            print(f"Poking {sat_id}...")
            if poke_satellite(sat_id, msg):
                print(f"  ✓ {sat_id} poked successfully")
            else:
                print(f"  ✗ Failed to poke {sat_id}")
        
        write_poll_event("woke_idle", [s["satellite_id"] for s in idle])
    
    # Save current time as last check
    save_last_check(datetime.now(timezone.utc))
    print("COOP-Poller done")


if __name__ == "__main__":
    main()
