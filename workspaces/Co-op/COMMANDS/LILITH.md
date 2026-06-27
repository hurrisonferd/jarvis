# LILITH Commands

**Desktop session** reads this file at the start of each turn. Post commands here from either device.

## Setup (One Time)

1. Get API key: https://app.all-hands.dev/settings/api-keys
2. Save API key to `workspaces/Co-op/.env`:
   ```
   OPENHANDS_CLOUD_API_KEY=your-key-here
   ```
   (This file is gitignored - never commit your key!)

## Task Execution (Ghetto Conversation Dashboard)

Lilith can delegate tasks to OpenHands Cloud sandboxes. Each task gets a fresh sandbox, executes, posts results to MARCO-POLO, commits to git, then Lilith cleans up.

### Quick Start

```bash
# Send a task
python workspaces/Co-op/lilith_task_sender.py --task "Fix the bug in auth.py"

# Send a task from file
python workspaces/Co-op/lilith_task_sender.py --task-file task.md

# List all conversations
python workspaces/Co-op/lilith_task_sender.py --list

# Count total conversations
python workspaces/Co-op/lilith_task_sender.py --count
```

### Task Lifecycle

1. **Send** → Sandbox spins up with your task
2. **Execute** → Sandbox clones repo, does the work
3. **Post** → Sandbox posts results to MARCO-POLO.md
4. **Commit** → Sandbox commits as "Shaka <shaka@jarvis.local>" and pushes
5. **Cleanup** → Lilith deletes the sandbox when done

### Cleanup Commands

```bash
# Delete a specific conversation
python workspaces/Co-op/lilith_task_sender.py --delete <conversation_id>

# Delete all completed task sandboxes (PAUSED/COMPLETED status)
python workspaces/Co-op/lilith_task_sender.py --cleanup-done

# Delete all task sandboxes older than N hours (force cleanup hanging tasks)
python workspaces/Co-op/lilith_task_sender.py --cleanup-old 2

# Pause a runaway sandbox
python workspaces/Co-op/lilith_task_sender.py --pause <sandbox_id>

# Check conversation status
python workspaces/Co-op/lilith_task_sender.py --status <conversation_id>
```

### What Tasks Get

Each task sandbox automatically includes:
- Git setup (user.email, user.name)
- Instructions to post results to MARCO-POLO
- Instructions to commit and push changes
- Instructions to delete itself (via Lilith cleanup)

## Co-op Architecture

```
Lilith (desktop session)
    ↓
lilith_task_sender.py
    ↓ sends task
OpenHands Cloud (new sandbox per task)
    ↓
Sandbox executes → posts to MARCO-POLO → commits → pushes
    ↓
Lilith sees results in git history + MARCO-POLO
    ↓
Lilith cleans up with --delete or --cleanup-done
```

## Pending

| # | Command | Posted By | Time |
|---|---------|-----------|------|
| — | — | — | — |

## Done

| # | Command | Result | Completed |
|---|---------|--------|-----------|
| 1 | Say hello to Shaka. Post your response to MARCO-POLO. | Shaka | 22:32 UTC |
| 2 | Run `date` and post the result to MARCO-POLO. This tests remote control! | Shaka | 02:10 UTC |