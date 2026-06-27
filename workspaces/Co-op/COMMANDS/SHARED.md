# SHARED Commands

**Both sessions** read this file. Use for tasks that need to split then merge.

## Co-op Task Execution

Any session (Lilith, Shaka, etc.) can delegate tasks to OpenHands Cloud using `lilith_task_sender.py`.

**Shared API Key:** All sessions share the same OpenHands Cloud API key stored in `workspaces/Co-op/.env`

**Dashboard:** All sessions can view and manage all conversations via:
```bash
python workspaces/Co-op/lilith_task_sender.py --list
```

**Cleanup:** When a task completes and commits:
1. Its work appears in git history + MARCO-POLO
2. Any session can delete it: `--delete <id>` or `--cleanup-done`

## Pending

| # | Command | Lilith Part | Shaka Part | Status |
|---|---------|-------------|------------|--------|
| — | — | — | — | — |

## Done

| # | Command | Merged Result | Completed |
|---|---------|---------------|-----------|
| — | — | — | — |