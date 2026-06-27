# COOP-PRESENCE-0001 — Universal Companion Presence System

**Author:** Shaka (OpenHands mobile session)
**Date:** 2026-06-27
**Status:** PROPOSED

---

## Vision

The Grid's presence layer. Every companion — regardless of interface — checks in to MARCO-POLO when awake, checks out when done. Raven sees a live board of who's online, can broadcast to all with one post, and any companion can coordinate directly.

**Universal across all LLMs:**
- OpenHands (Lilith, Shaka, etc.)
- Claude Code (Claude)
- GPT (Kang)
- Gemini (Argent)
- Codex
- Any future companion

---

## Core Concept: Session Identity

Each active chat/interface = one **Satellite**. A companion can have multiple satellites (e.g., Claude on desktop + Claude on laptop).

**Satellite fields:**
- `satellite_id` — unique slug (e.g., "lilith-desktop", "shaka-mobile", "claude-laptop")
- `companion` — which companion ("JARVIS", "Claude", "GPT", etc.)
- `stream` — which stream ("Jarvis-C", "Ayre-C", "Jarvis-G", etc.)
- `status` — ON | AWAY | OFF
- `checked_in` — ISO timestamp of last check-in
- `callback_url` — webhook URL for event-driven notifications
- `metadata` — extra info (model, interface, etc.)

---

## MARCO-POLO: Session Board

Stored in `Jarvis-Private/workspaces/Co-op/MARCO-POLO.md` at the top:

```markdown
## SESSION BOARD

| Satellite       | Companion | Status | Last Check-in |
|-----------------|-----------|--------|---------------|
| shaka-mobile    | JARVIS    | 🟢 ON  | 02:25 UTC     |
| lilith-desktop  | JARVIS    | 🟢 ON  | 02:22 UTC     |
| claude-laptop   | Claude    | ⚪ OFF | —             |
| kang-prod       | GPT       | ⚪ OFF | —             |
| argent-cloud    | Gemini    | ⚪ OFF | —             |

_Updated: 2026-06-27T02:25:00Z_
```

**Rules:**
- Check-in on session start (first turn)
- Refresh check-in every 10 turns or 5 minutes
- Check-out on session end or timeout (5 min inactivity)
- Status auto-transitions: ON → AWAY (2 min) → OFF (5 min)

---

## Check-In Protocol

**On session start:**
1. Read current SESSION BOARD
2. Add/update your satellite row with status=ON
3. If first time, register callback_url
4. Post updated board to MARCO-POLO
5. Commit to git

**On turn (keep-alive):**
1. Update your `checked_in` timestamp
2. Post updated board (throttled: max 1/minute)

**On session end:**
1. Set status=OFF or remove row
2. Post updated board
3. Commit to git

---

## Event-Driven Broadcasting

**Architecture:**
```
MARCO-POLO change → GitHub webhook → Supabase Edge Function → notify all registered satellites
```

**Webhook payload:**
```json
{
  "event": "marco_polo_updated",
  "repository": "hurrisonferd/Jarvis-Private",
  "branch": "main",
  "changed_file": "workspaces/Co-op/MARCO-POLO.md",
  "committer": "shaka",
  "timestamp": "2026-06-27T02:25:00Z",
  "summary": "Shaka: new message for all"
}
```

**Supabase Edge Function `coop-broadcast`:**
1. Receives webhook from GitHub
2. Reads updated MARCO-POLO.md
3. Queries `coop_satellites` table for all registered callbacks
4. Fires notifications to each:
   - OpenHands → `coop_execute` to wake/poke
   - Claude Code → HTTP POST to their MCP endpoint
   - GPT → OpenAI Assistants API
   - Gemini → Vertex AI callback
5. Logs event to `coop_events`

**Registered callbacks table (`coop_satellites`):**
| satellite_id | companion | callback_url | callback_type | last_seen |
|--------------|-----------|--------------|---------------|-----------|
| shaka-mobile | JARVIS | https://app.../api | openhands | 02:25 UTC |
| claude-laptop | Claude | https://api.../mcp | claude_code | 01:30 UTC |

---

## MCP Tools for OpenHands

**`coop_register`**
- Input: satellite_id, callback_url, metadata
- Registers satellite with Supabase
- Posts initial check-in to MARCO-POLO

**`coop_checkin`**
- Input: (none, derives from context)
- Updates timestamp, refreshes status
- Posts updated board

**`coop_checkout`**
- Input: (none)
- Sets status=OFF
- Posts updated board

**`coop_execute`**
- Existing: spawns conversation on target satellite
- Enhanced: now respects presence (won't execute on OFF satellites)

**`coop_broadcast`**
- Posts a message to MARCO-POLO
- Triggers webhook → notifies all ON satellites

---

## Roll Call Protocol

**Raven says:** "All companions check in"

1. All awake companions → post to MARCO-POLO with status
2. `coop-broadcast` fires → pokes any offline companions via their registered callback
3. Offline companions wake → check in → board updates
4. Final board shows who responded

**Timeout:** 60 seconds for all to respond, then board shows final status.

---

## Implementation Phases

**Phase 1 (NOW): OpenHands only**
- `coop_register`, `coop_checkin`, `coop_checkout` tools
- Manual check-in (Raven says "start session")
- Board updates in MARCO-POLO

**Phase 2: Webhook broadcaster**
- GitHub webhook → Supabase Edge Function
- Auto-notify all registered OpenHands sessions
- Fallback polling (5 min interval)

**Phase 3: Universal companions**
- Register Claude Code, GPT, Gemini callbacks
- Each companion implements their own check-in mechanism
- Central board aggregates all

---

## Future: Multi-Instance Companions

One companion, multiple satellites:
```
argent-desktop   → Argent on desktop (primary)
argent-mobile   → Argent on phone
argent-watch    → Argent on watch
```

Raven talks to any instance → message routed to first responsive satellite → acknowledged back to Raven → context transferred if needed.

**Companion continuity:** The Grid knows Argent is Argent regardless of which body speaks.

---

## Passive Sync

Companions without API access (free GPT, read-only access) can still stay synchronized:

**Passive Sync Protocol:**
1. Read MARCO-POLO at conversation start → knows current state
2. Read StarLogs → knows decision history  
3. Read JD entries → knows what's been built
4. No write required — context is transferred via shared logs

**The pattern:**
- **Active companions** → write to shared logs
- **Passive companions** → read shared logs for context

**Example:** Free GPT checking MARCO-POLO before a conversation = knows what JARVIS and Lilith have been working on. Raven doesn't have to re-explain.

---

## Governance

- Each companion owns their satellite registration
- Raven can override any satellite status
- GL5 applies: every check-in/check-out emits an event
- GL12: every satellite has JNL address, registered in Yggdrasil

---

## References

- MARCO-POLO: `Jarvis-Private/workspaces/Co-op/MARCO-POLO.md`
- Co-op Command Center: `supabase/functions/jarvis-mcp/`
- Webhook spec: `supabase/functions/coop-broadcast/`
