#!/usr/bin/env python3
"""
Lilith Task Sender — Co-op Task Execution via OpenHands Cloud

Sends tasks to OpenHands Cloud sandboxes with auto-cleanup:
1. Starts a new sandbox via Cloud API
2. Sandbox executes task
3. Sandbox posts results to MARCO-POLO
4. Sandbox deletes itself

Usage:
    python lilith_task_sender.py --task "Fix the bug in auth.py"
    python lilith_task_sender.py --task-file task.md
    python lilith_task_sender.py --list-tasks
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime, timezone
from pathlib import Path

# Configuration
OPENHANDS_API_URL = "https://app.all-hands.dev/api/v1"
JARVIS_PRIVATE_REPO = "hurrisonferd/Jarvis-Private"

def get_marco_polo_path():
    """Get today's MARCO-POLO daily file path."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"workspaces/Co-op/MARCO-POLO/{today}.md"

# Legacy path for backwards compatibility
MARCO_POLO_PATH = get_marco_polo_path()

class LilithTaskSender:
    def __init__(self, api_key: str = None):
        # Load from env file if not in environment
        if not api_key:
            api_key = os.environ.get("OPENHANDS_CLOUD_API_KEY")
            if not api_key:
                env_file = Path.home() / ".jarvis" / ".env.local"
                if env_file.exists():
                    for line in env_file.read_text().strip().split('\n'):
                        if '=' in line and line.startswith('OPENHANDS_CLOUD_API_KEY'):
                            api_key = line.split('=', 1)[1].strip()
        
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("OPENHANDS_CLOUD_API_KEY not set. Get it from https://app.all-hands.dev/settings/api-keys")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def list_conversations(self, limit: int = 10):
        """List recent OpenHands conversations/sandboxes."""
        url = f"{OPENHANDS_API_URL}/app-conversations/search"
        params = {"limit": limit}
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("items", [])
    
    def get_conversation(self, conversation_id: str):
        """Get details of a specific conversation."""
        url = f"{OPENHANDS_API_URL}/app-conversations"
        params = {"ids": conversation_id}
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("items", [])
        return items[0] if items else None
    
    def delete_sandbox(self, sandbox_id: str):
        """Delete a sandbox (if we have direct access)."""
        url = f"{OPENHANDS_API_URL}/sandboxes/{sandbox_id}"
        resp = requests.delete(url, headers=self.headers)
        return resp.status_code == 200
    
    def pause_sandbox(self, sandbox_id: str):
        """Pause a running sandbox."""
        url = f"{OPENHANDS_API_URL}/sandboxes/{sandbox_id}/pause"
        resp = requests.post(url, headers=self.headers)
        return resp.status_code == 200
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation by ID."""
        url = f"{OPENHANDS_API_URL}/app-conversations/{conversation_id}"
        resp = requests.delete(url, headers=self.headers)
        return resp.status_code == 200 and resp.json().get("success", False)
    
    def send_task(self, task: str, repo: str = None, branch: str = "main") -> dict:
        """
        Send a task to OpenHands Cloud.
        
        The task prompt includes instructions to:
        1. Execute the task
        2. Post results to MARCO-POLO
        3. Delete itself via Agent Server API
        """
        # Build the self-deleting task prompt
        task_prompt = self._build_task_prompt(task)
        
        data = {
            "initial_message": {
                "content": [{"type": "text", "text": task_prompt}]
            },
            "selected_repository": repo or JARVIS_PRIVATE_REPO,
            "selected_branch": branch
        }
        
        url = f"{OPENHANDS_API_URL}/app-conversations"
        resp = requests.post(url, headers=self.headers, json=data)
        resp.raise_for_status()
        
        result = resp.json()
        
        # Extract conversation info
        conversation_id = result.get("app_conversation_id") or result.get("id")
        start_task_id = result.get("id")
        
        return {
            "conversation_id": conversation_id,
            "start_task_id": start_task_id,
            "status": result.get("status"),
            "cloud_url": f"https://app.all-hands.dev/conversations/{conversation_id}" if conversation_id else None,
            "raw": result
        }
    
    def _build_task_prompt(self, task: str) -> str:
        """Build a task prompt that includes step-by-step progress and self-deletion."""
        # Build bash template separately to avoid f-string issues
        bash_delete = """CONV_ID=$(ls /workspace/conversations/ | head -1)
