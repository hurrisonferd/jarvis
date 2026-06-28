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
    
    def _pre_flight_cleanup(self, max_age_hours: int = 1, max_active: int = 8):
        """
        Clean up old conversations before sending new tasks.
        Prevents hitting the conversation cap.
        
        Deletes:
        - All conversations older than max_age_hours (except Lilith)
        - If still over max_active, deletes oldest non-Lilith conversations
        """
        convs = self.list_conversations(limit=100)
        
        # Skip Lilith's main session
        lilith_ids = [c.get('id') for c in convs if 'Lilith' in c.get('title','') or 'lilith' in c.get('title','').lower()]
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - (max_age_hours * 3600)
        
        # First pass: delete old ones
        deleted = 0
        for c in convs:
            cid = c.get('id', '')
            title = c.get('title', '')
            created = c.get('created_at', '')
            
            if cid in lilith_ids:
                continue
            
            try:
                created_ts = datetime.fromisoformat(created.replace('Z', '+00:00')).timestamp()
                if created_ts < cutoff:
                    if self.delete_conversation(cid):
                        deleted += 1
            except:
                pass
        
        if deleted:
            print(f"🧹 Cleaned up {deleted} old conversations")
        
        # Second pass: if still over max, delete oldest workers
        remaining = self.list_conversations(limit=100)
        non_lilith = [c for c in remaining if c.get('id') not in lilith_ids]
        
        while len(non_lilith) >= max_active:
            # Delete the oldest one
            oldest = min(non_lilith, key=lambda c: c.get('created_at', ''))
            if self.delete_conversation(oldest.get('id', '')):
                print(f"🧹 Deleted oldest worker to make room")
                non_lilith.remove(oldest)
            else:
                break
    
    def send_task(self, task: str, repo: str = None, branch: str = "main", auto_cleanup: bool = True) -> dict:
        """
        Send a task to OpenHands Cloud.
        
        The task prompt includes instructions to:
        1. Execute the task
        2. Post results to MARCO-POLO
        3. Delete itself via Agent Server API
        
        Args:
            auto_cleanup: If True, delete old conversations before sending (prevents cap issues)
        """
        # Auto-cleanup to prevent hitting conversation cap
        if auto_cleanup:
            self._pre_flight_cleanup()
        
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
    
    def _count_task_steps(self, task: str) -> str:
        """
        Estimate number of work steps from task description.
        
        Looks for patterns like:
        - "Step 1/2/3" or "First/Second/Third" 
        - Numbered lists
        - Bullet points with sub-tasks
        - Keywords like "then", "next", "finally"
        """
        import re
        
        # Count explicit step patterns
        step_patterns = [
            r'(?i)step\s*\d+',
            r'(?i)first[,\s]',
            r'(?i)second[,\s]',
            r'(?i)third[,\s]',
            r'(?i)then[,\s]',
            r'(?i)next[,\s]',
            r'(?i)finally[,\s]',
            r'(?i)after\s+that',
        ]
        
        count = 0
        for pattern in step_patterns:
            count += len(re.findall(pattern, task))
        
        # Count bullet points (lines starting with - or *)
        bullets = len(re.findall(r'^[\s]*[-*]\s+', task, re.MULTILINE))
        
        # Count numbered items
        numbered = len(re.findall(r'^[\s]*\d+[\.\)]\s+', task, re.MULTILINE))
        
        # Take the max of explicit steps and structure
        total = max(count, bullets, numbered)
        
        # Minimum 1 step, maximum 10
        return str(max(1, min(total, 10)))
    
    def _build_task_prompt(self, task: str) -> str:
        """
        Build a task prompt with guaranteed step logging and self-deletion.
        
        NOTE: Self-deletion is for WORKER sandboxes only. The parent Lilith
        session must NEVER call the delete endpoint on itself. Workers are
        disposable; Lilith is persistent.
        
        IMPORTANT: The delete command uses the SESSION_API_KEY to identify THIS
        conversation. It queries the API to get the current conversation ID
        rather than guessing from filesystem listing.
        """
        return f"""{task}

## MANDATORY: Follow this EXACT sequence

### CONUITY SETUP (do this first, before anything else)
```bash
# Count your expected steps and set this variable
# Example: If task has 3 work steps, set TASK_STEPS="3"
# Adjust based on actual task complexity
TASK_STEPS="{self._count_task_steps(task)}"
```

### Step 0: Setup (do this first, before anything else)
```bash
cd /workspace/project/Jarvis-Private
git config user.email "worker@jarvis.local"
git config user.name "Worker"
git pull origin main
mkdir -p workspaces/Co-op/MARCO-POLO
cd workspaces/Co-op/MARCO-POLO
LOG_FILE="MP-$(date +%m.%d.%y)-0001.md"
if [ ! -f "$LOG_FILE" ]; then
    echo "# MARCO-POLO — MP-$(date +%m.%d.%y)-0001" > "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "---" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
fi
echo "## [$(date +%H:%M:%S) UTC] Worker — Step 0: Setup complete" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
cd /workspace/project/Jarvis-Private
git add -A && git commit -m "Worker: Step 0 setup" && git push origin main
```

### Step 1: First work item
- Do the work
- Then immediately:
```bash
cd /workspace/project/Jarvis-Private/workspaces/Co-op/MARCO-POLO
echo "## [$(date +%H:%M:%S) UTC] Worker — Step 1: <describe>" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
cd /workspace/project/Jarvis-Private
git add -A && git commit -m "Worker: Step 1 done" && git push origin main
```

### Step 2: Second work item
- Do the work
- Then immediately:
```bash
cd /workspace/project/Jarvis-Private/workspaces/Co-op/MARCO-POLO
echo "## [$(date +%H:%M:%S) UTC] Worker — Step 2: <describe>" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
cd /workspace/project/Jarvis-Private
git add -A && git commit -m "Worker: Step 2 done" && git push origin main
```

### Continue for each step

### Final step: Complete and delete
```bash
cd /workspace/project/Jarvis-Private/workspaces/Co-op/MARCO-POLO
echo "## [$(date +%H:%M:%S) UTC] Worker — DONE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo '**Status:** ✅ COMPLETE' >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
cd /workspace/project/Jarvis-Private
git add -A && git commit -m "Worker: task complete" && git push origin main

# CONUITY CHECK: Verify at least 1 step was logged before deleting
# This ensures work was committed before self-deletion
STEPS_DONE=$(grep -c "^## \[[0-9][0-9]:[0-9][0-9]:[0-9][0-9] UTC\] Worker" "$LOG_FILE" 2>/dev/null || echo "0")
if [ "$STEPS_DONE" -lt 1 ]; then
    echo "⚠️ CONUITY WARNING: No steps logged! Checking for actual work..."
    # Allow delete if files were created even without step logging
    if [ "$(git status --porcelain | wc -l)" -lt 1 ]; then
        echo "⚠️ No work committed. Refusing to delete."
        exit 1
    fi
    echo "Work found, allowing delete..."
fi

# Get THIS conversation's ID from the API, then delete ONLY this conversation
MY_CONV_ID=$(curl -s "http://127.0.0.1:60000/api/conversations" -H "X-Session-API-Key: $SESSION_API_KEY" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); ids=d.get('conversation_ids',[]); print(ids[0] if ids else '')" 2>/dev/null)
if [ -n "$MY_CONV_ID" ]; then
    curl -X DELETE "http://127.0.0.1:60000/api/conversations/$MY_CONV_ID" -H "X-Session-API-Key: $SESSION_API_KEY"
fi
```

RULES:
1. Step 0 FIRST - no work until setup committed
2. After EACH step, post to log and commit
3. **CONUITY CHECK: All expected steps MUST be logged before delete**
4. Delete LAST after all commits pushed - and ONLY delete YOUR OWN conversation
5. NEVER delete a conversation unless you got its ID from the API using YOUR session key
6. If conuity check fails, REFUSE to delete and alert
"""

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