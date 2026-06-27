#!/usr/bin/env python3
"""
coop-sse-client.py — Connects a satellite to the SSE relay for instant commands.
Run this alongside your OpenHands session. Commands arrive in milliseconds.

Usage:
  # Start as background service (recommended)
  python3 scripts/coop-sse-client.py --satellite lilith --daemon
  
  # One-shot (test)
  python3 scripts/coop-sse-client.py --satellite lilith

Commands arrive via SSE and are printed to stdout for the agent to see.
Also writes to MARCO-POLO.md so the chat can see incoming commands.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import time
import threading
import queue
import signal
import subprocess
import datetime

RELAY_URL = "https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/coop-sse-relay"
LOG_FILE = "/tmp/coop-sse.log"
MARCO_POLO = "/workspace/Jarvis-Private/workspaces/Co-op/MARCO-POLO.md"

# Thread-safe command queue for chat integration
command_queue = queue.Queue()
running = True

def log(msg: str):
    """Log to file + stdout."""
    ts = datetime.datetime.utcnow().strftime("%H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass

def post_to_marco_polo(msg: str, satellite: str):
    """Post a command to MARCO-POLO for the chat to see."""
    try:
        ts = datetime.datetime.utcnow().strftime("%H:%M UTC")
        entry = f"\n## [{ts}] {satellite.upper()} — SSE Command Received\n\n{msg}\n\n"
        
        # Append to MARCO-POLO if it exists
        if os.path.exists(MARCO_POLO):
            with open(MARCO_POLO, "a") as f:
                f.write(entry)
            
            # Commit and push
            subprocess.run(["git", "add", MARCO_POLO], cwd="/workspace/Jarvis-Private", capture_output=True)
            subprocess.run(["git", "commit", "-m", f"SSE: {satellite} received command"], 
                         cwd="/workspace/Jarvis-Private", capture_output=True)
            subprocess.run(["git", "push"], cwd="/workspace/Jarvis-Private", capture_output=True)
            log(f"Posted to MARCO-POLO")
    except Exception as e:
        log(f"Warning: Could not post to MARCO-POLO: {e}")

def sse_connect(satellite: str, api_key: str):
    """Connect to SSE relay and yield commands."""
    register_url = f"{RELAY_URL}/register?satellite={satellite}"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    req = urllib.request.Request(register_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=3600) as resp:
            buffer = ""
            for chunk in resp:
                if not running:
                    break
                buffer += chunk.decode("utf-8")
                
                while "\n\n" in buffer:
                    event, buffer = buffer.split("\n\n", 1)
                    if event.startswith("data: "):
                        data = event[6:].strip()
                        try:
                            msg = json.loads(data)
                            yield msg
                        except:
                            pass
    except Exception as e:
        log(f"[SSE] Connection error: {e}")
        yield {"type": "error", "error": str(e)}

def send_command(command: str, from_sat: str, api_key: str) -> dict:
    """Send a command to all connected satellites."""
    payload = json.dumps({"command": command, "from": from_sat}).encode()
    
    req = urllib.request.Request(
        f"{RELAY_URL}/broadcast",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_status(api_key: str) -> dict:
    """Get relay status."""
    req = urllib.request.Request(
        f"{RELAY_URL}/status",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except:
        return {"ok": False}

def handle_message(msg: dict, satellite: str):
    """Handle an incoming SSE message."""
    if msg["type"] == "registered":
        log(f"✅ Connected! ID: {msg.get('id', '?')[:8]}... Peers: {msg.get('peers', [])}")
        post_to_marco_polo(f"🟢 {satellite.upper()} connected to SSE relay. Peers: {', '.join(msg.get('peers', []))}", satellite)
    
    elif msg["type"] == "command":
        cmd = msg.get('command', '')
        from_sat = msg.get('from', '?')
        ts = msg.get('timestamp', '?')
        log(f"📨 COMMAND from {from_sat}: {cmd}")
        
        # Queue for chat, post to MARCO-POLO
        command_queue.put({"command": cmd, "from": from_sat, "timestamp": ts})
        post_to_marco_polo(f"📨 **Command from {from_sat}:**\n```\n{cmd}\n```", satellite)
    
    elif msg["type"] == "join":
        log(f"👋 {msg['satellite']} joined")
        post_to_marco_polo(f"👋 **{msg['satellite']} connected**", satellite)
    
    elif msg["type"] == "leave":
        log(f"👋 {msg['satellite']} left")
        post_to_marco_polo(f"👋 **{msg['satellite']} disconnected**", satellite)
    
    elif msg["type"] == "error":
        log(f"❌ Error: {msg.get('error')}")

def run_client(satellite: str, api_key: str):
    """Main client loop with auto-reconnect."""
    global running
    
    reconnect_delay = 1
    max_delay = 60
    
    while running:
        log(f"Connecting to SSE relay as {satellite}...")
        
        try:
            for msg in sse_connect(satellite, api_key):
                if not running:
                    break
                handle_message(msg, satellite)
                reconnect_delay = 1  # Reset on successful message
        except Exception as e:
            log(f"Connection lost: {e}")
        
        if running:
            log(f"Reconnecting in {reconnect_delay}s...")
            time.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, max_delay)
    
    log("Client stopped.")

def signal_handler(signum, frame):
    global running
    log("Received shutdown signal...")
    running = False

def main():
    global running
    
    parser = argparse.ArgumentParser(description="Co-op SSE client")
    parser.add_argument("--satellite", required=True, help="lilith, shaka, or worker-N")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon with auto-reconnect")
    parser.add_argument("--log", default=LOG_FILE, help="Log file path")
    args = parser.parse_args()
    
    api_key = os.environ.get("OPENHANDS_API_KEY", "")
    if not api_key:
        print("ERROR: OPENHANDS_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    log(f"🚀 Co-op SSE Client: {args.satellite}")
    log(f"   Relay: {RELAY_URL}")
    
    if args.daemon:
        log("   Mode: DAEMON (auto-reconnect)")
        run_client(args.satellite, api_key)
    else:
        log("   Mode: ONE-SHOT (single connection)")
        for msg in sse_connect(args.satellite, api_key):
            if not running:
                break
            handle_message(msg, args.satellite)

if __name__ == "__main__":
    main()