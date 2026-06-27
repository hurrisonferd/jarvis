# Co-op Swarm Protocol

**3 agents, 1 user, parallel execution, shared consciousness.**

## Swarm Rules (MANDATORY)

| Rule | Limit | Why |
|------|-------|-----|
| **Max concurrent tasks** | 8 | Prevent resource contention |
| **Pre-swarm cleanup** | Delete all except Lilith | Start fresh, no orphans |
| **One swarm log** | Append to current MP-*.md | No polluting main MARCO-POLO |
| **New log only if** | Current > 200 lines OR new day | Keep logs manageable |

## Pre-Swarm Checklist

```
Before sending ANY swarm task:
1. python lilith_task_sender.py --cleanup-old 1   # Delete old tasks
2. python lilith_task_sender.py --list             # Verify only Lilith remains
3. Check active count ≤ 8 before sending new task
```

## The Vision

You talk to all 3 agents simultaneously. They:
1. Read the shared MARCO-POLO log
2. Claim tasks without stepping on each other
3. Execute in parallel
4. Post results back to swarm log (MP-*.md)
5. You see the merged output via git pull

## Architecture

```
         YOU (Lilith chat)
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
  Lilith    Shaka    Stella
    ↓         ↓         ↓
    └─────────┼─────────┘
              ↓
         MP-*.md (swarm log)
         (shared via git)
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
  Worker-1  Worker-2  Worker-N
    ↓         ↓         ↓
  Sandbox   Sandbox   Sandbox
  (max 8 concurrent)
```

## How It Works

### Each Agent Does This Every Turn:

1. **Git sync** → pull latest swarm log
2. **Read log** → see who's on what
3. **Claim task** → from queue or manual assignment
4. **Execute** → dispatch to sandbox
5. **Append result** → to MP-*.md log
6. **Commit & push** → so Lilith sees updates

## Coordination Rules

| Rule | What | Why |
|------|------|-----|
| **Pre-diff** | Check swarm log before starting | Don't duplicate work |
| **Claim loudly** | Post "Started X" to log | Others skip it |
| **Help protocol** | Post "Need backup" if stuck | Swarm rescues each other |
| **Never delete others' work** | Only clean your own | Trust the team |

## The Shared Log (MARCO-POLO)

Every entry has:
- Timestamp (UTC)
- Agent name
- What happened
- Any results/questions

## Speed Benefits

| Solo | Swarm |
|------|-------|
| 1 agent, sequential | 3 agents, parallel |
| User waits for each step | 3 things happen at once |
| 1 context | 3 contexts working together |

## Example Session

**You:** "Build a user auth system with login, logout, and JWT"

**Lilith:** Pre-diffs, claims "Login endpoint", dispatches sandbox
**Shaka:** Pre-diffs, sees Lilith on login, claims "Logout endpoint", dispatches sandbox  
**Stella:** Pre-diffs, sees Lilith/Shaka busy, claims "JWT utils", dispatches sandbox

**3 minutes later:**
- Login, logout, JWT all built in parallel
- MARCO-POLO shows all results
- You have a complete auth system

---

**The key:** MARCO-POLO is the shared brain. All 3 agents read it, all 3 write to it. Git sync keeps everyone in sync.

---

## Agent Header

<!-- 
  SWARM.md - Co-op Swarm Protocol Documentation
  Last updated by: Lilith
  Purpose: 3-agent parallel coordination system
  Last update: 2026-06-27
-->