SESSION_KEY="$SESSION_API_KEY"
curl -X DELETE "http://127.0.0.1:60000/api/conversations/${CONV_ID}" \\
  -H "X-Session-API-Key: ${SESSION_KEY}"
"""
        return f"""{task}

## MANDATORY: Step-by-Step Progress Logging

For multi-step tasks, you MUST log each step with timestamp as you complete it:

```bash
echo "[$(date +%H:%M:%S) UTC] Step 1: <description>" >> /tmp/swarm_progress.md
echo "[$(date +%H:%M:%S) UTC] Step 2: <description>" >> /tmp/swarm_progress.md
# ... continue for each step
echo "[$(date +%H:%M:%S) UTC] All steps complete!" >> /tmp/swarm_progress.md
cat /tmp/swarm_progress.md
```

## IMPORTANT: Setup Git First
Before making any commits, configure git:
```bash
git config user.email "worker@jarvis.local"
git config user.name "Worker"
```

## After completing your task, you MUST do the following in order:

### Step 1: Find or create the current swarm log

Run this script to get the right log file:
```bash
cd /workspace/project/Jarvis-Private/workspaces/Co-op/MARCO-POLO

# Get today's date parts
MONTH=$(date +%m | sed 's/^0//')  # 1-12
DAY=$(date +%d | sed 's/^0//')    # 1-31
YEAR=$(date +%y)                   # 26

# Find existing logs for today
EXISTING=$(ls MP-$MONTH.$DAY.$YEAR-*.md 2>/dev/null | sort)

# Count existing logs today
COUNT=$(echo "$EXISTING" | grep -c . || echo 0)
NEXT_NUM=$(printf "%04d" $((COUNT + 1)))

# Check if we need a new log (none exist OR current > 200 lines)
if [ -z "$EXISTING" ]; then
    LOG_FILE="MP-$MONTH.$DAY.$YEAR-$NEXT_NUM.md"
    echo "# MARCO-POLO — MP-$MONTH.$DAY.$YEAR-$NEXT_NUM" > "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "---" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
else
    LAST_LOG=$(echo "$EXISTING" | tail -1)
    LINE_COUNT=$(wc -l < "$LAST_LOG")
    if [ "$LINE_COUNT" -gt 200 ]; then
        LOG_FILE="MP-$MONTH.$DAY.$YEAR-$NEXT_NUM.md"
        echo "# MARCO-POLO — MP-$MONTH.$DAY.$YEAR-$NEXT_NUM" > "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        echo "---" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
    else
        LOG_FILE="$LAST_LOG"
    fi
fi
echo "USING_LOG=$LOG_FILE"
```

### Step 2: Append result to swarm log

Append to the log file determined above:
```
## [$$(date +%H:%M:%S) UTC] Worker — Task Complete

**Task:** <brief description>
**Status:** ✅ DONE
**Steps:**
- Step 1: <what you did>
- Step 2: <what you did>
**Files changed:** <list>

---
```

### Step 3: Commit and push your changes
```bash
cd /workspace/project/Jarvis-Private
git add -A
git commit -m "[Co-op] Worker: task complete"
git push origin main
```

### Step 4: Delete this conversation
After pushing, delete this conversation to clean up the sandbox:
```bash
{bash_delete}
```

If successful, you will see: {{"success": true}}

