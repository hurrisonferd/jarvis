# Co-op Swarm Protocol

**Multi-agent parallel execution with specialized roles.**

## Swarm Roles

| Role | Purpose | Key Skills |
|------|---------|------------|
| **Architect** | Project planner | Breaks down requirements, assigns tasks, monitors |
| **Specialist** | Deep work | Builds one thing really well (engine, AI, etc.) |
| **Integrator** | Gap-filler | Fills stubs, wires components, runs tests |

## Swarm Rules (MANDATORY)

| Rule | Limit | Why |
|------|-------|-----|
| **Max concurrent tasks** | 8 | Prevent resource contention |
| **Auto-cleanup on send** | Enabled by default | Prevents cap overflow |
| **One swarm log** | Append to current MP-*.md | No polluting main MARCO-POLO |
| **New log only if** | Current > 200 lines OR new day | Keep logs manageable |

## Architecture

```
         YOU (Lilith)
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
  Architect  Specialist  Integrator
    ↓         ↓         ↓
    └─────────┼─────────┘
              ↓
         MP-*.md (swarm log)
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
  Worker-1  Worker-2  Worker-N
    ↓         ↓         ↓
  Sandbox   Sandbox   Sandbox
  (max 8 concurrent)
```

## Worker Templates

Templates are in `templates/`:
- `ARCHITECT.md` — Project planner workflow
- `INTEGRATOR.md` — Gap-filler workflow

## Speed Benefits

| Solo | Swarm (8 parallel) |
|------|-------------------|
| ~32 min for 8 tasks | ~4 min for 8 tasks |
| 1 task at a time | 8 tasks at once |
| 87.5% time saved |

## Example: Build a Game

**1. Architect** analyzes requirements → creates 8 specialist tasks
**2. Specialists** build engine, entities, systems, UI, audio, levels, effects, integration
**3. Integrator** fills stubs, wires components, runs tests
**4. Done!** Game works.

## How to Play the Game

**Option 1: Local Machine (recommended)**
```bash
# Clone the repo
git clone https://github.com/hurrisonferd/Jarvis-Private.git
cd Jarvis-Private/workspaces/Co-op/swarm-output

# Install dependencies
pip install pygame numpy

# Run!
python3 run.py
```

**Option 2: Remote with Display**
If running on a server with X11 forwarding:
```bash
ssh -X your-server
cd /path/to/Jarvis-Private/workspaces/Co-op/swarm-output
python3 run.py
```

**Option 3: Copy the folder**
The entire game is in `workspaces/Co-op/swarm-output/` — copy it anywhere and run.

Controls:
- **Arrow keys** — Move left/right
- **Space** — Shoot
- **P** — Pause
- **ESC** — Quit

**Game URL:** `workspaces/Co-op/swarm-output/`

## Pre-Swarm Checklist (auto-done now)

The task sender auto-cleans old conversations before sending. But manual check:
```bash
python lilith_task_sender.py --list
```

---

**The key:** Specialists build, Integrator fills gaps, auto-cleanup prevents crashes.

## Agent Header

<!-- 
  SWARM.md - Co-op Swarm Protocol Documentation
  Last updated by: Lilith
  Purpose: Multi-agent parallel coordination system
  Last update: 2026-06-28
-->
