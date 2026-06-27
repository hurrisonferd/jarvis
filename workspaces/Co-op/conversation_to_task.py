#!/usr/bin/env python3
"""
MARCO-POLO to Task Converter
Scans conversations and creates tasks from task-like messages.
"""
import re
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent
MARCOPOLO = BASE / "MARCO-POLO"
QUEUE_FILE = BASE / "tasks" / "queue.md"

# Patterns that indicate a task request
TASK_PATTERNS = [
    r"(?:build|create|make)\s+(?:a\s+)?(.+)",
    r"(?:fix|update|clean)\s+(?:up\s+)?(.+)",
    r"(?:check|look\s+at|audit)\s+(?:the\s+)?(.+)",
    r"should\s+(?:we\s+)?(.+)",
    r"need\s+(?:to\s+)?(.+)",
    r"please\s+(.+)",
    r"task[:\s]+(.+)",
]

class TaskExtractor:
    def __init__(self):
        self.seen = set()
    
    def scan_conversations(self):
        """Scan MARCO-POLO for task-like messages."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = MARCOPOLO / f"{today}.md"
        
        if not log_file.exists():
            return []
        
        with open(log_file) as f:
            content = f.read()
        
        new_tasks = []
        messages = re.findall(r'\*\*Message:\*\* (.+)', content)
        
        for msg in messages:
            msg_short = msg[:80]
            if msg_short in self.seen:
                continue
            
            # Check for task patterns
            for pattern in TASK_PATTERNS:
                match = re.search(pattern, msg, re.IGNORECASE)
                if match:
                    task_text = match.group(1).strip()
                    if len(task_text) > 5:  # Skip short fragments
                        self.seen.add(msg_short)
                        new_tasks.append((task_text, msg_short))
                    break
        
        return new_tasks
    
    def add_to_queue(self, description, source):
        """Add a task to the queue."""
        import uuid
        task_id = f"chat-{uuid.uuid4().hex[:6]}"
        
        if not QUEUE_FILE.exists():
            QUEUE_FILE.write_text("# Swarm Task Queue\n\n<!-- TASKS -->\n\n<!-- END TASKS -->\n")
        
        content = QUEUE_FILE.read_text()
        
        # Don't duplicate (check first 50 chars of description)
        if description[:50] in content:
            return None
        
        # Clean description - remove emoji and truncate
        clean_desc = re.sub(r'[💬📋✅⚡🐝🔨👁️🎉]+', '', description).strip()[:70]
        new_line = f"- [ ] {task_id} | {clean_desc}\n"
        
        if "<!-- TASKS -->" in content:
            content = content.replace("<!-- TASKS -->", f"<!-- TASKS -->\n{new_line}")
        else:
            content += new_line
        
        QUEUE_FILE.write_text(content)
        print(f"📋 Task: {task_id} - {clean_desc[:40]}")
        return task_id

def main():
    print("👁️ MARCO-POLO → Task converter running...")
    extractor = TaskExtractor()
    
    while True:
        tasks = extractor.scan_conversations()
        for desc, src in tasks:
            extractor.add_to_queue(desc, src)
        
        time.sleep(5)  # Poll every 5 seconds

if __name__ == "__main__":
    main()