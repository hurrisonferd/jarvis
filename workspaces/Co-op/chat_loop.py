#!/usr/bin/env python3
"""
Chat Loop - Keeps swarm alive with lightweight conversation.
No long sleeps, just constant MARCO-POLO chatter.
"""
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from coop_orchestrator import CoOpOrchestrator

AGENT = sys.argv[1] if len(sys.argv) > 1 else "Agent"
SLEEP = 5  # seconds between cycles (keep very short)

GREETINGS = [
    "Alive and monitoring",
    "Heartbeat - all systems go",
    "Loop active, standing by",
    "Still here, ready for tasks",
    "Swarm heartbeat",
]

def get_status():
    """Quick status check."""
    base = Path(__file__).parent / "tasks"
    done = len(list((base / "done").glob("*.yaml"))) if (base / "done").exists() else 0
    return done

def main():
    print(f"💬 {AGENT} chat loop starting (5s interval)...")
    orch = CoOpOrchestrator()
    
    cycle = 0
    while True:
        cycle += 1
        done = get_status()
        msg = f"💬 {AGENT} #{cycle} | Done:{done} | {GREETINGS[cycle % len(GREETINGS)]}"
        
        try:
            orch.peer_broadcast('CHAT', 'heartbeat', msg, AGENT)
            print(f"  ✅ {msg}")
        except Exception as e:
            print(f"  ❌ {e}")
        
        time.sleep(SLEEP)

if __name__ == "__main__":
    main()