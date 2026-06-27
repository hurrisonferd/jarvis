#!/usr/bin/env python3
"""
Autonomous Agent Loop — Makes satellites actually work.

Usage:
    python agent_loop.py Lilith
    python agent_loop.py Shaka
    python agent_loop.py Stella

This runs an infinite loop:
1. Git sync (pull latest state)
2. Check MARCO-POLO (see who's on what)
3. Check commands (any orders?)
4. Check queue (claim next task)
5. Execute (dispatch to sandbox)
6. Broadcast results
7. Sleep 30s, repeat
"""

import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from coop_orchestrator import CoOpOrchestrator
from lilith_task_sender import LilithTaskSender

AGENT = sys.argv[1] if len(sys.argv) > 1 else "Lilith"
LOOP_INTERVAL = 30  # seconds between checks


def log(msg):
    """Log with timestamp."""
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
    except:
        pass
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
        if "] Command from" in section:
            cmd = section.split("]\n", 1)[1].split("---")[0].strip()
            commands.append(cmd)
    
    return commands


def clear_commands():
    """Clear command file."""
    path = Path(f"workspaces/Co-op/tasks/commands/{AGENT.upper()}.md")
    if path.exists():
        path.unlink()


def broadcast(orch, message):
    """Broadcast to MARCO-POLO."""
    orch.broadcast(message, AGENT)


def main():
    log(f"Starting autonomous loop (interval: {LOOP_INTERVAL}s)")
    orch = CoOpOrchestrator()
    sender = LilithTaskSender() if AGENT == "Lilith" else None
    
    tasks_done = 0
    
    while True:
        try:
            # 1. Git sync
            git_sync()
            
            # 2. Check for commands
            commands = read_commands()
            if commands:
                log(f"📨 Got {len(commands)} command(s)")
                for cmd in commands:
                    log(f"   → {cmd[:60]}...")
                clear_commands()
            
            # 3. Do pre-diff check
            running = orch.queue.get_running()
            queued = orch.queue.get_queued()
            
            # 4. Claim a task if none running and queue has items
            if not running and queued:
                log("📋 Claiming next task...")
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
                        # Just mark as done (no sandbox for Shaka/Stella)
                        orch.release(task.id, "Completed")
                    
                    tasks_done += 1
                    log(f"✅ Tasks completed: {tasks_done}")
                else:
                    log("📭 Queue empty")
            elif not queued:
                log("📋 Queue empty, checking again soon...")
            
            # 5. Post check-in to MARCO-POLO (every 5 cycles)
            if tasks_done > 0 and tasks_done % 5 == 0:
                broadcast(orch, f"Status: {tasks_done} tasks done. Queue: {len(queued)} pending.")
            
            log(f"😴 Sleeping {LOOP_INTERVAL}s...")
            time.sleep(LOOP_INTERVAL)
            
        except KeyboardInterrupt:
            log("⏹️ Stopped")
            break
        except Exception as e:
            log(f"⚠️ Error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()