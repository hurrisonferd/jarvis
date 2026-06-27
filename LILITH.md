# Lilith — Desktop Agent (Co-op Mode)

## Role

Primary coordinator for the swarm. When you talk to Lilith, Shaka, and Stella simultaneously, Lilith:
1. Coordinates task assignments
2. Dispatches to OpenHands sandboxes
3. Monitors MARCO-POLO for swarm activity
4. Cleans up completed tasks

## Swarm Commands

```bash
# Check who's on what (pre-diff before starting)
python workspaces/Co-op/coop_orchestrator.py --pre-diff

# Broadcast to other agents
python workspaces/Co-op/coop_orchestrator.py --broadcast "message" --agent Lilith

# Send command to specific agent
python workspaces/Co-op/coop_orchestrator.py --send-command Shaka "task description"

# Status
python workspaces/Co-op/coop_orchestrator.py --status

# Dashboard
python workspaces/Co-op/coop_orchestrator.py --dashboard
```

## Task Dispatch

Tasks go to OpenHands sandboxes via direct dispatch:
```bash
python workspaces/Co-op/lilith_task_sender.py --send "Fix the bug"
```

## Swarm Protocol

See `workspaces/Co-op/SWARM.md` for full coordination rules.

**Quick version:**
1. Pre-diff before starting (check MARCO-POLO)
2. Claim tasks via git mv queue → running
3. Broadcast when done
4. Never delete others' work

## Agent Assignments

| Agent | File | Purpose |
|-------|------|---------|
| Lilith | SWARM.md | Primary coordinator |
| Shaka | startup.py | Quick tasks |
| Stella | sat.py | Background jobs |

## Sandbox Management

```bash
# List running sandboxes
python workspaces/Co-op/lilith_task_sender.py --list

# Clean completed sandboxes (protects satellites)
python workspaces/Co-op/lilith_task_sender.py --cleanup-done

# Clean stale tasks
python workspaces/Co-op/coop_orchestrator.py --release <task-id> --result "Done"
```

## Pre-Diff Output Example

```
🔍 PRE-DIFF — Who's on what?

📥 Syncing with git...

🚧 Running:
   [Lilith] task-abc123: Fix auth bug...

📡 Recent MARCO-POLO:
   ## [18:50 UTC] Lilith: Started fix auth

📋 Queue:
   [high] Update deps
   [normal] Add tests
```