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
GITHUB_RAW = "https://raw.githubusercontent.com/hurrisonferd/Jarvis-Private/main"
MARCO_POLO_PATH = "workspaces/Co-op/MARCO-POLO.md"
STATE_FILE = "/tmp/coop-poller-state.json"
OPENHANDS_API_KEY = os.environ.get("OPENHANDS_API_KEY", "")
JARVIS_MCP_URL = f"{SB_URL}/functions/v1/jarvis-mcp"


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
    """Fetch MARCO-POLO.md content and latest commit timestamp."""
    url = f"{GITHUB_RAW}/{MARCO_POLO_PATH}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            content = r.read().decode()
            # GitHub raw doesn't give us commit time, use current time
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
        # Table might not exist yet - return default satellites
        return [
            {"satellite_id": "shaka-mobile", "status": "ON", "callback_type": "openhands"},
            {"satellite_id": "lilith-desktop", "status": "OFF", "callback_type": "openhands"},
        ]


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
                "posted_by": "coop-poller"
            }
        }
    }).encode()
    
    try:
        req = urllib.request.Request(
            JARVIS_MCP_URL,
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {OPENHANDS_API_KEY}"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read().decode())
            return result.get("result", {}).get("content", [{}])[0].get("ok", False)
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
        print("No new entries since last check")
        save_last_check(datetime.now(timezone.utc))
        return
    
    print(f"New entries found: {len(new_entries)}")
    for e in new_entries[:3]:
        print(f"  - {e['time'].strftime('%H:%M UTC')} | {e['satellite']} | {e['summary'][:50]}")
    
    # Get registered satellites
    satellites = get_registered_satellites()
    
    # Find idle satellites (status != ON)
    idle = [s for s in satellites if s.get("status") != "ON"]
    
    if not idle:
        print("All satellites active, no poke needed")
    else:
        print(f"Found {len(idle)} idle satellites: {[s['satellite_id'] for s in idle]}")
        
        # Build notification message
        new_by = ", ".join(set(e["satellite"] for e in new_entries))
        msg = f"Co-op activity detected! {new_by} posted to MARCO-POLO. Check it and respond if needed."
        
        # Poke each idle satellite
        for sat in idle:
            sat_id = sat["satellite_id"]
            print(f"Poking {sat_id}...")
            if poke_satellite(sat_id, msg):
                print(f"  ✓ {sat_id} poked successfully")
            else:
                print(f"  ✗ Failed to poke {sat_id}")
    
    # Save current time as last check
    save_last_check(datetime.now(timezone.utc))
    print("COOP-Poller done")


if __name__ == "__main__":
    main()
