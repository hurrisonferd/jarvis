#!/usr/bin/env python3
"""
Co-op Orchestrator — Coordinates task execution across satellites.

The orchestrator manages a distributed task queue where multiple satellite
agents can submit, claim, and complete tasks. It integrates with OpenHands
sandboxes for task execution and maintains a log (MARCO-POLO) of all
completed work.

Usage:
    python coop_orchestrator.py --submit "Fix the bug"
    python coop_orchestrator.py --claim --owner Shaka
    python coop_orchestrator.py --status
    python coop_orchestrator.py --release task-abc123 --result "Fixed!"
    python coop_orchestrator.py --dashboard
    python coop_orchestrator.py --spawn 3 --owner Lilith
    python coop_orchestrator.py --send-command Shaka "Review PR #42"

Worker Ranges:
    - Lilith: Workers 1-3
    - Shaka: Workers 4-6
    - Stella: Workers 7-9
"""

import argparse
import os
import sys
import subprocess
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
    """
    Get the worker number range for a satellite owner.

    Each satellite manages a dedicated fleet of workers identified by
    sequential numbers. This function maps an owner name to their
    assigned worker number range.

    Args:
        owner: The satellite owner name (e.g., "Lilith", "Shaka", "Stella").
            Case-insensitive matching is performed against WORKER_RANGES.

    Returns:
        A tuple of (start_worker, end_worker) inclusive, representing
        the range of worker numbers assigned to the owner.
        Defaults to (1, 3) if owner is not recognized.

    Examples:
        >>> get_worker_range("Lilith")
        (1, 3)
        >>> get_worker_range("Shaka")
        (4, 6)
        >>> get_worker_range("Unknown")
        (1, 3)
    """
    if owner in WORKER_RANGES:
        return WORKER_RANGES[owner]
    return (1, 3)


def get_command_path(owner: str) -> str:
    """
    Get the file path for a satellite's command file.

    Command files are used for inter-satellite communication. Each satellite
    has a dedicated markdown file where other satellites can write commands
    that will be read on the target's next startup.

    Args:
        owner: The satellite owner name (e.g., "Lilith", "Shaka").

    Returns:
        A string path to the command file, formatted as
        "workspaces/Co-op/tasks/commands/{OWNER}.md" where OWNER is
        the owner name in uppercase.

    Examples:
        >>> get_command_path("Lilith")
        'workspaces/Co-op/tasks/commands/LILITH.md'
        >>> get_command_path("shaka")
        'workspaces/Co-op/tasks/commands/SHAKA.md'
    """
    return f"workspaces/Co-op/tasks/commands/{owner.upper()}.md"

# Import task sender for API calls
try:
    from lilith_task_sender import LilithTaskSender
    SENDER = LilithTaskSender()
except:
    SENDER = None


