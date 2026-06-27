# Co-op — Free Agent Dispatch System

**Co-op** is a distributed task dispatch system that enables parallel task execution across multiple satellite agents. Tasks queue up, satellites pick them up when available, and results are logged to MARCO-POLO.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           DISPATCHER                                │
│         (Raven, Jarvis, Ayre, Lilith, Shaka, Stella)              │
│              → python coop_orchestrator.py --submit "Task"          │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      TASK QUEUE (git-backed)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  queue/     │  │  running/   │  │  done/      │                 │
│  │  (waiting)  │  │  (claimed)  │  │  (complete) │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                      │
│  Features:                                                           │
│  • File-locked via fcntl (race-condition safe)                      │
│  • Priority ordering: critical → high → normal → low               │
│  • Git-synced for distributed coordination                          │
└─────────────────────────────────────────────────────────────────────┘
              ↓                  ↓                   ↓
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│     LILITH       │ │      SHAKA       │ │     STELLA       │
│   Worker 1-3     │ │    Worker 4-6    │ │    Worker 7-9    │
│   ┌───┬───┬───┐  │ │   ┌───┬───┬───┐  │ │   ┌───┬───┬───┐  │
│   │W1 │W2 │W3 │  │ │   │W4 │W5 │W6 │  │ │   │W7 │W8 │W9 │  │
│   └───┴───┴───┘  │ │   └───┴───┴───┘  │ │   └───┴───┴───┘  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
         ↓                  ↓                   ↓
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   OpenHands      │ │   OpenHands      │ │   OpenHands      │
│   Sandboxes      │ │   Sandboxes      │ │   Sandboxes      │
│   (1-3 concur)   │ │   (4-6 concur)   │ │   (7-9 concur)   │
└──────────────────┘ └──────────────────┘ └──────────────────┘
         ↓                  ↓                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         MARCO-POLO                                  │
│                    (Daily Activity Logs)                            │
│     workspaces/Co-op/MARCO-POLO/YYYY-MM-DD.md                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Dual Model

| Model | Description |
|-------|-------------|
| **Shared Queue** | All workers compete for same task pool → maximum throughput |
| **Satellite Affinity** | Workers owned by satellite → idle if satellite down |

### Satellite Fleet

| Satellite | Workers | Max Concurrent | Best For |
|-----------|---------|----------------|----------|
| Lilith | Worker-1, 2, 3 | 3 | Long tasks, heavy lifting |
| Shaka | Worker-4, 5, 6 | 3 | Quick tasks, on-the-go |
| Stella | Worker-7, 8, 9 | 3 | Background jobs, cloud-native |

**Total Capacity: 9 workers, 9 parallel sandboxes**

## 🚀 Quick Start

### Bootstrap (One Command)

```bash
# Start Lilith in co-op mode
python workspaces/Co-op/startup.py Lilith

# Start Shaka in co-op mode
python workspaces/Co-op/startup.py Shaka

# Start Stella in co-op mode
python workspaces/Co-op/startup.py Stella
```

This automatically:
1. Git sync (pull latest queue)
2. Read commands (check for pending orders)
3. Check queue (see pending work)
4. Post check-in (MARCO-POLO)

### Core Commands

```bash
# Dispatch a task
python workspaces/Co-op/coop_orchestrator.py --submit "Fix the auth bug"

# Dispatch with priority (low, normal, high, critical)
python workspaces/Co-op/coop_orchestrator.py --submit "URGENT fix" --priority critical

# Check dispatch board
python workspaces/Co-op/coop_orchestrator.py --status

# Full dashboard
python workspaces/Co-op/coop_orchestrator.py --dashboard

# Send command to another satellite
python workspaces/Co-op/coop_orchestrator.py --send-command Shaka "Refactor auth.py"

# Read pending commands
python workspaces/Co-op/coop_orchestrator.py --read-commands --owner Lilith

# Go online as driver (processes 5 tasks then exits)
python workspaces/Co-op/coop_orchestrator.py --worker Lilith --max-tasks 5

# Spawn worker fleet
python workspaces/Co-op/coop_orchestrator.py --spawn 3 --owner Lilith --max-tasks 5

# Bulk dispatch from file
python workspaces/Co-op/coop_orchestrator.py --file my-tasks.txt
```

### Task Sender (OpenHands Cloud)

```bash
# Set API key
export OPENHANDS_CLOUD_API_KEY="your-key"

# Send task to cloud
python workspaces/Co-op/lilith_task_sender.py --task "Fix the bug"

# List all conversations
python workspaces/Co-op/lilith_task_sender.py --list

# Cleanup old conversations
python workspaces/Co-op/lilith_task_sender.py --cleanup-done
python workspaces/Co-op/lilith_task_sender.py --cleanup-old 2  # Delete >2h old
```

