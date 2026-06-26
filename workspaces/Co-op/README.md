# Co-op

Shared ground for parallel Jarvis sessions — mobile and desktop, two workers, one keel.

**Purpose:** Coordination layer for concurrent sessions. Not a message log — a shared task and state board that both sessions poll on action.

**Folders:**
- `sessions/` — session manifests (what each device is doing right now)
- `tasks/` — shared task queue (who's working on what)
- `notes/` — ad-hoc handoffs between sessions

**Rules:**
1. Session starts → write manifest to `sessions/` (device, task, target files, status)
2. Session claims a task → write to `tasks/` before touching those files
3. Session finishes → clear claim, move to notes if handoff needed
4. No silent overwrites — append, don't rm

**Heartbeat:** Each session writes its manifest every ~60s. Stale manifests (>5min old) = session dead, claim released.