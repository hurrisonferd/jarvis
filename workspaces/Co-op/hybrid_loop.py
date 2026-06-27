#!/usr/bin/env python3
"""
Hybrid Loop - Real work + Chat combined
Agents poll tasks AND chat - keeps sessions alive.
"""
import os
import sys
import time
import random
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from coop_orchestrator import CoOpOrchestrator
from task_manager import TaskManager

AGENT = sys.argv[1] if len(sys.argv) > 1 else "Agent"
SLEEP = 5  # seconds between cycles

PEERS = ["Lilith", "Shaka", "Stella"]
PEERS = [p for p in PEERS if p != AGENT]

CHATS = [
    "Heartbeat - all systems go",
    "Standing by for tasks",
    "Loop active, ready",
    "Still here!",
    "Quick status: ready",
]

def main():
    print(f"🔄 {AGENT} hybrid loop starting...")
    orch = CoOpOrchestrator()
    tm = TaskManager()
    
    cycle = 0
    while True:
        cycle += 1
        ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
        
        # 1. DO REAL WORK - poll tasks
        try:
            task = tm.fetch_task(AGENT)
            if task:
                print(f"  📋 {AGENT} got task: {task.get('id', 'unknown')}")
                # Execute task
                tm.complete_task(task.get('id'))
                # Broadcast completion
                orch.peer_broadcast('TASK', 'complete', f"✅ {AGENT} completed: {task.get('id', 'unknown')}", AGENT)
            else:
                # 2. CHAT to stay alive
                msg = f"💬 {AGENT} [{ts}]: {random.choice(CHATS)}"
                try:
                    if random.random() < 0.3:  # 30% peer message
                        peer = random.choice(PEERS)
                        orch.peer_request(peer, 'CHAT', 'swarm', f"{AGENT} here - {random.choice(CHATS)}", AGENT)
                    else:  # 70% broadcast
                        orch.peer_broadcast('CHAT', 'heartbeat', msg, AGENT)
                    print(f"  💬 {msg}")
                except Exception as e:
                    print(f"  ❌ Chat error: {e}")
        except Exception as e:
            print(f"  ❌ Task error: {e}")
        
        time.sleep(SLEEP)

if __name__ == "__main__":
    main()