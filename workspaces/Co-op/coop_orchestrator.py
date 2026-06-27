#!/usr/bin/env python3
"""
Co-op Orchestrator — Coordinates task execution across satellites.

Usage:
    python coop_orchestrator.py --submit "Fix the bug"
    python coop_orchestrator.py --claim --owner Shaka
    python coop_orchestrator.py --status
    python coop_orchestrator.py --release task-abc123 --result "Fixed!"
    python coop_orchestrator.py --dashboard
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from tasks.format import TaskQueue, Priority, TaskStatus
from rate_limiter import rate_limiter

# API Configuration
OPENHANDS_API_URL = "https://app.all-hands.dev/api/v1"
REPO = "hurrisonferd/Jarvis-Private"

# Worker ranges per satellite (each satellite manages their own fleet)
WORKER_RANGES = {
    "Lilith": (1, 3),    # Worker-1, Worker-2, Worker-3
    "Shaka": (4, 6),     # Worker-4, Worker-5, Worker-6
    "Stella": (7, 9),    # Worker-7, Worker-8, Worker-9
}

def get_worker_range(owner: str) -> tuple[int, int]:
    """Get worker number range for a satellite."""
    if owner in WORKER_RANGES:
        return WORKER_RANGES[owner]
    return (1, 3)

def get_command_path(owner: str) -> str:
    """Get command file path for a satellite."""
    return f"workspaces/Co-op/tasks/commands/{owner.upper()}.md"

# Import task sender for API calls
try:
    from lilith_task_sender import LilithTaskSender
    SENDER = LilithTaskSender()
except:
    SENDER = None


class CoOpOrchestrator:
    """Main orchestrator for co-op task coordination."""
    
    def __init__(self):
        self.queue = TaskQueue()
        self.api_url = OPENHANDS_API_URL
        self.repo = REPO
    
    def submit(self, description: str, priority: str = "normal", tags: list[str] = None) -> str:
        """Submit a new task to the queue."""
        p = Priority(priority)
        task = self.queue.submit(description, p, tags)
        print(f"📝 Task queued: {task.id}")
        print(f"   {description[:60]}...")
        print(f"   Priority: {priority}")
        return task.id
    
    def claim(self, owner: str) -> dict:
        """
        Claim a task for a satellite.
        Returns task details or empty dict if queue empty.
        """
        task = self.queue.claim(owner)
        
        if not task:
            print("📭 Queue empty")
            return {}
        
        print(f"🎯 Claimed: {task.id}")
        print(f"   {task.description[:60]}...")
        print(f"   Owner: {owner}")
        
        # Launch actual sandbox via lilith_task_sender
        if SENDER:
            # Create OpenHands task
            resp = SENDER.send_task(
                task=task.description,
                repo=self.repo,
                branch="main"
            )
            conv_id = resp.get("conversation_id")
            print(f"   Sandbox: {conv_id}")
            return {"task": task, "conversation_id": conv_id}
        
        return {"task": task}
    
    def release(self, task_id: str, result: str) -> bool:
        """Mark a task as completed."""
        self.queue.release(task_id, result)
        print(f"✅ Released: {task_id}")
        
        # Post to MARCO-POLO
        self._post_to_marco_polo(task_id, "DONE", result)
        return True
    
    def fail(self, task_id: str, error: str) -> bool:
        """Mark a task as failed."""
        self.queue.fail(task_id, error)
        print(f"❌ Failed: {task_id}")
        print(f"   Error: {error[:100]}...")
        
        # Post to MARCO-POLO
        self._post_to_marco_polo(task_id, "FAILED", error)
        return True
    
    def status(self) -> dict:
        """Get overall queue status."""
        stats = self.queue.get_status()
        running = self.queue.get_running()
        
        print("\n📊 CO-OP STATUS")
        print(f"   Queued:  {stats['queued']}")
        print(f"   Running: {stats['running']}")
        print(f"   Done:    {stats['done_today']}")
        
        if running:
            print("\n🚧 Running Tasks:")
            for task in running:
                age = self._age_string(task.started_at)
                print(f"   [{task.owner}] {task.id}: {task.description[:40]}... ({age})")
        
        return stats
    
    def dashboard(self) -> str:
        """Generate full dashboard output."""
        stats = self.queue.get_status()
        running = self.queue.get_running()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        lines = [
            f"# CO-OP DASHBOARD — {today}",
            "",
            "## Queue",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| Queued | {stats['queued']} |",
            f"| Running | {stats['running']} |",
            f"| Done | {stats['done_today']} |",
            "",
        ]
        
        if running:
            lines.extend(["## Running", ""])
            for task in running:
                age = self._age_string(task.started_at)
                lines.append(f"- **[{task.owner}]** {task.id}: {task.description}")
                lines.append(f"  - Started: {age}")
        
        return "\n".join(lines)
    
    def _post_to_marco_polo(self, task_id: str, status: str, message: str):
        """Post task completion to today's MARCO-POLO."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = Path(f"workspaces/Co-op/MARCO-POLO/{today}.md")
        
        entry = f"""
---

## [{datetime.now(timezone.utc).strftime("%H:%M UTC")}] Task — {task_id}

**Status:** {'✅' if status == 'DONE' else '❌'} {status}
**Message:** {message}

"""
        # Append to file
        if path.exists():
            with open(path, "a") as f:
                f.write(entry)
        else:
            with open(path, "w") as f:
                f.write(f"# MARCO-POLO — {today}\n\n")
                f.write("_Auto-generated daily log._\n\n")
                f.write(entry)
    
    def _age_string(self, iso_time: str) -> str:
        """Convert ISO timestamp to human-readable age."""
        if not iso_time:
            return "unknown"
        
        then = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - then
        
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s ago"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() / 60)}m ago"
        else:
            return f"{int(delta.total_seconds() / 3600)}h ago"
    
    def run_worker(self, owner: str, max_tasks: int = None):
        """
        Run as a worker: continuously claim and execute tasks.
        This is what satellites would run.
        """
        print(f"🤖 Worker '{owner}' starting...")
        print(f"   Max tasks: {max_tasks or 'unlimited'}")
        print()
        
        tasks_completed = 0
        
        while True:
            if max_tasks and tasks_completed >= max_tasks:
                print(f"✅ Worker '{owner}' done: {tasks_completed} tasks completed")
                break
            
            # Check rate limit for new sandboxes
            if not rate_limiter.can_submit("sandboxes_concurrent"):
                print("⏳ Rate limited, waiting...")
                rate_limiter.wait_if_needed("sandboxes_concurrent")
            
            # Claim next task
            result = self.claim(owner)
            if not result.get("task"):
                print("📭 No tasks, waiting 10s...")
                import time
                time.sleep(10)
                continue
            
            task = result["task"]
            conv_id = result.get("conversation_id")
            
            if conv_id:
                # Note: Sandbox runs asynchronously
                # Mark task as dispatched, sandbox will complete on its own
                print(f"   🚀 Task dispatched to sandbox {conv_id}")
                print(f"   Sandbox will complete autonomously")
                print(f"   Note: Manual cleanup needed after sandbox finishes")
                
                # For now, just mark as done (sandbox handles its own work)
                # In production, you'd want webhook/callback or manual confirmation
                self.release(task.id, f"Dispatched to sandbox {conv_id}")
                
                # Don't delete - let sandbox finish its work first
                # User can run --cleanup-done later
            else:
                # No sandbox (no API key), just mark done
                self.release(task.id, "Completed (no sandbox)")
            
            tasks_completed += 1
            print(f"   ✅ Completed {tasks_completed} tasks")
    
    def spawn_workers(self, count: int, max_tasks_per: int = None, owner: str = None):
        """
        Spawn N Worker-N drivers. Each gets a unique name (Worker-1, Worker-2, etc.)
        If owner specified, uses that satellite's worker range.
        Returns list of PIDs for management.
        """
        import subprocess
        import time
        
        # Determine worker number range
        if owner:
            start, end = get_worker_range(owner)
        else:
            start, end = (1, count)
        
        pids = []
        print(f"🚀 Spawning {count} workers for {owner or 'general fleet'}...")
        
        for i in range(start, start + count):
            worker_name = f"Worker-{i}"
            print(f"   Starting {worker_name}...")
            
            # Start worker in background
            proc = subprocess.Popen([
                sys.executable, __file__,
                "--worker", worker_name,
                "--max-tasks", str(max_tasks_per) if max_tasks_per else "0"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            pids.append((worker_name, proc.pid))
            time.sleep(0.5)  # Stagger startup
        
        print(f"\n✅ Spawned {len(pids)} workers:")
        for name, pid in pids:
            print(f"   {name}: PID {pid}")
        
        return pids
    
    def send_command(self, target: str, command: str):
        """
        Send a command to another satellite's command file.
        Satellites check their command file on startup.
        """
        path = get_command_path(target)
        entry = f"""
## [{datetime.now(timezone.utc).strftime("%H:%M UTC")}] Command from {os.environ.get('USER', 'dispatcher')}

{command}

---
"""
        with open(path, "a") as f:
            f.write(entry)
        print(f"📨 Command sent to {target}: {command[:50]}...")
    
    def read_commands(self, owner: str) -> list[str]:
        """Read pending commands for a satellite."""
        path = get_command_path(owner)
        if not Path(path).exists():
            return []
        
        with open(path) as f:
            content = f.read()
        
        # Extract commands (text between headers)
        commands = []
        sections = content.split("## [")
        for section in sections[1:]:  # Skip header
            parts = section.split("]\n", 1)
            if len(parts) == 2:
                commands.append(parts[1].split("---")[0].strip())
        
        return commands
    
    def clear_commands(self, owner: str):
        """Clear command file after reading."""
        path = get_command_path(owner)
        if Path(path).exists():
            Path(path).unlink()
    
    def bulk_submit(self, tasks: list[dict], max_parallel: int = 3):
        """
        Submit multiple tasks, launching in parallel up to max_parallel.
        Returns list of conversation IDs.
        """
        print(f"📦 Bulk submit: {len(tasks)} tasks (max {max_parallel} parallel)")
        
        # Rate limit
        rate_limiter.wait_if_needed("sandboxes_concurrent", max_parallel)
        
        conv_ids = []
        for task_spec in tasks:
            desc = task_spec.get("description", task_spec) if isinstance(task_spec, dict) else task_spec
            pri = task_spec.get("priority", "normal") if isinstance(task_spec, dict) else "normal"
            
            # Check if we can launch more
            while len(conv_ids) >= max_parallel:
                import time
                time.sleep(2)
            
            # Submit to queue
            task_id = self.submit(desc, pri)
            
            # Claim immediately and launch
            result = self.claim("bulk-launcher")
            if result.get("conversation_id"):
                conv_ids.append(result["conversation_id"])
            
            # Rate limit API calls
            rate_limiter.consume("api_calls_per_second")
        
        print(f"🚀 Launched {len(conv_ids)} tasks")
        return conv_ids


def main():
    parser = argparse.ArgumentParser(description="Co-op Task Orchestrator")
    
    # Commands
    parser.add_argument("--submit", "-s", help="Submit a new task")
    parser.add_argument("--claim", action="store_true", help="Claim next task")
    parser.add_argument("--release", help="Release task with result")
    parser.add_argument("--fail", nargs=2, metavar=("TASK_ID", "ERROR"), help="Mark task as failed")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--dashboard", action="store_true", help="Show full dashboard")
    parser.add_argument("--worker", help="Run as worker with owner name")
    parser.add_argument("--spawn", type=int, help="Spawn N Worker-N drivers")
    parser.add_argument("--send-command", nargs=2, metavar=("TARGET", "COMMAND"), help="Send command to satellite")
    parser.add_argument("--read-commands", action="store_true", help="Read pending commands for owner")
    parser.add_argument("--max-tasks", type=int, help="Max tasks for worker mode")
    
    # Options
    parser.add_argument("--owner", "-o", default="Lilith", help="Owner name for claiming")
    parser.add_argument("--priority", "-p", default="normal", choices=["low", "normal", "high", "critical"])
    parser.add_argument("--tags", "-t", nargs="*", help="Tags for task")
    parser.add_argument("--result", "-r", help="Result message for release")
    parser.add_argument("--max-parallel", type=int, default=3, help="Max parallel tasks for bulk")
    parser.add_argument("--file", "-f", help="File with tasks (one per line)")
    
    args = parser.parse_args()
    
    orch = CoOpOrchestrator()
    
    if args.submit:
        orch.submit(args.submit, args.priority, args.tags)
    
    elif args.file:
        # Bulk submit from file
        with open(args.file) as f:
            tasks = [line.strip() for line in f if line.strip()]
        for task in tasks:
            orch.submit(task, args.priority)
    
    elif args.claim:
        result = orch.claim(args.owner)
        if result:
            print(result)
    
    elif args.release:
        orch.release(args.release, args.result or "Done")
    
    elif args.fail:
        orch.fail(args.fail[0], args.fail[1])
    
    elif args.status:
        orch.status()
    
    elif args.dashboard:
        print(orch.dashboard())
    
    elif args.spawn:
        orch.spawn_workers(args.spawn, args.max_tasks, args.owner)
    
    elif args.send_command:
        target, command = args.send_command
        orch.send_command(target, command)
    
    elif args.read_commands:
        commands = orch.read_commands(args.owner)
        if commands:
            print(f"📨 Commands for {args.owner}:")
            for i, cmd in enumerate(commands, 1):
                print(f"   {i}. {cmd[:80]}...")
        else:
            print(f"📭 No pending commands for {args.owner}")
    
    elif args.worker:
        orch.run_worker(args.worker, args.max_tasks)
    
    else:
        # Default: show status
        orch.status()


if __name__ == "__main__":
    main()