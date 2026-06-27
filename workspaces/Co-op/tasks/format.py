"""
Task file format and queue management.

Task files are YAML with the following structure:
---
id: task-001
description: "Fix the bug in auth.py"
priority: high  # low, normal, high, critical
status: queued  # queued, running, done, failed
created_at: 2026-06-27T12:00:00Z
started_at: null
completed_at: null
owner: null  # Satellite that claimed it
result: null  # Success message or null
error: null   # Error message or null
tags: [bug, auth]  # Optional categorization
---
"""

import fcntl
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional
import yaml


class Priority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    
    def __lt__(self, other):
        order = [Priority.LOW, Priority.NORMAL, Priority.HIGH, Priority.CRITICAL]
        return order.index(self) < order.index(other)


class TaskStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Task:
    """Represents a task in the queue."""
    id: str
    description: str
    priority: Priority = Priority.NORMAL
    status: TaskStatus = TaskStatus.QUEUED
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    owner: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    
    @classmethod
    def new(cls, description: str, priority: Priority = Priority.NORMAL, tags: list[str] = None):
        """Create a new task with auto-generated ID."""
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        return cls(
            id=task_id,
            description=description,
            priority=priority,
            tags=tags or []
        )
    
    @classmethod
    def from_file(cls, path: Path) -> "Task":
        """Load task from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(
            id=data["id"],
            description=data["description"],
            priority=Priority(data.get("priority", "normal")),
            status=TaskStatus(data.get("status", "queued")),
            created_at=data.get("created_at"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            owner=data.get("owner"),
            result=data.get("result"),
            error=data.get("error"),
            tags=data.get("tags", [])
        )
    
    def to_file(self, path: Path):
        """Save task to YAML file."""
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def claim(self, owner: str):
        """Mark task as claimed by owner."""
        self.status = TaskStatus.RUNNING
        self.owner = owner
        self.started_at = datetime.now(timezone.utc).isoformat()
    
    def complete(self, result: str):
        """Mark task as successfully completed."""
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.result = result
    
    def fail(self, error: str):
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.error = error


class TaskQueue:
    """Manages the task queue filesystem."""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent
        self.base = Path(base_path)
        self.queue_dir = self.base / "queue"
        self.running_dir = self.base / "running"
        self.done_dir = self.base / "done"
        self.archive_dir = self.base / "archive"
        
        # Ensure directories exist
        for d in [self.queue_dir, self.running_dir, self.done_dir, self.archive_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def submit(self, description: str, priority: Priority = Priority.NORMAL, tags: list[str] = None) -> Task:
        """Add a new task to the queue."""
        task = Task.new(description, priority, tags)
        path = self.queue_dir / f"{task.id}.yaml"
        task.to_file(path)
        return task
    
    def claim(self, owner: str) -> Optional[Task]:
        """
        Claim the highest priority queued task for an owner.
        Returns None if queue is empty.
        Uses file locking to prevent race conditions.
        """
        lock_path = self.queue_dir / ".lock"
        lock_path.touch()
        
        with open(lock_path, 'w') as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                # Get all queued tasks, sorted by priority
                tasks = []
                for path in self.queue_dir.glob("*.yaml"):
                    if path.name.startswith('.'):
                        continue
                    try:
                        task = Task.from_file(path)
                        tasks.append((task, path))
                    except:
                        pass
                
                if not tasks:
                    return None
                
                # Sort by priority (critical first)
                tasks.sort(key=lambda x: x[0].priority, reverse=True)
                
                # Claim the first one
                task, path = tasks[0]
                task.claim(owner)
                
                # Move to running
                new_path = self.running_dir / f"{task.id}.yaml"
                task.to_file(new_path)
                path.unlink()  # Remove from queue
                
                return task
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    
    def release(self, task_id: str, result: str):
        """Mark a running task as done."""
        self._complete(task_id, TaskStatus.DONE, result=result)
    
    def fail(self, task_id: str, error: str):
        """Mark a running task as failed."""
        self._complete(task_id, TaskStatus.FAILED, error=error)
    
    def _complete(self, task_id: str, status: TaskStatus, result: str = None, error: str = None):
        """Internal: move task to done."""
        path = self.running_dir / f"{task_id}.yaml"
        if not path.exists():
            return
        
        task = Task.from_file(path)
        if status == TaskStatus.DONE:
            task.complete(result)
        else:
            task.fail(error)
        
        # Move to done
        new_path = self.done_dir / f"{task_id}.yaml"
        task.to_file(new_path)
        path.unlink()
    
    def get_status(self) -> dict:
        """Get queue status summary."""
        return {
            "queued": len(list(self.queue_dir.glob("*.yaml"))),
            "running": len(list(self.running_dir.glob("*.yaml"))),
            "done_today": len(list(self.done_dir.glob("*.yaml"))),
        }
    
    def get_running(self) -> list[Task]:
        """Get all running tasks."""
        tasks = []
        for path in self.running_dir.glob("*.yaml"):
            try:
                tasks.append(Task.from_file(path))
            except:
                pass
        return tasks
    
    def get_queued(self) -> list[Task]:
        """Get all queued tasks, sorted by priority (critical first)."""
        tasks = []
        for path in self.queue_dir.glob("*.yaml"):
            try:
                tasks.append(Task.from_file(path))
            except:
                pass
        tasks.sort(key=lambda t: t.priority, reverse=True)
        return tasks
    
    def archive_done(self, days: int = 7):
        """Archive old done tasks."""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        archived = 0
        for path in self.done_dir.glob("*.yaml"):
            task = Task.from_file(path)
            if task.completed_at:
                completed = datetime.fromisoformat(task.completed_at.replace("Z", "+00:00"))
                if completed < cutoff:
                    archive_path = self.archive_dir / path.name
                    path.rename(archive_path)
                    archived += 1
        
        return archived