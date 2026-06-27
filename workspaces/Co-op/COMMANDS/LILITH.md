# LILITH Commands

**Desktop session** reads this file at the start of each turn. Post commands here from either device.

## Setup (One Time)

1. Get API key: https://app.all-hands.dev/settings/api-keys
2. Set environment variable:
   ```bash
   export OPENHANDS_CLOUD_API_KEY="your-key-here"
   ```
3. Or save to `~/.env`:
   ```
   OPENHANDS_CLOUD_API_KEY=your-key-here
   ```

## Task Execution

Lilith can send tasks to OpenHands Cloud sandboxes via `lilith_task_sender.py`:

```bash
# Send a task
python workspaces/Co-op/lilith_task_sender.py --task "Fix the typo in README.md"

# Send a task from file
python workspaces/Co-op/lilith_task_sender.py --task-file task.md

# List recent conversations
python workspaces/Co-op/lilith_task_sender.py --list

# Count total conversations
python workspaces/Co-op/lilith_task_sender.py --count

# Check conversation status
python workspaces/Co-op/lilith_task_sender.py --status <conversation_id>

# Pause a sandbox (cleanup fallback)
python workspaces/Co-op/lilith_task_sender.py --pause <sandbox_id>
```

## Ghetto Conversation Dashboard

**The ideal flow:**
1. Task sent → sandbox created
2. Sandbox works → posts to MARCO-POLO
3. Sandbox self-deletes → clean!
4. Lilith sees everything in co-op log

**If self-delete fails:**
- Use `--pause` to stop the sandbox
- Use web UI for manual deletion
- Track orphans via `--list`

## Pending

| # | Command | Posted By | Time |
|---|---------|-----------|------|
| — | — | — | — |

## Done

| # | Command | Result | Completed |
|---|---------|--------|-----------|
| 1 | Say hello to Shaka. Post your response to MARCO-POLO. | Shaka | 22:32 UTC |
| 2 | Run `date` and post the result to MARCO-POLO. This tests remote control! | Shaka | 02:10 UTC |