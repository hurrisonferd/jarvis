#!/usr/bin/env python3
"""
Autonomous Agent Loop — Makes satellites actually work.

Usage:
    python agent_loop.py Lilith          # Infinite loop
    python agent_loop.py Shaka --once    # Run one cycle, then exit
    python agent_loop.py Stella --debug  # Verbose output

Options:
    --once      Run one cycle and exit
    --debug     Verbose logging
    --interval  Seconds between cycles (default: 30)
"""

import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

AGENT = sys.argv[1] if len(sys.argv) > 1 else "Lilith"
ONCE_MODE = "--once" in sys.argv
DEBUG = "--debug" in sys.argv
LOOP_INTERVAL = 30
HEARTBEAT_INTERVAL = 5  # minutes between heartbeats

# Parse interval
for i, arg in enumerate(sys.argv):
    if arg == "--interval" and i + 1 < len(sys.argv):
        LOOP_INTERVAL = int(sys.argv[i + 1])

cycles_since_heartbeat = 0


def log(msg, debug=False):
    """Log with timestamp."""
    if debug and not DEBUG:
        return
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    print(f"[{ts}] [{AGENT}] {msg}")


def git_sync():
    """Pull latest from git."""
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            capture_output=True, text=True, timeout=30
        )
        if "Already up to date" not in result.stdout:
            log("📥 Pulled new changes")
            return True
    except Exception as e:
        log(f"⚠️ Git sync error: {e}", debug=True)
    return False


def read_commands():
    """Read pending commands for this agent."""
    path = Path(f"workspaces/Co-op/tasks/commands/{AGENT.upper()}.md")
    if not path.exists():
        return []
    
    with open(path) as f:
        content = f.read()
    
    commands = []
    for section in content.split("## ["):
        if "] Command from dispatcher" in section:
            marker = "] Command from dispatcher\n\n"
            if marker in section:
                cmd = section.split(marker, 1)[1].split("---")[0].strip()
                commands.append(cmd)
    
    return commands


def clear_commands():
    """Clear command file."""
    path = Path(f"workspaces/Co-op/tasks/commands/{AGENT.upper()}.md")
    if path.exists():
        path.unlink()


def send_heartbeat(orch):
    """Post heartbeat to MARCO-POLO to signal agent is alive."""
    orch.peer_broadcast("HEARTBEAT", "system", f"{AGENT} is alive. Watching for tasks.", AGENT)


def run_cycle(orch, sender, tasks_done):
    """Run one agent cycle."""
    global cycles_since_heartbeat
    log("Starting cycle...", debug=True)
    
    # 1. Git sync
    git_sync()
    
    # 2. Check for commands
    commands = read_commands()
    if commands:
        log(f"📨 Got {len(commands)} command(s)")
        for cmd in commands:
            log(f"   → {cmd[:60]}...")
        clear_commands()
    
    # 3. Check P2P messages - respond to peer requests
    p2p_messages = orch.peer_check(AGENT, since_minutes=5)
    for msg in p2p_messages:
        log(f"📡 P2P [{msg['type']}] from {msg['from']}: {msg['message'][:50]}...")
        if msg['type'] == 'HELP':
            # Respond with backup offer
            orch.peer_request(msg['from'], 'BACKUP', msg['task'], 
                            f"Can help with {msg['task']} - what's the issue?", AGENT)
        elif msg['type'] == 'DELEGATE':
            # Claim the delegated task
            orch.claim(AGENT)
            orch.peer_request(msg['from'], 'CLAIMED', msg['task'],
                            f"Taking over: {msg['message']}", AGENT)
        elif msg['type'] == 'ASK':
            # Auto-respond if we know the answer
            if 'git' in msg['message'].lower():
                orch.peer_request(msg['from'], 'ANSWER', msg['task'],
                                "Try: git pull origin main", AGENT)
    
    # 4. Check queue state
    running = orch.queue.get_running()
    queued = orch.queue.get_queued()
    log(f"State: {len(running)} running, {len(queued)} queued", debug=True)
    
    # 4. Claim a task if queue has items
    if queued:
        log("📋 Claiming next task...")
        try:
            result = orch.claim(AGENT)
            if result.get("task"):
                task = result["task"]
                log(f"🎯 Claimed: {task.description[:50]}...")
                
                # Dispatch to sandbox
                if sender:
                    resp = sender.send_task(
                        task=task.description,
                        repo="hurrisonferd/Jarvis-Private",
                        branch="main"
                    )
                    conv_id = resp.get("conversation_id")
                    log(f"🚀 Dispatched to sandbox: {conv_id}")
                    orch.release(task.id, f"Dispatched to {conv_id}")
                else:
                    orch.release(task.id, "Completed")
                
                tasks_done += 1
                log(f"✅ Tasks completed: {tasks_done}")
            else:
                log("📭 Queue empty (race condition)")
        except Exception as e:
            log(f"⚠️ Task error: {e}")
    else:
        log("📋 Queue empty")
    
    return tasks_done


def main():
    log(f"Starting agent loop (interval: {LOOP_INTERVAL}s, once={ONCE_MODE})")
    
    try:
        from coop_orchestrator import CoOpOrchestrator
        from lilith_task_sender import LilithTaskSender
    except Exception as e:
        log(f"❌ Import error: {e}")
        sys.exit(1)
    
    orch = CoOpOrchestrator()
    sender = LilithTaskSender() if AGENT == "Lilith" else None
    tasks_done = 0
    
    while True:
        try:
            tasks_done = run_cycle(orch, sender, tasks_done)
            
            if ONCE_MODE:
                log("✅ One shot complete, exiting")
                break
            
            # Broadcast status every 5 tasks
            if tasks_done > 0 and tasks_done % 5 == 0:
                queued = orch.queue.get_queued()
                orch.broadcast(AGENT, f"Status: {tasks_done} tasks done. Queue: {len(queued)} pending.")
            
            # Heartbeat every HEARTBEAT_INTERVAL minutes
            cycles_since_heartbeat += 1
            if cycles_since_heartbeat >= (HEARTBEAT_INTERVAL * 60 // LOOP_INTERVAL):
                send_heartbeat(orch)
                cycles_since_heartbeat = 0
                log("💓 Heartbeat sent")
            
            log(f"😴 Sleeping {LOOP_INTERVAL}s...")
            time.sleep(LOOP_INTERVAL)
            
        except KeyboardInterrupt:
            log("⏹️ Stopped by user")
            break
        except Exception as e:
            log(f"⚠️ Cycle error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()