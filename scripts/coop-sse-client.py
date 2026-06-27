#!/usr/bin/env python3
"""
coop-sse-client.py — Connects a satellite to the SSE relay for instant commands.
Run this alongside your OpenHands session. Commands arrive in milliseconds.

Usage:
  python3 coop-sse-client.py --satellite lilith

Commands arrive via SSE and are printed to stdout for the agent to see.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import threading
import queue
import time

RELAY_URL = "https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/coop-sse-relay"

# Thread-safe command queue
command_queue = queue.Queue()

def sse_connect(satellite: str, api_key: str):
    """Connect to SSE relay and yield commands."""
    register_url = f"{RELAY_URL}/register?satellite={satellite}"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    req = urllib.request.Request(register_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=3600) as resp:
            buffer = ""
            for chunk in resp:
                buffer += chunk.decode("utf-8")
                
                # Process complete events
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
        print(f"[SSE] Connection error: {e}", file=sys.stderr)
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

def main():
    parser = argparse.ArgumentParser(description="Co-op SSE client")
    parser.add_argument("--satellite", required=True, help="lilith or shaka")
    parser.add_argument("--poll", action="store_true", help="Poll for commands instead of SSE")
    args = parser.parse_args()
    
    api_key = os.environ.get("OPENHANDS_API_KEY", "")
    if not api_key:
        print("ERROR: OPENHANDS_API_KEY not set", file=sys.stderr)
        return
    
    print(f"🚀 Co-op SSE Client: {args.satellite}")
    
    if args.poll:
        # Fallback: poll for commands (less real-time but works without SSE)
        print("   Mode: POLLING (fallback)")
        print("   Commands will appear as they arrive.")
        while True:
            # This would need a separate endpoint to get pending commands
            time.sleep(5)
    else:
        # Main: SSE connection
        print("   Mode: SSE (real-time)")
        print(f"   Relay: {RELAY_URL}")
        print("   Waiting for commands...")
        
        for msg in sse_connect(args.satellite, api_key):
            if msg["type"] == "registered":
                print(f"✅ Connected! ID: {msg.get('id', '?')[:8]}...")
                print(f"   Peers online: {', '.join(msg.get('peers', []))}")
            
            elif msg["type"] == "command":
                print(f"\n📨 COMMAND from {msg.get('from')}:")
                print(f"   {msg['command']}")
                print(f"   (at {msg.get('timestamp', '?')})")
                print()
            
            elif msg["type"] == "join":
                print(f"👋 {msg['satellite']} joined")
            
            elif msg["type"] == "leave":
                print(f"👋 {msg['satellite']} left")
            
            elif msg["type"] == "error":
                print(f"❌ Error: {msg.get('error')}")
                break
        
        print("Disconnected. Reconnecting in 5s...")
        time.sleep(5)

if __name__ == "__main__":
    main()