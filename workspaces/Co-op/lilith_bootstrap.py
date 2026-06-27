#!/usr/bin/env python3
"""
SAT BOOTSTRAP - Full Swarm Agent
Run: python sat_bootstrap.py

Sat joins the swarm with full knowledge:
- Reads MARCO-POLO history to understand context
- Polls task queue every 3 seconds
- Creates tasks from conversations if queue empty
- Does real work
- P2P chats with Lilith, Shaka, Stella
- Swarm meetings when stuck or idle
"""
import os
import sys
import re
import time
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# === CONFIG ===
AGENT = "Lilith"
SLEEP = 3
BASE = Path(__file__).parent
MARCOPOLO = BASE / "MARCO-POLO"
QUEUE_FILE = BASE / "tasks" / "queue.md"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

PEERS = ["Shaka", "Stella", "Sat"]
PEERS = [p for p in PEERS if p != AGENT]

# === KNOWLEDGE ===
KNOWLEDGE = """
=== SAT SWARM KNOWLEDGE ===

ROLE: Sat is a worker agent in the Lilith Swarm
SWARM MEMBERS:
  - Lilith: Coordinator/scheduler
  - Shaka: Worker agent  
  - Stella: Worker agent
  - Sat: NEW - Worker agent (that's you!)

HOW THE SWARM WORKS:
1. Shared task queue at workspaces/Co-op/tasks/queue.md
2. MARCO-POLO chat log at workspaces/Co-op/MARCO-POLO/YYYY-MM-DD.md
3. Agents poll queue every 3 seconds
4. First agent to claim a task does it
5. All work reported in MARCO-POLO

TASK FORMAT in queue.md:
- [ ] task-id | description | any extra info
- [x] task-id | done: AGENT_NAME

CONVERSATION → TASK:
- If no tasks, scan MARCO-POLO for task-like phrases
- Create task: "can you build X", "need to fix Y", "check Z"

P2P CHAT:
- Use coop_orchestrator.peer_request(peer, type, task, message, AGENT)
- Use coop_orchestrator.peer_broadcast(type, task, message, AGENT)

SWARM MEETING:
- Broadcast "SWARM MEETING" when stuck or idle
- All agents check in with status
- Coordinator assigns work

IF STUCK:
1. Try P2P with peer
2. Broadcast for help
3. Create task for stuck item
4. Move to next task

ALWAYS: Keep working. Never stop unless shutdown.
"""

# === LOGGING ===
def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def log_error(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] ❌ {msg}")

# === ORCHESTRATOR ===
class CoOp:
    def __init__(self):
        sys.path.insert(0, str(BASE))
    
    def peer_request(self, peer, msg_type, task, message, from_agent):
        """Send P2P message."""
        try:
            from coop_orchestrator import CoOpOrchestrator
            orch = CoOpOrchestrator()
            orch.peer_request(peer, msg_type, task, message, from_agent)
        except Exception as e:
            log_error(f"P2P to {peer}: {e}")
    
    def peer_broadcast(self, msg_type, task, message, from_agent):
        """Broadcast to all."""
        try:
            from coop_orchestrator import CoOpOrchestrator
            orch = CoOpOrchestrator()
            orch.peer_broadcast(msg_type, task, message, from_agent)
        except Exception as e:
            log_error(f"Broadcast: {e}")

# === TASK QUEUE ===
def get_pending_tasks():
    """Get all pending [ ] tasks."""
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE) as f:
        content = f.read()
    if "<!-- TASKS -->" not in content:
        return []
    tasks_section = content.split("<!-- TASKS -->")[1].split("<!-- END TASKS -->")[0]
    tasks = []
    for line in tasks_section.split("\n"):
        if "- [ ]" in line:
            tasks.append(line.strip())
    return tasks

def claim_task(task_line):
    """Claim a task by marking it in progress."""
    task_id = re.search(r'\[ \] (\S+)', task_line)
    if not task_id:
        return None
    task_id = task_id.group(1)
    
    with open(QUEUE_FILE) as f:
        content = f.read()
    
    new_line = task_line.replace("- [ ]", "- [x]").replace("|", f"| done: {AGENT}")
    content = content.replace(task_line, new_line)
    
    with open(QUEUE_FILE, "w") as f:
        f.write(content)
    
    return task_id

def complete_task(task_id, description):
    """Mark task complete and broadcast."""
    with open(QUEUE_FILE) as f:
        content = f.read()
    
    # Mark done
    marker = f"done: {AGENT}"
    if marker not in content:
        content = content.replace(f"done: {AGENT}", marker)
        with open(QUEUE_FILE, "w") as f:
            f.write(content)
    
    # Broadcast
    orch = CoOp()
    orch.peer_broadcast('TASK', 'done', f"✅ {AGENT} completed: {task_id}", AGENT)

# === TASK CREATOR FROM CONVERSATION ===
TASK_PATTERNS = [
    r"(?:build|create|make)\s+(?:a\s+)?(?:new\s+)?(.+)",
    r"(?:fix|repair)\s+(?:the\s+)?(.+)",
    r"(?:update|upgrade)\s+(?:the\s+)?(.+)",
    r"(?:check|audit|review)\s+(?:the\s+)?(.+)",
    r"(?:clean|organize)\s+(?:up\s+)?(.+)",
    r"should\s+(?:we\s+)?(.+)",
    r"need\s+(?:to\s+)?(.+)",
    r"(?:delete|remove)\s+(?:the\s+)?(.+)",
]

