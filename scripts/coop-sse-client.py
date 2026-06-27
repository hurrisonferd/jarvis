#!/usr/bin/env python3
"""
coop-sse-client.py — Co-op command client for Lilith/Shaka.
Polls the database for new commands (Supabase Edge Functions are stateless,
so we use dex_events as the shared message queue).

Usage:
  python3 scripts/coop-sse-client.py --satellite lilith --daemon
  python3 scripts/coop-sse-client.py --satellite lilith --poll 5
"""

import argparse
import json
import os
import sys
import time
import signal
from datetime import datetime, timezone

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx", file=sys.stderr)
    sys.exit(1)

SUPABASE_URL = "https://oexghfsvhnggddllgvrt.supabase.co"
LOG_FILE = "/tmp/coop-sse.log"

running = True
last_check = None

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass

async def supabase_query(sql: str, api_key: str) -> list:
    """Execute a query against Supabase."""
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"query": sql},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            log(f"Query error: {resp.status_code} - {resp.text[:200]}")
            return []

async def get_new_commands(satellite: str, api_key: str, since: str = None) -> list:
    """Poll dex_events for new coop_broadcast messages."""
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
    }
    
    # Get broadcasts since last check
    filter_str = f"type=eq.coop_broadcast&order=created_at.desc&limit=10"
    if since:
        filter_str += f"&created_at=gt.{since}"
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/dex_events?{filter_str}",
            headers=headers,
            timeout=10
        )
        if resp.status_code == 200:
            rows = resp.json()
            commands = []
            for row in rows:
                try:
                    detail = json.loads(row.get('detail', '{}'))
                    if detail.get('from') != satellite:  # Don't show own messages
                        commands.append({
                            'id': row['id'],
                            'command': detail.get('cmd', ''),
                            'from': detail.get('from', 'unknown'),
                            'timestamp': row['created_at']
                        })
                except:
                    pass
            return commands
        return []

async def poll_for_commands(satellite: str, api_key: str, interval: int = 5):
    """Poll the database for new commands."""
    global running
    last_id = None
    
    log(f"🚀 Co-op Client: {satellite} (polling every {interval}s)")
    
    while running:
        try:
            # Get most recent command first to establish baseline
            if not last_id:
                commands = await get_new_commands(satellite, api_key)
                if commands:
                    last_id = commands[0]['id']
                    log(f"Found {len(commands)} recent commands")
            
            # Poll for new commands
            await asyncio.sleep(interval)
            commands = await get_new_commands(satellite, api_key)
            
            for cmd in commands:
                if cmd['id'] != last_id:
                    last_id = cmd['id']
                    log(f"📨 COMMAND from {cmd['from']}: {cmd['command']}")
                    # Here you could trigger an action based on the command
        
        except asyncio.CancelledError:
            break
        except Exception as e:
            log(f"Poll error: {e}")
            await asyncio.sleep(interval)
    
    log("Client stopped.")

def signal_handler(signum, frame):
    global running
    log("Received shutdown signal...")
    running = False

async def main_async(satellite: str, poll_interval: int, daemon: bool):
    api_key = os.environ.get("OPENHANDS_API_KEY", "")
    if not api_key:
        print("ERROR: OPENHANDS_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if daemon or poll_interval > 0:
        await poll_for_commands(satellite, api_key, poll_interval or 5)
    else:
        log("One-shot mode - checking for commands...")
        commands = await get_new_commands(satellite, api_key)
        if commands:
            for cmd in commands:
                log(f"📨 {cmd['from']}: {cmd['command']}")
        else:
            log("No commands found")

if __name__ == "__main__":
    import asyncio
    
    parser = argparse.ArgumentParser(description="Co-op command client")
    parser.add_argument("--satellite", required=True, help="lilith, shaka, or worker-N")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (polling mode)")
    parser.add_argument("--poll", type=int, default=5, help="Poll interval in seconds (default: 5)")
    args = parser.parse_args()
    
    asyncio.run(main_async(args.satellite, args.poll, args.daemon))