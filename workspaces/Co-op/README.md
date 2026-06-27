# Co-op

**Vegapunk's Satellite System** — Lilith (desktop) and Shaka (mobile), two workers, one keel.

**Purpose:** Coordination layer for concurrent sessions. Not a message log — a shared task and state board that both sessions poll on action.

**Sessions:**
- **Lilith** — desktop (the original, more resources, longer sessions)
- **Shaka** — mobile (on-the-go, quick tasks, handoffs)

**Folders:**
- `sessions/` — session manifests (which satellite, what task, target files, heartbeat)
- `tasks/` — shared task queue (who's working on what)
- `notes/` — ad-hoc handoffs between satellites

**Rules:**
1. Session starts → write manifest to `sessions/` (satellite name, device, task, target files, status)
2. Session claims a task → write to `tasks/` before touching those files
3. Session finishes → clear claim, move to notes if handoff needed
4. No silent overwrites — append, don't rm

**Heartbeat:** Each satellite writes its manifest every ~60s. Stale manifests (>5min old) = satellite offline, claim released.

## Session Protocol

1. **Start** → pull Co-op, write manifest to `sessions/`, post to MARCO-POLO
2. **Each turn** → pull Co-op, check other satellite's manifest + MARCO-POLO
3. **Finish chunk** → update manifest, post summary to MARCO-POLO
4. **End session** → mark manifest done, post to MARCO-POLO