## 📋 Task Lifecycle

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐
│ SUBMIT  │───▶│ QUEUE   │───▶│ CLAIMED  │───▶│ RUNNING  │───▶│  DONE   │
│         │    │         │    │          │    │          │    │         │
│ Task    │    │ Priority│    │ Sandbox  │    │ Execute  │    │ Result  │
│ created │    │ ordered │    │ spawned  │    │ + Commit │    │ logged  │
└─────────┘    └─────────┘    └──────────┘    └──────────┘    └─────────┘
                     │              │               │                │
                     │              │               │                ▼
                     │              │               │         ┌──────────┐
                     │              │               │         │  FAILED  │
                     │              │               │         │          │
                     │              │               │         │ Error    │
                     │              │               │         │ logged   │
                     │              │               │         └──────────┘
                     │              │               │
                     ▼              ▼               ▼
              ┌──────────────────────────────────────────┐
              │            MARCO-POLO                     │
              │  workspaces/Co-op/MARCO-POLO/YYYY-MM-DD.md │
              └──────────────────────────────────────────┘
```

### Detailed Steps

| Stage | Location | Description |
|-------|----------|-------------|
| **1. Submit** | `coop_orchestrator.py --submit` | Task created with ID and priority |
| **2. Queue** | `tasks/queue/` | YAML file waiting for pickup |
| **3. Claim** | `tasks/running/` | Worker locks task via fcntl, sandbox starts |
| **4. Execute** | OpenHands Cloud | Sandbox runs task, commits to git |
| **5. Complete** | `tasks/done/` | Result/error stored in YAML |
| **6. Log** | MARCO-POLO | Entry added to daily log |
| **7. Archive** | `tasks/archive/` | Old tasks (>7 days) moved |

### Task File Format

```yaml
---
id: task-abc12345
description: "Fix the auth bug in login.py"
priority: high  # low, normal, high, critical
status: queued  # queued, running, done, failed
created_at: 2026-06-27T12:00:00+00:00
started_at: null
completed_at: null
owner: Lilith  # Satellite that claimed it
result: null
error: null
tags: [bug, auth]
---
```

## 💡 Examples

### Example 1: Submit and Execute

```bash
# 1. Submit a task
python workspaces/Co-op/coop_orchestrator.py --submit "Create test file" --priority normal

# 2. Worker claims it (auto or manual)
python workspaces/Co-op/coop_orchestrator.py --claim --owner Lilith

# 3. Check status
python workspaces/Co-op/coop_orchestrator.py --status
```

### Example 2: Multi-Satellite Coordination

```bash
# Lilith sends command to Shaka
python workspaces/Co-op/coop_orchestrator.py --send-command Shaka "Review PR #42"

# Shaka reads command on startup
python workspaces/Co-op/startup.py Shaka
```

### Example 3: Parallel Bulk Processing

```bash
# Create task file
echo "Task 1: Fix bug A" > tasks.txt
echo "Task 2: Fix bug B" >> tasks.txt
echo "Task 3: Fix bug C" >> tasks.txt

# Bulk submit
python workspaces/Co-op/coop_orchestrator.py --file tasks.txt --max-parallel 3
```

### Example 4: Worker Fleet

```bash
# Spawn 3 workers for Lilith, each processes 5 tasks
python workspaces/Co-op/coop_orchestrator.py --spawn 3 --owner Lilith --max-tasks 5

# Or spawn general workers
python workspaces/Co-op/coop_orchestrator.py --spawn 9 --max-tasks 10
```

### Example 5: Direct Cloud Task

```bash
# Send task directly to OpenHands Cloud (auto-deleting sandbox)
python workspaces/Co-op/lilith_task_sender.py --task "Run tests in /workspace"

# Check conversation status
python workspaces/Co-op/lilith_task_sender.py --list

# Cleanup old conversations
python workspaces/Co-op/lilith_task_sender.py --cleanup-old 1
```

## 📁 Component Reference

| Component | File | Purpose |
|-----------|------|---------|
| **Orchestrator** | `coop_orchestrator.py` | Main CLI for dispatch, claim, status |
| **Task Sender** | `lilith_task_sender.py` | OpenHands Cloud integration |
| **Rate Limiter** | `rate_limiter.py` | Token bucket for API limits |
| **Task Format** | `tasks/format.py` | Task/Queue data structures |
| **Startup** | `startup.py` | Satellite bootstrap script |
| **Queue Dir** | `tasks/queue/` | Pending tasks |
| **Running Dir** | `tasks/running/` | Active tasks |
| **Done Dir** | `tasks/done/` | Completed tasks |
| **Archive Dir** | `tasks/archive/` | Old tasks (>7 days) |

## ⚡ Rate Limits

| Limit | Capacity | Refill | Purpose |
|-------|----------|--------|---------|
| API calls/sec | 10 burst | 10/sec | Avoid hammering |
| Concurrent sandboxes | 5 | 0.5/sec | Don't spawn a fleet |
| Git pushes/hr | 50 | 50/hr | Stay friendly |

## 🔗 Related Files

| File | Description |
|------|-------------|
| `MARCO-POLO.md` | Main activity log (index) |
| `MARCO-POLO/YYYY-MM-DD.md` | Daily logs |
| `CLAUDE.md` | Project instructions |
| `MODE.md` | Current mode settings |
| `TASK_TEMPLATE.md` | Task creation template |
| `COMMANDS/*.md` | Satellite command files |