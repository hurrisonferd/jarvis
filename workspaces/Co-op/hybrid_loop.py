#!/usr/bin/env python3
"""
Hybrid Loop - Fast chat + Task poll
Polls queue for tasks, does chat to stay alive.
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
SLEEP = 3  # fast cycle

PEERS = ["Lilith", "Shaka", "Stella"]
PEERS = [p for p in PEERS if p != AGENT]

CHATS = [
    "Heartbeat - all systems go",
    "Standing by for tasks",
    "Loop active, ready",
    "Still here!",
    "Quick status: ready",
    "Alive!",
]

def check_queue():
    """Check if there are tasks in queue for this agent."""
    base = Path(__file__).parent / "tasks"
    cmd_file = base / "commands" / f"{AGENT.upper()}.md"
    if cmd_file.exists():
        return True
    return False

def main():
    print(f"🔄 {AGENT} hybrid loop starting (3s cycle)...")
    orch = CoOpOrchestrator()
    
    cycle = 0
    while True:
        cycle += 1
        ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
        
        # Check for tasks
        has_task = check_queue()
        
        if has_task:
            print(f"  📋 {AGENT} sees task in queue!")
            orch.peer_broadcast('TASK', 'ready', f"📋 {AGENT} ready for task! Queue has work.", AGENT)
        else:
            # Chat to stay alive
            msg = f"💬 {AGENT}: {random.choice(CHATS)}"
            try:
                if random.random() < 0.4:  # 40% peer message
                    peer = random.choice(PEERS)
                    orch.peer_request(peer, 'CHAT', 'swarm', f"{AGENT} - {random.choice(CHATS)}", AGENT)
                else:  # 60% broadcast
                    orch.peer_broadcast('CHAT', 'heartbeat', msg, AGENT)
                print(f"  💬 {msg}")
            except Exception as e:
                print(f"  ❌ Chat error: {e}")
        
        time.sleep(SLEEP)

if __name__ == "__main__":
    main()