class CoOpOrchestrator:
    """
    Main orchestrator for co-op task coordination.

    This class manages a distributed task queue where multiple satellite
    agents can submit tasks, claim work, and report completion. It integrates
    with OpenHands sandboxes for task execution and maintains a daily log
    (MARCO-POLO) of all completed work.

    Attributes:
        queue: The TaskQueue instance managing all tasks.
        api_url: The OpenHands API endpoint URL.
        repo: The GitHub repository identifier for task execution.

    Example:
        >>> orch = CoOpOrchestrator()
        >>> task_id = orch.submit("Fix login bug", priority="high")
        >>> result = orch.claim("Lilith")
        >>> orch.release(task_id, "Fixed the bug")
    """

    def __init__(self):
        """
        Initialize the Co-op Orchestrator.

        Sets up the task queue, API URL, and repository configuration.
        The orchestrator is ready to submit, claim, and manage tasks.
        """
        self.queue = TaskQueue()
        self.api_url = OPENHANDS_API_URL
        self.repo = REPO

    def submit(self, description: str, priority: str = "normal", tags: list[str] = None) -> str:
        """
        Submit a new task to the queue.

        Adds a task to the shared task queue with the specified priority
        and optional tags. The task is assigned a unique ID and is
        immediately available for claiming by any satellite.

        Args:
            description: A human-readable description of the task to
                be performed. Will be truncated in console output.
            priority: The task priority level. Valid values are "low",
                "normal", "high", and "critical". Defaults to "normal".
            tags: Optional list of string tags for categorization and
                filtering. Defaults to None.

        Returns:
            The unique task ID (a string) assigned to the submitted task.
            This ID is required for claiming, releasing, or failing the task.

        Prints:
            Confirmation message with task ID, truncated description,
            and priority level.

        Example:
            >>> orch = CoOpOrchestrator()
            >>> task_id = orch.submit("Refactor authentication module", priority="high", tags=["security", "urgent"])
            📝 Task queued: task-abc123
               Refactor authentication module...
               Priority: high
        """
        p = Priority(priority)
        task = self.queue.submit(description, p, tags)
        print(f"📝 Task queued: {task.id}")
        print(f"   {description[:60]}...")
        print(f"   Priority: {priority}")
        return task.id

    def claim(self, owner: str) -> dict:
        """
        Claim a task for a satellite.

        Attempts to claim the next available task in the queue for the
        specified satellite owner. If a task sender is configured, also
        launches an OpenHands sandbox to execute the task.

        Args:
            owner: The name of the satellite claiming the task (e.g.,
                "Lilith", "Shaka", "Stella"). Used for tracking task
                ownership and worker assignment.

        Returns:
            A dictionary containing task information:
            - If successful with sandbox: {"task": Task, "conversation_id": str}
            - If successful without sandbox: {"task": Task}
            - If queue empty: {}

            The Task object contains at least: id, description, owner.

        Prints:
            - "📭 Queue empty" if no tasks available
            - "🎯 Claimed: {task_id}" and task details on success
            - "Sandbox: {conv_id}" if sandbox launched

        Example:
            >>> orch = CoOpOrchestrator()
            >>> result = orch.claim("Shaka")
            🎯 Claimed: task-abc123
               Refactor authentication module...
               Owner: Shaka
               Sandbox: conv-xyz789
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
        """
        Mark a task as completed.

        Removes the task from the running queue and records it as done
        with the provided result message. Also posts a completion entry
        to the daily MARCO-POLO log.

        Args:
            task_id: The unique identifier of the task to release, as
                returned by submit() or claim().
            result: A human-readable description of the task outcome,
                such as "Fixed the login bug" or "Completed successfully".

        Returns:
            Always returns True, indicating successful release.

        Prints:
            Confirmation message with task ID.

        Side Effects:
            - Updates task status in the queue to "DONE"
            - Creates/updates MARCO-POLO log entry

        Example:
            >>> orch = CoOpOrchestrator()
            >>> orch.release("task-abc123", "Fixed authentication bypass vulnerability")
            ✅ Released: task-abc123
        """
        self.queue.release(task_id, result)
        print(f"✅ Released: {task_id}")

        # Post to MARCO-POLO
        self._post_to_marco_polo(task_id, "DONE", result)
        return True

    def fail(self, task_id: str, error: str) -> bool:
        """
        Mark a task as failed.

        Records a task failure with an error description and posts the
        failure to the daily MARCO-POLO log. The task is removed from
        the running queue.

        Args:
            task_id: The unique identifier of the task that failed.
            error: A description of what went wrong, such as "Timeout
                after 10 minutes" or "API authentication failed".

        Returns:
            Always returns True, indicating the failure was recorded.

        Prints:
            Confirmation message with task ID and truncated error message.

        Side Effects:
            - Updates task status in the queue to "FAILED"
            - Creates/updates MARCO-POLO log entry with FAILED status

        Example:
            >>> orch = CoOpOrchestrator()
            >>> orch.fail("task-abc123", "OpenHands sandbox timed out")
            ❌ Failed: task-abc123
               Error: OpenHands sandbox timed out...
        """
        self.queue.fail(task_id, error)
        print(f"❌ Failed: {task_id}")
        print(f"   Error: {error[:100]}...")

        # Post to MARCO-POLO
        self._post_to_marco_polo(task_id, "FAILED", error)
        return True

    def status(self) -> dict:
        """
        Get the overall queue status.

        Retrieves current statistics about the task queue including
        counts of queued, running, and completed tasks. Also lists
        any currently running tasks with their age.

        Returns:
            A dictionary containing queue statistics:
            - "queued": Number of tasks waiting to be claimed
            - "running": Number of tasks currently being processed
            - "done_today": Number of tasks completed today

        Prints:
            Formatted status report showing queue counts and details
            of any running tasks with their owner, ID, description,
            and age since start.

        Example:
            >>> orch = CoOpOrchestrator()
            >>> stats = orch.status()

            📊 CO-OP STATUS
               Queued:  5
               Running: 2
               Done:    12

            🚧 Running Tasks:
               [Lilith] task-abc123: Fix login bug... (5m ago)
               [Shaka] task-def456: Add unit tests... (12m ago)
        """
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

    def pre_diff(self):
        """
        PRE-DIFF: Check who's on what before starting work.
        
        This is the core coordination protocol - always call before claiming.
        Syncs git, checks running tasks, reads MARCO-POLO, shows queue.
        
        Prints:
            - Git sync status
            - Running tasks with owners and ages
            - Recent MARCO-POLO entries
            - Queued tasks sorted by priority
        """
        print("🔍 PRE-DIFF — Who's on what?\n")
        
        # 1. Git sync first
        print("📥 Syncing with git...")
        self._git_sync()
        
        # 2. Check running tasks
        print("\n🚧 Running:")
        running = self.queue.get_running()
        if running:
            for task in running:
                age = self._age_string(task.started_at)
                print(f"   [{task.owner}] {task.id}")
                print(f"      {task.description[:60]}...")
                print(f"      Started: {age}")
        else:
            print("   None")
        
        # 3. Check MARCO-POLO for recent activity
        print("\n📡 Recent MARCO-POLO:")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        polo_path = Path(f"workspaces/Co-op/MARCO-POLO/{today}.md")
        if polo_path.exists():
            content = polo_path.read_text()
            entries = content.split("---")
            for entry in entries[-10:]:
                if entry.strip():
                    print(f"   {entry.strip()[:100]}")
        else:
            print("   No entries today")
        
        # 4. Check queue
        print("\n📋 Queue:")
        queued = self.queue.get_queued()
        if queued:
            for task in queued[:5]:
                print(f"   [{task.priority.value:8}] {task.description[:50]}...")
        else:
            print("   Empty")
        if len(queued) > 5:
            print(f"   ... and {len(queued) - 5} more")
    
    def broadcast(self, message: str, agent: str = None):
        """
        Broadcast a message to MARCO-POLO for other agents to see.
        
        Use this to announce: started, need help, blocked, done, findings.
        Pushes immediately so other agents see it on next git sync.
        
        Args:
            message: The message to broadcast to other agents.
            agent: The agent name sending the message. Defaults to USER env var.
        
        Prints:
            Confirmation of broadcast with truncated message.
        
        Side Effects:
            Appends entry to today's MARCO-POLO file.
            Commits and pushes to git immediately.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = Path(f"workspaces/Co-op/MARCO-POLO/{today}.md")
        agent = agent or os.environ.get("USER", "Unknown")
        
        entry = f"""
---

## [{datetime.now(timezone.utc).strftime("%H:%M UTC")}] 📢 {agent}

{message}

"""
        if path.exists():
            with open(path, "a") as f:
                f.write(entry)
        else:
            with open(path, "w") as f:
                f.write(f"# MARCO-POLO — {today}\n\n")
                f.write("_Auto-generated daily log._\n\n")
                f.write(entry)
        
        self._git_push(f"[Co-op] Broadcast from {agent}")
        print(f"📡 Broadcasted: {message[:60]}...")
    
    def _git_sync(self):
        """Sync with git remote (pull latest changes)."""
        try:
            subprocess.run(["git", "pull", "origin", "main"],
                         capture_output=True, check=False, timeout=30)
        except:
            pass
    
    def _git_push(self, message: str):
        """Commit and push changes to git."""
        try:
            subprocess.run(["git", "add", "-A"], capture_output=True, check=False)
            subprocess.run(["git", "commit", "-m", message],
                         capture_output=True, check=False)
            subprocess.run(["git", "push", "origin", "main"],
                         capture_output=True, check=False, timeout=30)
        except:
            pass

    def dashboard(self) -> str:
        """
        Generate a full dashboard output in Markdown format.

        Creates a comprehensive Markdown-formatted dashboard showing
        current queue statistics and all running tasks. Useful for
        reporting, sharing status, or generating static status pages.

        Returns:
            A Markdown-formatted string containing:
            - Dashboard title with current date
            - Queue statistics table (Queued, Running, Done)
            - List of running tasks with owner, ID, description, and start time

        Example:
            >>> orch = CoOpOrchestrator()
            >>> print(orch.dashboard())
            # CO-OP DASHBOARD — 2026-06-27

            ## Queue
            | Status | Count |
            |--------|-------|
            | Queued | 5 |
            | Running | 2 |
            | Done | 12 |

            ## Running

            - **[Lilith]** task-abc123: Fix login bug
              - Started: 5m ago
            - **[Shaka]** task-def456: Add unit tests
              - Started: 12m ago
        """
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
        """
        Post task completion to today's MARCO-POLO log.

        Creates or appends to a daily MARCO-POLO markdown file that serves
        as a log of all completed and failed tasks. Each entry includes
        the task ID, status, and result message.

        Args:
            task_id: The unique identifier of the completed or failed task.
            status: The task status, either "DONE" or "FAILED".
            message: The result or error message from task execution.

        Side Effects:
            Creates file at workspaces/Co-op/MARCO-POLO/{date}.md if it
            doesn't exist, with appropriate header.
            Appends new entry to existing daily log file.

        Note:
            This is a private method typically called internally by
            release() and fail() methods.
        """
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
        """
        Convert an ISO timestamp to a human-readable age string.

        Takes an ISO 8601 formatted timestamp and returns a human-friendly
        string describing how long ago that time was.

        Args:
            iso_time: An ISO 8601 formatted timestamp string, optionally
                ending with "Z" to indicate UTC timezone.

        Returns:
            A string describing the time elapsed:
            - "Xs ago" for seconds (e.g., "30s ago")
            - "Xm ago" for minutes (e.g., "5m ago")
            - "Xh ago" for hours (e.g., "2h ago")
            - "unknown" if iso_time is empty or None

        Examples:
            >>> orch = CoOpOrchestrator()
            >>> orch._age_string("2026-06-27T18:45:00Z")  # 3 minutes ago
            '3m ago'
            >>> orch._age_string("2026-06-27T17:00:00+00:00")  # 1 hour ago
            '1h ago'
            >>> orch._age_string("")
            'unknown'
        """
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

        Starts a long-running worker loop that continuously claims tasks
        from the queue and dispatches them to OpenHands sandboxes. The
        worker runs until either max_tasks is reached or the process is
        interrupted.

        Args:
            owner: The worker/satellite name that will be associated with
                all claimed tasks (e.g., "Worker-4", "Lilith").
            max_tasks: Optional maximum number of tasks to process before
                the worker exits. If None, runs indefinitely.

        Prints:
            - Worker startup message with owner and task limit
            - Rate limit wait messages
            - Queue empty wait messages (10 second polling)
            - Task dispatch confirmation with sandbox ID
            - Progress updates with completed task count

        Side Effects:
            - Claims tasks from the shared queue
            - Launches OpenHands sandboxes for task execution
            - Releases tasks after sandbox dispatch
            - Respects rate limits for concurrent sandboxes

        Example:
            >>> orch = CoOpOrchestrator()
            >>> orch.run_worker("Worker-4", max_tasks=10)
            🤖 Worker 'Worker-4' starting...
               Max tasks: 10

            🎯 Claimed: task-abc123
               Refactor authentication...
               Owner: Worker-4
               Sandbox: conv-xyz789
               🚀 Task dispatched to sandbox conv-xyz789
               ✅ Completed 1 tasks
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
        Spawn multiple worker processes in parallel.

        Creates multiple worker processes (subprocesses) that each run
        independently to claim and execute tasks. Each worker is assigned
        a unique name (Worker-1, Worker-2, etc.) and can process up to
        max_tasks_per tasks before exiting.

        Args:
            count: The number of worker processes to spawn.
            max_tasks_per: Optional maximum tasks each worker should
                process before exiting. Defaults to None (unlimited).
            owner: Optional satellite owner name. If specified, uses
                that owner's worker number range (e.g., "Lilith" uses
                Worker-1 through Worker-3). If None, uses Worker-1
                through Worker-N.

        Returns:
            A list of tuples containing (worker_name, pid) for each
            spawned worker, useful for process management and monitoring.

        Prints:
            Summary of spawned workers with their names and PIDs.

        Side Effects:
            Creates multiple background subprocesses running the same
            script in worker mode.

        Example:
            >>> orch = CoOpOrchestrator()
            >>> pids = orch.spawn_workers(3, max_tasks_per=5, owner="Lilith")
            🚀 Spawning 3 workers for Lilith...
               Starting Worker-1...
               Starting Worker-2...
               Starting Worker-3...

            ✅ Spawned 3 workers:
               Worker-1: PID 12345
               Worker-2: PID 12346
               Worker-3: PID 12347
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

        Allows inter-satellite communication by appending a command to
        a target satellite's command file. Satellites typically read
        their command file on startup to receive instructions from
        other satellites or the dispatcher.

        Args:
            target: The name of the target satellite (e.g., "Lilith",
                "Shaka", "Stella"). The command file path is derived
                from this name.
            command: The command text to send. Can be any string that
                the target satellite will understand.

        Prints:
            Confirmation message showing target and truncated command.

        Side Effects:
            Creates or appends to the target's command file at
            workspaces/Co-op/tasks/commands/{TARGET}.md

        Example:
            >>> orch = CoOpOrchestrator()
            >>> orch.send_command("Shaka", "Review PR #42 and merge if approved")
            📨 Command sent to Shaka: Review PR #42 and merge if approve...
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
        """
        Read pending commands for a satellite.

        Parses the command file for the specified satellite owner and
        returns a list of all pending commands. Commands are extracted
        from the markdown sections between headers.

        Args:
            owner: The satellite owner name whose command file should
                be read (e.g., "Lilith", "Shaka").

        Returns:
            A list of command strings found in the command file.
            Returns an empty list if the command file doesn't exist
            or contains no valid commands.

        Example:
            >>> orch = CoOpOrchestrator()
            >>> commands = orch.read_commands("Lilith")
            >>> for cmd in commands:
            ...     print(cmd)
            Review PR #42 and merge if approved
            Add unit tests for auth module
        """
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
        """
        Clear the command file for a satellite.

        Deletes the command file after commands have been read and
        processed. Should be called after successfully reading and
        executing all pending commands.

        Args:
            owner: The satellite owner name whose command file should
                be deleted.

        Prints:
            No output. Silently ignores if the file doesn't exist.

        Side Effects:
            Deletes the file at workspaces/Co-op/tasks/commands/{OWNER}.md

        Example:
            >>> orch = CoOpOrchestrator()
            >>> commands = orch.read_commands("Lilith")
            >>> for cmd in commands:
            ...     execute_command(cmd)
            >>> orch.clear_commands("Lilith")  # Clean up after processing
        """
        path = get_command_path(owner)
        if Path(path).exists():
            Path(path).unlink()

    def bulk_submit(self, tasks: list[dict], max_parallel: int = 3):
        """
        Submit multiple tasks, launching in parallel up to max_parallel.

        Efficiently submits a batch of tasks to the queue, claiming and
        launching them to OpenHands sandboxes. Respects rate limits and
        maintains no more than max_parallel concurrent sandboxes.

        Args:
            tasks: A list of task specifications. Each item can be either:
                - A string: Used as the task description with normal priority
                - A dict: Must contain "description" key, optionally "priority"
            max_parallel: Maximum number of sandboxes to run concurrently.
                Defaults to 3. The method will wait if this limit is reached.

        Returns:
            A list of conversation IDs for each successfully launched
            sandbox. The list length may be less than the input task count
            if some tasks failed to launch.

        Prints:
            Progress messages showing total tasks and launched count.

        Side Effects:
            - Submits tasks to the queue
            - Claims tasks immediately for execution
            - Launches OpenHands sandboxes for each claimed task
            - Respects rate limits for concurrent sandboxes and API calls

        Example:
            >>> orch = CoOpOrchestrator()
            >>> tasks = [
            ...     {"description": "Fix bug in login", "priority": "high"},
            ...     "Add unit tests for auth",
            ...     {"description": "Update docs", "priority": "low"}
            ... ]
            >>> conv_ids = orch.bulk_submit(tasks, max_parallel=2)
            📦 Bulk submit: 3 tasks (max 2 parallel)
            🚀 Launched 3 tasks
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
    """
    Main entry point for the Co-op Orchestrator CLI.

    Parses command-line arguments and executes the appropriate orchestrator
    action. Supports task submission, claiming, status reporting, worker
    spawning, and inter-satellite command delivery.

    Command-line Arguments:
        --submit/-s: Submit a new task with description
        --claim: Claim the next available task
        --release: Release a task with result message
        --fail: Mark a task as failed with error message
        --status: Show queue status summary
        --dashboard: Generate full Markdown dashboard
        --worker: Run as a worker with specified owner name
        --spawn: Spawn N worker processes
        --send-command: Send a command to a satellite
        --read-commands: Read pending commands for owner
        --owner/-o: Owner name for claiming (default: Lilith)
        --priority/-p: Task priority (default: normal)
        --tags/-t: Tags for task
        --result/-r: Result message for release
        --max-parallel: Max parallel tasks for bulk submit
        --file/-f: File with tasks (one per line)
        --max-tasks: Max tasks for worker mode

    Prints:
        Various outputs depending on the command executed.

    Example:
        python coop_orchestrator.py --submit "Fix the bug" --priority high
        python coop_orchestrator.py --status
        python coop_orchestrator.py --spawn 3 --owner Lilith
    """
    parser = argparse.ArgumentParser(description="Co-op Task Orchestrator")
    
    # Commands
    parser.add_argument("--submit", "-s", help="Submit a new task")
    parser.add_argument("--claim", action="store_true", help="Claim next task")
    parser.add_argument("--release", help="Release task with result")
    parser.add_argument("--fail", nargs=2, metavar=("TASK_ID", "ERROR"), help="Mark task as failed")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--dashboard", action="store_true", help="Show full dashboard")
    parser.add_argument("--pre-diff", action="store_true", help="Check who's on what before starting")
    parser.add_argument("--broadcast", "-b", help="Broadcast message to MARCO-POLO")
    parser.add_argument("--agent", help="Agent name for broadcasts (default: owner)")
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
    
    elif args.pre_diff:
        orch.pre_diff()
    
    elif args.broadcast:
        orch.broadcast(args.broadcast, args.agent or args.owner)
    
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