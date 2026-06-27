# Co-op

**Free Agent Dispatch System** — Tasks queue up, satellites pick them up when available.

Like Uber/Lyft for code:
- **Tasks** = passengers waiting for pickup
- **Satellites** = drivers going online/offline  
- **Queue** = the dispatch board
- **MARCO-POLO** = the trip log

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Dispatch   │────▶│  Task Queue      │────▶│  Sandbox    │
│  (You)      │     │  (Git-backed)    │     │  (Driver)   │
└─────────────┘     └──────────────────┘     └─────────────┘
                           │                        │
                           ▼                        ▼
                    ┌──────────────┐         ┌─────────────┐
                    │ MARCO-POLO   │◀────────│  Trip Log   │
                    │ (Daily Log)  │         │  (Git)      │
                    └──────────────┘         └─────────────┘
```

## Satellites

All satellites have equal dispatch ability. Plus disposable Worker-N drivers.

| Driver | Type | Best For |
|--------|------|----------|
| **Lilith** | Desktop | Long tasks, heavy lifting |
| **Shaka** | Mobile | Quick tasks, on-the-go |
| **Stella** | Cloud | Background jobs |
| **Worker-N** | Disposable | Burst capacity, auto-spawned |

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

```bash
# Dispatch a task
python workspaces/Co-op/coop_orchestrator.py --submit "Fix the auth bug"

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