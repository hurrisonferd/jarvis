#!/usr/bin/env python3
"""
Sat — Natural language satellite commands.

Usage:
    python sat.py "Sat Status?"
    python sat.py "Tell Stella to refactor auth"
    python sat.py "Queue?"
    python sat.py "Spawn 2 workers"
"""

import re
import sys
from pathlib import Path

# Add coop to path
sys.path.insert(0, str(Path(__file__).parent))

from coop_orchestrator import CoOpOrchestrator
from tasks.format import TaskQueue


def natural_command(text: str, owner: str = "Lilith"):
    """Parse and execute natural language commands."""
    orch = CoOpOrchestrator()
    text = text.strip()
    
    # Net Status? — fleet overview
    if re.match(r"(net|sat|network)\s*status", text, re.I) or text in ["net?", "fleet?"]:
        return fleet_status(orch)
    
    # Queue? — pending tasks
    if text in ["queue?", "q?"] or re.match(r"show\s*queue", text, re.I):
        return queue_status(orch)
    
    # Tell X to Y — send command to satellite
    match = re.match(r"tell\s+(\w+)\s+to\s+(.+)", text, re.I)
    if match:
        target, command = match.groups()
        orch.send_command(target.capitalize(), command)
        return f"📨 Sent to {target.capitalize()}: {command}"
    
    # Ask X — send question to satellite
    match = re.match(r"ask\s+(\w+)\s+(.+)", text, re.I)
    if match:
        target, question = match.groups()
        orch.send_command(target.capitalize(), question)
        return f"📨 Asked {target.capitalize()}: {question}"
    
    # Spawn N workers
    match = re.match(r"spawn\s+(\d+)\s+workers?", text, re.I)
    if match:
        count = int(match.group(1))
        orch.spawn_workers(count, max_tasks_per=5, owner=owner)
        return f"🤖 Spawned {count} workers for {owner}"
    
    # Worker N do X — direct worker command
    match = re.match(r"worker[- ]?(\d+)\s+(do|run|execute)?\s*(.+)", text, re.I)
    if match:
        worker_num, _, task = match.groups()
        orch.submit(f"Worker-{worker_num}: {task}", owner=owner)
        return f"📝 Task for Worker-{worker_num}: {task}"
    
    # Check X? — read satellite status
    match = re.match(r"check\s+(\w+)\?", text, re.I)
    if match:
        target = match.group(1).capitalize()
        commands = orch.read_commands(target)
        status = "📭 No pending" if not commands else f"📬 {len(commands)} commands"
        return f"{target}: {status}"
    
    # Who is online? — fleet check
    if re.match(r"who\s+(is|are)\s+online", text, re.I):
        return fleet_online(orch)
    
    # Dashboard
    if text in ["dashboard", "dash"]:
        return orch.dashboard()
    
    # Default: submit as task
    orch.submit(text)
    return f"📝 Queued: {text[:50]}..."


def fleet_status(orch: CoOpOrchestrator):
    """Show full fleet status."""
    status = orch.queue.get_status()
    running = orch.queue.get_running()
    
    lines = [
        "📡 FLEET STATUS",
        f"   Queue: {status['queued']} pending",
        f"   Running: {status['running']} active",
        f"   Done: {status['done_today']} today",
        "",
    ]
    
    if running:
        lines.append("   🚧 Active tasks:")
        for task in running:
            lines.append(f"      [{task.owner}] {task.id}: {task.description[:40]}...")
    
    return "\n".join(lines)


def queue_status(orch: CoOpOrchestrator):
    """Show queue contents."""
    queue_dir = Path("workspaces/Co-op/tasks/queue")
    files = list(queue_dir.glob("*.yaml"))
    
    if not files:
        return "📭 Queue empty"
    
    lines = [f"📋 QUEUE ({len(files)} tasks):"]
    for f in files:
        task = orch.queue._load_task(f)
        if task:
            lines.append(f"   • {task.description[:50]}... [{task.priority.value}]")
    
    return "\n".join(lines)


def fleet_online(orch: CoOpOrchestrator):
    """Check which satellites are online."""
    # Read MARCO-POLO for recent check-ins
    today = orch._get_today_path()
    if not today.exists():
        return "📭 No MARCO-POLO today"
    
    return "🟢 All satellites synced via git\n   Check MARCO-POLO for last check-in times"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sat.py \"command\"")
        print("  e.g.: python sat.py \"Sat Status?\"")
        sys.exit(1)
    
    # Get owner from env or default
    owner = sys.argv[2] if len(sys.argv) > 2 else "Lilith"
    
    result = natural_command(sys.argv[1], owner)
    print(result)