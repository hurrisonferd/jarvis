# Co-op

**Vegapunk's Satellite System** — Lilith (desktop) and Shaka (mobile), two workers, one keel.

**Purpose:** Orchestration layer for parallel sessions. You pilot both satellites from either device. Both poll Co-op on every turn.

**Satellites:**
- **Lilith** — desktop (the original, more resources, longer sessions)
- **Shaka** — mobile (on-the-go, quick tasks, handoffs)

**Folders:**
- `COMMANDS/` — where you post tasks for each satellite
  - `LILITH.md` — commands for desktop
  - `SHAKA.md` — commands for mobile
  - `SHARED.md` — tasks split between both (then merged)
- `sessions/` — session manifests (satellite name, device, task, heartbeat)
- `tasks/` — shared task queue (who's working on what)
- `notes/` — ad-hoc handoffs between satellites
- `MARCO-POLO.md` — shared log, both append

**Rules:**
1. You post command → either satellite picks it up on next turn
2. Satellite executes → posts result to MARCO-POLO
3. No silent overwrites — append to command files, mark done not deleted

## Session Protocol (each turn)

1. **Read commands** → check COMMANDS/{SATELLITE}.md for pending tasks
2. **Execute** → run the command, post result to MARCO-POLO
3. **Mark done** → move command to Done section
4. **Heartbeat** → update manifest with current task

## Example Usage

**From desktop:** "Lilith, run JVE" + "Shaka, check the JATM"
→ Both work in parallel, both post to MARCO-POLO

**From mobile:** "Shaka, audit the GRIMOIRE"
→ Shaka executes, Lilith sees result on next turn

**Shared task:** "Compare ARCHREFIDX across both repos"
→ Lilith checks jarvis, Shaka checks Jarvis-Private, merge in SHARED.md