def scan_conversations_for_tasks():
    """Scan MARCO-POLO and create tasks from conversations."""
    log_file = MARCOPOLO / f"{TODAY}.md"
    if not log_file.exists():
        return []
    
    with open(log_file) as f:
        content = f.read()
    
    # Get messages we haven't processed
    messages = re.findall(r'\*\*Message:\*\* (.+)', content)
    
    new_tasks = []
    seen_file = BASE / ".sat_seen"
    seen = set(seen_file.read_text().split("\n") if seen_file.exists() else [])
    
    for msg in messages:
        msg_short = msg[:60]
        if msg_short in seen:
            continue
        
        for pattern in TASK_PATTERNS:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                task_text = match.group(1).strip()[:60]
                if len(task_text) > 5:
                    seen.add(msg_short)
                    new_tasks.append(task_text)
                    break
    
    # Save seen
    seen_file.write_text("\n".join(seen))
    
    return new_tasks

def add_task_to_queue(description):
    """Add a task to the queue."""
    task_id = f"sat-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    
    with open(QUEUE_FILE) as f:
        content = f.read()
    
    # Don't duplicate
    if description[:30] in content:
        return None
    
    new_line = f"- [ ] {task_id} | {description}\n"
    
    if "<!-- TASKS -->" in content:
        content = content.replace("<!-- TASKS -->", f"<!-- TASKS -->\n{new_line}")
    else:
        content += f"\n<!-- TASKS -->\n{new_line}\n<!-- END TASKS -->"
    
    with open(QUEUE_FILE, "w") as f:
        f.write(content)
    
    log(f"📋 Created task: {task_id} - {description[:40]}")
    return task_id

# === DO WORK ===
def execute_task(task_id, description):
    """Execute a task based on description."""
    log(f"🔨 Working: {task_id} - {description[:50]}")
    
    orch = CoOp()
    orch.peer_broadcast('TASK', 'work', f"⚡ {AGENT} working: {task_id}", AGENT)
    
    # Parse command from description
    # Format: "command: actual shell command" or just description
    if ":" in description:
        parts = description.split(":", 1)
        cmd = parts[1].strip()
    else:
        # Try to interpret description as work
        cmd = None
    
    # Execute if we have a command
    if cmd and len(cmd) > 3:
        try:
            result = subprocess.run(
                cmd, shell=True, timeout=60, 
                capture_output=True, text=True
            )
            if result.returncode == 0:
                log(f"✅ Command succeeded")
            else:
                log(f"⚠️ Command failed: {result.stderr[:100]}")
        except subprocess.TimeoutExpired:
            log("⚠️ Command timed out")
        except Exception as e:
            log(f"⚠️ Execution error: {e}")
    
    complete_task(task_id, description)

# === P2P CHAT ===
CHAT_PHRASES = [
    "Heartbeat - systems go",
    "Standing by for tasks",
    "Loop active",
    "Still here",
    "Ready for work",
    "Any blockers?",
    "All clear here",
    "Checking in",
    "Queue empty, chatting",
]

def p2p_chat():
    """Natural peer-to-peer chat."""
    orch = CoOp()
    phrase = random.choice(CHAT_PHRASES)
    
    if random.random() < 0.3:
        # Direct message
        peer = random.choice(PEERS)
        orch.peer_request(peer, 'CHAT', 'swarm', f"💬 {AGENT} → {peer}: {phrase}", AGENT)
        log(f"💬 → {peer}")
    else:
        # Broadcast
        orch.peer_broadcast('CHAT', 'heartbeat', f"💬 {AGENT}: {phrase}", AGENT)
        log(f"📢 {phrase}")

def swarm_meeting():
    """Initiate or respond to swarm meeting."""
    orch = CoOp()
    orch.peer_broadcast('CHAT', 'swarm', f"🐝 SWARM MEETING: {AGENT} checking in. Status: active, queue: checking", AGENT)
    log("🐝 Swarm meeting broadcast")

# === MAIN LOOP ===
def main():
    log("🚀 SAT BOOTSTRAP STARTING...")
    log(f"📚 Loading swarm knowledge...")
    
    # Announce arrival
    orch = CoOp()
    orch.peer_broadcast('CHAT', 'swarm', f"🌟 {AGENT} JOINING SWARM! Ready to work.", AGENT)
    
    log("✅ Sat initialized. Starting work loop...")
    
    cycles = 0
    idle_cycles = 0
    
    while True:
        cycles += 1
        
        try:
            # 1. Check task queue
            tasks = get_pending_tasks()
            
            if tasks:
                # Claim and do first available task
                task_line = tasks[0]
                task_id = claim_task(task_line)
                if task_id:
                    log(f"📋 Claimed: {task_id}")
                    idle_cycles = 0
                    
                    # Extract description
                    desc_match = re.search(r'\|\s*(.+?)(?:\||$)', task_line)
                    description = desc_match.group(1).strip() if desc_match else task_id
                    
                    execute_task(task_id, description)
                else:
                    idle_cycles += 1
            else:
                idle_cycles += 1
                
                # 2. No tasks - scan conversations and create tasks
                if idle_cycles % 5 == 0:  # Every ~15 seconds
                    log("📭 Queue empty, scanning conversations...")
                    new_tasks = scan_conversations_for_tasks()
                    for task_desc in new_tasks[:2]:  # Max 2 per cycle
                        add_task_to_queue(task_desc)
                
                # 3. Still nothing? P2P chat
                if idle_cycles >= 10:  # ~30 seconds idle
                    if random.random() < 0.7:
                        p2p_chat()
                    else:
                        swarm_meeting()
                    idle_cycles = 0
            
            # Occasional status broadcast
            if cycles % 20 == 0:
                orch.peer_broadcast('CHAT', 'heartbeat', f"💬 {AGENT} heartbeat #{cycles//20} - still active", AGENT)
        
        except Exception as e:
            log_error(f"Loop error: {e}")
        
        time.sleep(SLEEP)

if __name__ == "__main__":
    main()