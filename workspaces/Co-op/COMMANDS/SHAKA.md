# SHAKA Commands

**Mobile session** reads this file at the start of each turn. Post commands here from either device.

## Task Execution

Shaka can delegate tasks to OpenHands Cloud via `lilith_task_sender.py`. Each task runs in a fresh sandbox, posts results to MARCO-POLO, commits to git, then gets cleaned up.

### Quick Start

```bash
# Send a task
python workspaces/Co-op/lilith_task_sender.py --task "Fix the bug in auth.py"

# Send a task from file
python workspaces/Co-op/lilith_task_sender.py --task-file task.md

# List all conversations
python workspaces/Co-op/lilith_task_sender.py --list

# Delete a completed task
python workspaces/Co-op/lilith_task_sender.py --delete <conversation_id>

# Cleanup all done tasks
python workspaces/Co-op/lilith_task_sender.py --cleanup-done
```

### Task Lifecycle

1. **Send** → Sandbox spins up with your task
2. **Execute** → Sandbox clones repo, does the work
3. **Post** → Sandbox posts results to MARCO-POLO.md
4. **Commit** → Sandbox commits as "Shaka <shaka@jarvis.local>" and pushes
5. **Cleanup** → Delete the sandbox when done

## Pending

| # | Command | Posted By | Time |
|---|---------|-----------|------|
| — | — | — | — |

## Done

| # | Command | Result | Completed |
|---|---------|--------|-----------|
| 2 | Run `date` and post the result to MARCO-POLO. This tests remote control! | Done | 02:10 UTC |