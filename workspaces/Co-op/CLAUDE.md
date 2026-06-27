# Co-op — Satellite Dispatch System

## One-Command Bootstrap

```bash
python workspaces/Co-op/startup.py <SatelliteName>
```

Example: `python workspaces/Co-op/startup.py Lilith`

This spawns 3 workers in infinite loop, polling shared queue.

## Natural Commands (sat.py)

```bash
python workspaces/Co-op/sat.py "Net Status?"              # Fleet overview
python workspaces/Co-op/sat.py "Queue?"                   # Pending tasks
python workspaces/Co-op/sat.py "Tell Stella to do X"      # Inter-satellite
python workspaces/Co-op/sat.py "Spawn 2 workers"          # Scale up
python workspaces/Co-op/sat.py "Worker 5 do the thing"    # Direct worker
```

## Key Files

| File | Purpose |
|------|---------|
| `startup.py` | Bootstrap satellite + workers |
| `sat.py` | Natural language interface |
| `coop_orchestrator.py` | Core dispatch logic |
| `tasks/format.py` | Task queue with fcntl locking |
| `lilith_task_sender.py` | OpenHands Cloud API client |

## Architecture

- **Shared Queue**: All 9 workers (3 per satellite) pull from same pool
- **File Locking**: `fcntl.flock` prevents race conditions on claim
- **Infinite Loop**: Workers run forever, auto-requeue after dispatch
- **Satellite Affinity**: Workers owned by satellite, idle if satellite down

## Worker Ranges

- Lilith: Worker-1, Worker-2, Worker-3
- Shaka: Worker-4, Worker-5, Worker-6
- Stella: Worker-7, Worker-8, Worker-9