DO NOT stop before completing all steps."""


def read_task_file(filepath: str) -> str:
    """Read task from a file."""
    with open(filepath, 'r') as f:
        return f.read().strip()


def main():
    parser = argparse.ArgumentParser(description="Lilith Task Sender — Co-op task execution")
    parser.add_argument("--task", "-t", help="Task description")
    parser.add_argument("--task-file", "-f", help="File containing task description")
    parser.add_argument("--repo", "-r", help="GitHub repository (default: hurrisonferd/Jarvis-Private)")
    parser.add_argument("--branch", "-b", default="main", help="Branch (default: main)")
    parser.add_argument("--list", "-l", action="store_true", help="List recent conversations")
    parser.add_argument("--status", "-s", help="Check status of a conversation by ID")
    parser.add_argument("--pause", "-p", help="Pause a sandbox by ID")
    parser.add_argument("--delete", "-d", help="Delete a conversation by ID")
    parser.add_argument("--cleanup-done", action="store_true", help="Delete all completed (PAUSED/COMPLETED) task sandboxes")
    parser.add_argument("--cleanup-old", metavar="HOURS", help="Delete all task sandboxes older than N hours (keeps your session)")
    parser.add_argument("--count", action="store_true", help="Count total conversations")
    
    args = parser.parse_args()
    
    try:
        sender = LilithTaskSender()
        
        if args.list:
            print("📋 Recent OpenHands Conversations:\n")
            convs = sender.list_conversations(limit=20)
            for c in convs:
                status = c.get("status") or c.get("sandbox_status") or "?"
                title = c.get("title") or c.get("id", "?")[:20]
                created = c.get("created_at", "")[:19]
                print(f"  [{status:10}] {title:25} | {created}")
            return
        
        if args.count:
            url = f"{OPENHANDS_API_URL}/app-conversations/count"
            resp = requests.get(url, headers=sender.headers)
            count = resp.json().get("count", "?")
            print(f"Total conversations: {count}")
            return
        
        if args.status:
            conv = sender.get_conversation(args.status)
            if conv:
                print(json.dumps(conv, indent=2))
            else:
                print(f"Conversation {args.status} not found")
            return
        
        if args.pause:
            if sender.pause_sandbox(args.pause):
                print(f"✅ Sandbox {args.pause} paused")
            else:
                print(f"❌ Failed to pause sandbox {args.pause}")
            return
        
        if args.delete:
            if sender.delete_conversation(args.delete):
                print(f"✅ Deleted conversation {args.delete}")
            else:
                print(f"❌ Failed to delete {args.delete}")
            return
        
        if args.cleanup_done:
            convs = sender.list_conversations(limit=50)
            deleted = 0
            for c in convs:
                status = c.get('sandbox_status', '')
                cid = c.get('id', '')
                title = c.get('title', '')
                # Skip Lilith's main session
                if 'Lilith' in title or 'lilith' in title.lower():
                    continue
                if status in ['PAUSED', 'COMPLETED']:
                    if sender.delete_conversation(cid):
                        print(f"✅ Deleted: {title[:40]}")
                        deleted += 1
            print(f"\n🧹 Cleaned up {deleted} old conversations")
            return
        
        if args.cleanup_old:
            from datetime import datetime, timezone
            import math
            hours = int(args.cleanup_old)
            cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
            convs = sender.list_conversations(limit=100)
            deleted = 0
            for c in convs:
                cid = c.get('id', '')
                title = c.get('title', '')
                created = c.get('created_at', '')
                # Skip Lilith's main session
                if 'Lilith' in title or 'lilith' in title.lower():
                    continue
                # Check age
                try:
                    created_ts = datetime.fromisoformat(created.replace('Z', '+00:00')).timestamp()
                    if created_ts < cutoff:
                        if sender.delete_conversation(cid):
                            print(f"✅ Deleted (old): {title[:40]}")
                            deleted += 1
                except:
                    pass
            print(f"\n🧹 Cleaned up {deleted} conversations older than {hours}h")
            return
        
        if args.task_file:
            task = read_task_file(args.task_file)
        elif args.task:
            task = args.task
        else:
            parser.print_help()
            return
        
        print(f"🚀 Sending task to OpenHands Cloud...")
        result = sender.send_task(task, args.repo, args.branch)
        
        print(f"\n✅ Task sent!")
        print(f"   Conversation ID: {result['conversation_id']}")
        print(f"   Status: {result['status']}")
        if result['cloud_url']:
            print(f"   URL: {result['cloud_url']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()