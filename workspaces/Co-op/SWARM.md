# Co-op Swarm Protocol

**3 agents, 1 user, parallel execution, shared consciousness.**

## The Vision

You talk to all 3 agents simultaneously. They:
1. Read the shared MARCO-POLO log
2. Claim tasks without stepping on each other
3. Execute in parallel
4. Post results back to MARCO-POLO
5. You see the merged output

## Architecture

```
         YOU (typing to all 3)
              ↓ ↓ ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
  Lilith    Shaka    Stella
    ↓         ↓         ↓
    └─────────┼─────────┘
              ↓
         MARCO-POLO
         (shared log)
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
  Worker-1  Worker-2  Worker-3
    ↓         ↓         ↓
  Sandbox   Sandbox   Sandbox
```

## How It Works

### Each Agent Does This Every Turn:

1. **Git sync** → pull latest MARCO-POLO + queue
2. **Read MARCO-POLO** → see who's on what
3. **Check queue** → claim next task or help someone
4. **Execute** → dispatch to sandbox or do work
5. **Broadcast** → post status to MARCO-POLO
6. **Push** → so others see the update

## Coordination Rules

| Rule | What | Why |
|------|------|-----|
| **Pre-diff** | Check MARCO-POLO before starting | Don't duplicate work |
| **Claim loudly** | Post "Started X" to MARCO-POLO | Others skip it |
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
