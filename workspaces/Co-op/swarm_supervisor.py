#!/usr/bin/env python3
"""
Swarm Supervisor - Monitors and auto-restarts agent loops.
Runs as a daemon process to keep the swarm alive.
"""
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

AGENTS = ["Shaka", "Stella"]
CHECK_INTERVAL = 20  # seconds between checks
LOG_FILE = "/tmp/swarm_supervisor.log"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def is_process_running(agent):
    """Check if agent loop is running."""
    result = subprocess.run(
        ["pgrep", "-f", f"agent_loop.py {agent}"],
        capture_output=True
    )
    return result.returncode == 0

def restart_agent(agent):
    """Restart an agent's chat loop."""
    log(f"🔄 Restarting {agent}...")
    os.chdir("/workspace/project/Jarvis-Private")
    
    # Kill existing
    subprocess.run(["pkill", "-f", f"chat_loop.py {agent}"], capture_output=True)
    subprocess.run(["pkill", "-f", f"agent_loop.py {agent}"], capture_output=True)
    time.sleep(1)
    
    # Restart with chat_loop.py (5s interval - constant chatter)
    cmd = f"cd /workspace/project/Jarvis-Private && git pull && python workspaces/Co-op/chat_loop.py {agent} &"
    os.system(cmd)
    log(f"✅ {agent} restarted (chat loop)")

def main():
    log("🐝 SWARM SUPERVISOR starting...")
    
    while True:
        ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
        
        for agent in AGENTS:
            if not is_process_running(agent):
                log(f"⚠️ {agent} not running - restarting...")
                restart_agent(agent)
            else:
                log(f"✅ {agent} alive")
        
        log(f"🐝 Supervisor heartbeat #{ts}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()