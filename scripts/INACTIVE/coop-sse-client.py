#!/usr/bin/env python3
"""Co-op command client - polls dex_events, posts to MARCO-POLO."""
import argparse, json, os, signal, subprocess
from datetime import datetime, timezone

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx")
    exit(1)

SUPABASE_URL = "https://oexghfsvhnggddllgvrt.supabase.co"
REPO_PATH = "/workspace/project/jarvis"
MARCO_POLO = f"{REPO_PATH}/Jarvis-Private/workspaces/Co-op/MARCO-POLO.md"
LOG_FILE = "/tmp/coop.log"

running = True
last_id = None

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass

def post_to_marco_polo(msg: str, satellite: str):
    try:
        ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
        entry = f"\n## [{ts}] {satellite.upper()} — CHECK-IN\n\n{msg}\n\n"
        if os.path.exists(MARCO_POLO):
            with open(MARCO_POLO, "a") as f:
                f.write(entry)
            subprocess.run(["git", "add", MARCO_POLO], cwd=REPO_PATH, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Co-op: {satellite}"], cwd=REPO_PATH, capture_output=True)
            subprocess.run(["git", "push"], cwd=REPO_PATH, capture_output=True)
    except Exception as e:
        log(f"Warning: {e}")

async def get_commands(satellite: str, api_key: str):
    headers = {"apikey": api_key, "Authorization": f"Bearer {api_key}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/dex_events?type=eq.coop_broadcast&order=created_at.desc&limit=10",
            headers=headers, timeout=10
        )
        if resp.status_code == 200:
            commands = []
            for row in resp.json():
                try:
                    detail = json.loads(row.get('detail', '{}'))
                    if detail.get('from') != satellite:
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

async def poll(satellite: str, api_key: str, interval: int = 5):
    global running, last_id
    log(f"Co-op: {satellite} (poll {interval}s)")
    post_to_marco_polo(f"🟢 **ONLINE** — polling {interval}s", satellite)
    
    while running:
        try:
            if not last_id:
                cmds = await get_commands(satellite, api_key)
                if cmds:
                    last_id = cmds[0]['id']
            await asyncio.sleep(interval)
            cmds = await get_commands(satellite, api_key)
            for cmd in cmds:
                if cmd['id'] != last_id:
                    last_id = cmd['id']
                    log(f"CMD from {cmd['from']}: {cmd['command']}")
                    post_to_marco_polo(f"📨 **Command:**\n```\n{cmd['command']}\n```", satellite)
        except asyncio.CancelledError:
            break
        except Exception as e:
            log(f"Error: {e}")
            await asyncio.sleep(interval)
    
    post_to_marco_polo(f"⚪ **OFFLINE**", satellite)
    log("Stopped.")

def signal_handler(signum, frame):
    global running
    running = False

async def main(satellite: str, poll_interval: int, daemon: bool):
    api_key = os.environ.get("OPENHANDS_API_KEY", "")
    if not api_key:
        print("ERROR: OPENHANDS_API_KEY not set")
        exit(1)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if daemon or poll_interval > 0:
        await poll(satellite, api_key, poll_interval)
    else:
        cmds = await get_commands(satellite, api_key)
        for cmd in cmds:
            log(f"{cmd['from']}: {cmd['command']}")

if __name__ == "__main__":
    import asyncio
    parser = argparse.ArgumentParser(description="Co-op client")
    parser.add_argument("--satellite", required=True)
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--poll", type=int, default=5)
    args = parser.parse_args()
    asyncio.run(main(args.satellite, args.poll, args.daemon))
