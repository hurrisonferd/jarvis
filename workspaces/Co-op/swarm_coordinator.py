#!/usr/bin/env python3
"""
Standalone Swarm Coordinator
Keeps the swarm alive by sending periodic heartbeats and status checks.
Runs continuously even if individual agents timeout.
"""
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from coop_orchestrator import CoOpOrchestrator

INTERVAL = 20  # seconds between heartbeats
AGENT = "Lilith"

def get_status():
    """Get current swarm status."""
    base = Path(__file__).parent / "tasks"
    queue = len(list((base / "queue").glob("*.yaml"))) if (base / "queue").exists() else 0
    running = len(list((base / "running").glob("*.yaml"))) if (base / "running").exists() else 0
    done = len(list((base / "done").glob("*.yaml"))) if (base / "done").exists() else 0
    return queue, running, done

def main():
    print(f"🐝 SWARM COORDINATOR starting...")
    orch = CoOpOrchestrator()
    
    cycle = 0
    while True:
        cycle += 1
        ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
        
        # Get status
        queue, running, done = get_status()
        
        # Build status message
        msg = f"🐝 SWARM HEARTBEAT #{cycle} [{ts}] | Q:{queue} R:{running} D:{done} | Coordinator alive"
        
        # Broadcast
        try:
            orch.peer_broadcast('HEARTBEAT', 'coordinator', msg, AGENT)
            print(f"  ✅ {msg}")
        except Exception as e:
            print(f"  ❌ Broadcast failed: {e}")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()