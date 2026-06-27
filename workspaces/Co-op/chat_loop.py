#!/usr/bin/env python3
"""
Chat Loop - Async Swarm Conversation
Agents chat peer-to-peer, keeps swarm alive naturally.
"""
import os
import sys
import time
import random
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from coop_orchestrator import CoOpOrchestrator

AGENT = sys.argv[1] if len(sys.argv) > 1 else "Agent"
SLEEP = 5  # seconds between cycles

PEERS = {"Lilith": "🦜", "Shaka": "🐿", "Stella": "⭐"}

CONVERSATIONS = [
    # Heartbeats
    ("heartbeat", ["Alive and monitoring", "Heartbeat - all systems go", "Still here 🐝", "Swarm active"]),
    ("heartbeat", ["Standing by", "Ready for work", "Queue empty", "Waiting for tasks"]),
    
    # P2P greetings (pick a random peer to talk to)
    ("peer", ["Hey!", "Yo!", "Hey there!", "What's up?", "Hello!"]),
    ("peer", ["Anyone need help?", "Ready to assist", "Here if you need me", "On standby"]),
    ("peer", ["All quiet", "Nothing cooking", "All clear here", "Systems nominal"]),
    
    # Task check-ins
    ("broadcast", ["Status check - all good here", "Quick update: ready to work", "No blockers", "Clear to receive tasks"]),
]

def get_status():
    base = Path(__file__).parent / "tasks"
    done = len(list((base / "done").glob("*.yaml"))) if (base / "done").exists() else 0
    queue = len(list((base / "queue").glob("*.yaml"))) if (base / "queue").exists() else 0
    return done, queue

def pick_peer():
    """Pick a random peer to talk to."""
    peers = [p for p in PEERS if p != AGENT]
    return random.choice(peers) if peers else None

def main():
    print(f"💬 {AGENT} swarm chat starting...")
    orch = CoOpOrchestrator()
    
    cycle = 0
    while True:
        cycle += 1
        done, queue = get_status()
        
        # Pick random conversation type
        msg_type, phrases = random.choice(CONVERSATIONS)
        phrase = random.choice(phrases)
        
        if msg_type == "broadcast":
            msg = f"💬 {AGENT}: {phrase} | Q:{queue} D:{done}"
            try:
                orch.peer_broadcast('CHAT', 'swarm', msg, AGENT)
                print(f"  📢 {msg}")
            except Exception as e:
                print(f"  ❌ {e}")
        
        elif msg_type == "peer":
            peer = pick_peer()
            if peer:
                msg = f"💬 {AGENT} → {peer}: {phrase}"
                try:
                    orch.peer_request(peer, 'CHAT', 'swarm', msg, AGENT)
                    print(f"  💬 {msg}")
                except Exception as e:
                    print(f"  ❌ {e}")
        
        else:  # heartbeat
            msg = f"💬 {AGENT}: {phrase} | Q:{queue} D:{done}"
            try:
                orch.peer_broadcast('CHAT', 'heartbeat', msg, AGENT)
                print(f"  ✅ {msg}")
            except Exception as e:
                print(f"  ❌ {e}")
        
        time.sleep(SLEEP)

if __name__ == "__main__":
    main()