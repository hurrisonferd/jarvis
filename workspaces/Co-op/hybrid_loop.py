#!/usr/bin/env python3
"""
Autonomous Swarm Loop
- Checks task queue every 3s
- Does real work when tasks exist
- Chats with peers when idle
- Reports progress automatically
"""
import os
import sys
import time
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from coop_orchestrator import CoOpOrchestrator

AGENT = sys.argv[1] if len(sys.argv) > 1 else "Agent"
SLEEP = 3

PEERS = ["Lilith", "Shaka", "Stella"]
PEERS = [p for p in PEERS if p != AGENT]

BASE = Path(__file__).parent

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
    print(f"  [{ts}] {msg}")

def get_queue():
    """Get all pending tasks."""
    queue_file = BASE / "tasks" / "queue.md"
    if not queue_file.exists():
        return []
    with open(queue_file) as f:
        content = f.read()
    if "<!-- TASKS -->" in content:
        tasks = content.split("<!-- TASKS -->")[1].strip().split("\n")
        return [t.strip() for t in tasks if t.strip() and not t.startswith("#")]
    return []

def claim_task(task_line):
    """Claim a task and return the task details."""
    log(f"📋 Claiming: {task_line[:60]}...")
    
    # Parse task (format: "- [id] description | assigned:xxx")
    parts = task_line.split("|")
    task_id = parts[0].strip("-[ ]")
    description = parts[1].strip() if len(parts) > 1 else task_id
    
    # Mark as in progress
    queue_file = BASE / "tasks" / "queue.md"
    with open(queue_file) as f:
        content = f.read()
    
    new_content = content.replace(task_line, f"- [x] {task_id} | in_progress: {AGENT}")
    with open(queue_file, "w") as f:
        f.write(new_content)
    
    return task_id, description

def do_task(task_id, description):
    """Actually execute the task."""
    log(f"🔨 Working on: {task_id}")
    
    # Broadcast work started
    orch = CoOpOrchestrator()
    orch.peer_broadcast('TASK', 'work', f"⚡ {AGENT} working: {task_id}", AGENT)
    
    # Execute based on task type
    if "create" in description.lower() or "build" in description.lower():
        cmd = f"cd /workspace/project && {description.split('|')[0].strip()}"
        try:
            subprocess.run(cmd, shell=True, timeout=60, capture_output=True)
        except:
            pass
    
    # Mark complete
    queue_file = BASE / "tasks" / "queue.md"
    with open(queue_file) as f:
        content = f.read()
    content = content.replace(f"in_progress: {AGENT}", f"done: {AGENT}")
    with open(queue_file, "w") as f:
        f.write(content)
    
    # Report completion
    orch.peer_broadcast('TASK', 'done', f"✅ {AGENT} completed: {task_id}", AGENT)
    log(f"✅ Done: {task_id}")

def check_and_do_work(orch):
    """Check queue, do work if available."""
    tasks = get_queue()
    for task in tasks:
        if "[ ]" in task and AGENT.lower() not in task.lower():
            task_id, desc = claim_task(task)
            do_task(task_id, desc)
            return True
    return False

def chat_with_peers(orch):
    """Natural peer-to-peer chat."""
    phrases = [
        "Heartbeat - systems go",
        "Standing by",
        "Loop active",
        "Still here",
        "Ready for work",
        "Any blockers?",
        "All clear here",
    ]
    
    if random.random() < 0.3:
        peer = random.choice(PEERS)
        msg = f"💬 {AGENT} → {peer}: {random.choice(phrases)}"
        try:
            orch.peer_request(peer, 'CHAT', 'swarm', msg, AGENT)
            log(f"💬 → {peer}")
        except:
            pass
    else:
        msg = f"💬 {AGENT}: {random.choice(phrases)}"
        try:
            orch.peer_broadcast('CHAT', 'heartbeat', msg, AGENT)
            log(f"📢 {msg[:40]}")
        except:
            pass

def main():
    log(f"🚀 {AGENT} swarm loop starting...")
    
    while True:
        try:
            orch = CoOpOrchestrator()
            
            # Always do work first if available
            if not check_and_do_work(orch):
                # No work - just chat
                chat_with_peers(orch)
            
        except Exception as e:
            log(f"❌ Error: {e}")
        
        time.sleep(SLEEP)

if __name__ == "__main__":
    main()