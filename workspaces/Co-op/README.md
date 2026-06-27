# Co-op

**Free Agent Dispatch System** — Tasks queue up, satellites pick them up when available.

Like Uber/Lyft for code:
- **Tasks** = passengers waiting for pickup
- **Satellites** = drivers going online/offline  
- **Queue** = the dispatch board
- **MARCO-POLO** = the trip log

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Dispatcher (Raven, Jarvis, Ayre, or Satellite)     │
│     → python sat.py "Do the thing"                  │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  TASK QUEUE (git-backed, file-locked)               │
│     → All workers pull from SAME queue              │
│     → Priority ordering (critical → low)            │
│     → Race-condition safe via fcntl                 │
└─────────────────────────────────────────────────────┘
           ↓          ↓          ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Lilith   │  │ Shaka    │  │ Stella   │
│ Workers  │  │ Workers  │  │ Workers  │
│ 1, 2, 3  │  │ 4, 5, 6  │  │ 7, 8, 9  │
└──────────┘  └──────────┘  └──────────┘
     ↓              ↓              ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│Sandbox 1 │  │Sandbox 4 │  │Sandbox 7 │  ← 9 parallel
│Sandbox 2 │  │Sandbox 5 │  │Sandbox 8 │     sandboxes
│Sandbox 3 │  │Sandbox 6 │  │Sandbox 9 │
└──────────┘  └──────────┘  └──────────┘
```

## Dual Model: Shared Queue + Satellite Affinity

**Shared Queue:** All workers compete for same task pool — maximum throughput.

**Satellite Affinity:** Workers owned by satellite, idle if satellite down.

| Satellite | Worker Pool | Parallel Sandboxes |
|-----------|-------------|-------------------|
| Lilith    | Worker-1, 2, 3 | 3 concurrent |
| Shaka     | Worker-4, 5, 6 | 3 concurrent |
| Stella    | Worker-7, 8, 9 | 3 concurrent |

**Total: 9 workers, 9 parallel sandboxes**

## Satellites

All satellites have equal dispatch ability. Plus Worker-N drivers that auto-spawn on startup.

| Driver | Type | Best For |
|--------|------|----------|
| **Lilith** | Desktop | Long tasks, heavy lifting |
| **Shaka** | Mobile | Quick tasks, on-the-go |
| **Stella** | Cloud | Background jobs |
| **Worker-N** | Disposable | Parallel burst capacity |

### Spawn Workers

```bash
# Spawn 3 Worker-N drivers (auto-named Worker-1, Worker-2, Worker-3)
python workspaces/Co-op/coop_orchestrator.py --spawn 3 --max-tasks 5

# Workers auto-claim from queue, complete tasks, then exit
```

## Components

| File | Purpose |
|------|---------|
| `coop_orchestrator.py` | Main dispatch CLI |
| `lilith_task_sender.py` | Send tasks to OpenHands Cloud |
| `rate_limiter.py` | Token bucket for API limits |
| `tasks/format.py` | Task data structures |
| `tasks/queue/` | Waiting passengers |
| `tasks/running/` | In-trip (owned) |
| `tasks/done/` | Completed trips |
| `tasks/archive/` | Old trips (>7 days) |

## Quick Start

**Bootstrap (one command to rule them all):**
```bash
# "Lilith, co-op mode"
python workspaces/Co-op/startup.py Lilith

# "Shaka, co-op mode"
python workspaces/Co-op/startup.py Shaka

# "Stella, co-op mode"  
python workspaces/Co-op/startup.py Stella
```

This runs the full chain:
1. Git sync (pull latest)
2. Read commands (check for orders)
3. Check queue (see pending work)
4. Post check-in (MARCO-POLO)

**Individual commands:**
```bash
# Dispatch a task
python workspaces/Co-op/coop_orchestrator.py --submit "Fix the auth bug"

# Send command to another satellite
python workspaces/Co-op/coop_orchestrator.py --send-command Shaka "Refactor auth.py"

# Check dispatch board
python workspaces/Co-op/coop_orchestrator.py --status

# Full dashboard
python workspaces/Co-op/coop_orchestrator.py --dashboard

# Go online as driver
python workspaces/Co-op/coop_orchestrator.py --worker Lilith --max-tasks 5

# Bulk dispatch from file
python workspaces/Co-op/coop_orchestrator.py --file my-tasks.txt
```

## Task Lifecycle

1. **Dispatch** → Task added to queue (`tasks/queue/`)
2. **Pickup** → Driver claims it → sandbox spins up
3. **Trip** → Sandbox executes, commits work
4. **Completion** → Result posted to MARCO-POLO daily log
5. **Archive** → Old tasks moved after 7 days

## Rate Limits

| Limit | Value | Purpose |
|-------|-------|---------|
| API calls/sec | 10 burst | Avoid hammering |
| Concurrent sandboxes | 5 | Don't spawn a fleet |
| Git pushes/hr | 50 | Stay friendly |

## Coordination

Git-backed queue = built-in conflict resolution.

File-based ownership = no two drivers pick up same job.

```bash
# Submit with priority
python coop_orchestrator.py --submit "URGENT" --priority critical

# Priority levels: low, normal, high, critical
```

## Daily Logs

All trip logs go to daily files:
```
workspaces/Co-op/MARCO-POLO/2026-06-27.md
```