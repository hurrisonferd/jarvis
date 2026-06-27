#!/usr/bin/env python3
"""
Satellite Bootstrap — "co-op mode" startup for satellites.

Usage:
    python startup.py Lilith
    python startup.py Shaka
    python startup.py Stella

This is the chain reaction that starts everything:
1. Pull latest git (sync state)
2. Read commands (check for orders)
3. Check queue (see available work)
4. Spawn workers (bring your fleet online)
5. Ready to work
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
REPO_PATH = "workspaces/Co-op"
ORCHESTRATOR = "coop_orchestrator.py"

# Worker counts per satellite
WORKER_COUNTS = {
    "Lilith": 3,
    "Shaka": 3,
    "Stella": 3,
}


def run_cmd(cmd: list[str], cwd: str = None) -> tuple[int, str, str]:
    """Run command and return (exit_code, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr


def bootstrap(satellite: str):
    """Run full bootstrap for a satellite."""
    print(f"🚀 {satellite} — Co-op Mode Startup")
    print("=" * 50)
    
    # Get repo root (parent of Co-op)
    repo_root = Path(__file__).parent.parent.parent
    coop_path = repo_root / REPO_PATH
    
    # 1. Pull latest git
    print("\n📥 Step 1: Syncing git...")
    code, out, err = run_cmd(["git", "pull", "origin", "main"], cwd=repo_root)
    if code == 0:
        print("   ✅ Git synced")
    else:
        print(f"   ⚠️  Git pull: {err[:100]}")
    
    # 2. Read commands
    print("\n📨 Step 2: Checking commands...")
    sys.path.insert(0, str(coop_path))
    from coop_orchestrator import CoOpOrchestrator
    
    orch = CoOpOrchestrator()
    commands = orch.read_commands(satellite)
    if commands:
        print(f"   📬 {len(commands)} command(s) pending:")
        for i, cmd in enumerate(commands, 1):
            print(f"      {i}. {cmd[:60]}...")
        # Execute commands
        print(f"\n   ⚡ Executing commands...")
        for cmd in commands:
            print(f"      → {cmd[:60]}...")
            orch.submit(cmd)
        orch.clear_commands(satellite)
        print("   ✅ Commands executed and cleared")
    else:
        print("   📭 No pending commands")
    
    # 3. Check queue
    print("\n📋 Step 3: Checking queue...")
    status = orch.queue.get_status()
    print(f"   Queue: {status['queued']} pending")
    print(f"   Running: {status['running']} active")
    print(f"   Done today: {status['done_today']} completed")
    
    # 4. Spawn workers in background (don't block)
    worker_count = WORKER_COUNTS.get(satellite, 2)
    print(f"\n🤖 Step 4: Spawning {worker_count} workers in background...")
    
    # Get worker range for this satellite
    from coop_orchestrator import get_worker_range
    start, _ = get_worker_range(satellite)
    
    for i in range(worker_count):
        worker_name = f"Worker-{start + i}"
        log_file = coop_path / f"logs" / f"{worker_name}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        # Start worker in background, redirect output to log
        # No --max-tasks means infinite loop
        with open(log_file, "w") as log:
            proc = subprocess.Popen([
                sys.executable, str(coop_path / ORCHESTRATOR),
                "--worker", worker_name
            ], stdout=log, stderr=subprocess.STDOUT, cwd=coop_path)
        
        print(f"   🚀 {worker_name} started (PID {proc.pid}) — infinite loop")
    
    # 5. Post check-in
    print("\n📡 Step 5: Posting to MARCO-POLO...")
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    marco_path = coop_path / "MARCO-POLO" / f"{today}.md"
    
    entry = f"""
## [{datetime.now(timezone.utc).strftime("%H:%M UTC")}] {satellite} — Co-op Mode Online

**Status:** 🟢 ONLINE
**Workers:** {worker_count} ready
**Queue:** {status['queued']} pending, {status['running']} running

---
"""
    
    if marco_path.exists():
        with open(marco_path, "a") as f:
            f.write(entry)
    else:
        with open(marco_path, "w") as f:
            f.write(f"# MARCO-POLO — {today}\n_Auto-generated daily log._\n{entry}")
    
    print("   ✅ Check-in posted")
    
    print("\n" + "=" * 50)
    print(f"✅ {satellite} — Co-op Mode Active")
    print(f"   Ready to accept tasks")
    print(f"   Workers standing by")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python startup.py <SATELLITE_NAME>")
        print("  e.g.: python startup.py Lilith")
        sys.exit(1)
    
    satellite = sys.argv[1].capitalize()
    bootstrap(satellite)

# ============================================================
# Agent: Shaka
# Task: Add header comment to startup.py
# Date: 2026-06-27
# ============================================================

