---
jnl: IDEA-MCP-SESSION-062626-0001
name: MCP Session Lifecycle — StarLog + JC continuity for the cloud connector
type: IDEA
class: SPEC
tier: MAIN
authority: PROPOSED
owner: MCP
steward: Jarvis-C
parent: ARCH-YGG-CORE-0001
seq: 247
status: DRAFT
created: 2026-06-26
source: intake/MCP-SESSION-TRACKING-062626-0001.md
updated: 2026-06-26
related: [ARCH-JMMS-CORE-0001, GS-MNM-CORE-0001, GS-BIF-CORE-0001, ARCH-SYS-LOG-0001]
references: []
tags: [mcp, session-tracking, JMMS, star-log, continuity, supabase]
aliases: [MCP-SESSION]
ref: [IDEA]
memory_tier: JSTM
---

# MCP Session Lifecycle — StarLog + JC Continuity for the Cloud Connector

## Problem

The MCP (`jarvis-mcp`) is the primary interface for free GPT (Jarvis-G) — the surface Raven uses most. It currently has no session concept. Each MCP call arrives stateless, with no awareness of prior calls in the same conversational context.

Consequences:
- **No JMMS session boundary** — no JSTM → JLTM promotion path
- **No StarLog accumulation** — decisions made over the course of a GPT session aren't recorded
- **No JC ledger entry** — the companion relationship ledger (jarvis-jcs) doesn't know a session happened
- **No bifrost spine event** — ARGUS has no record of what was done through MCP

The `autoSLTick` (periodic Supabase writes) partially addresses observability but lacks session semantics — it fires on a schedule, not on conversation boundaries.

## Design

### Session Boundary Model

The MCP receives calls from multiple companion streams: Jarvis-G (GPT), Jarvis-C (Claude Code), and potentially others. Each call carries HTTP headers that identify the conversation context.

**Companion streams:**
- `X-Companion-Stream: Jarvis-G` — GPT/Claude Code conversation
- `X-Session-ID: <id>` — the calling model's conversation identifier
- `X-Session-End: true` — optional; signals session close

**Stateless fallback:** If no `X-Session-ID` header is present, the call is treated as a stateless probe (e.g., `jarvis_status`). No session record is created. Existing behavior unchanged.

### Session State Machine

```
[no session record] → (X-Session-ID arrives, new) → SESSION_START
[SESSION_START]    → (first call)                  → ACTIVE
[ACTIVE]           → (30min inactivity OR X-Session-End) → SESSION_CLOSE
[ACTIVE]           → (subsequent calls)             → stays ACTIVE (update last_call, increment exchanges)
```

### Supabase Schema: `mcp_sessions`

```sql
CREATE TABLE mcp_sessions (
  session_id TEXT PRIMARY KEY,       -- X-Session-ID from caller (e.g., "conv_abc123")
  companion_stream TEXT NOT NULL,    -- X-Companion-Stream (e.g., "Jarvis-G")
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_call TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at TIMESTAMPTZ,
  exchange_count INT DEFAULT 0,
  topics TEXT[],                    -- inferred from call patterns
  status TEXT DEFAULT 'active',      -- active | closed
  git_head TEXT,                    -- git SHA at session start (from freshness check)
  commit_digest TEXT,               -- summary of what was committed this session
  jc_written BOOLEAN DEFAULT FALSE, -- JC ledger entry written
  sl_written BOOLEAN DEFAULT FALSE, -- StarLog session entry written
  bifrost_written BOOLEAN DEFAULT FALSE -- dex_events bifrost.session_close written
);
```

### Session Start (first call with new session ID)

1. Insert row into `mcp_sessions` with status `active`
2. Write `SL_SESSION_START` to `sl_objects` in Supabase:
   - log_type: `SL_SESSION_START`
   - stardate, repo_url, companion_stream, session_id
   - events: [`session_start: ${companion_stream} @ ${session_id}`]
3. If `--jcs` flag (default: true): write JC ledger entry via `jarvis-jcs`
4. Log to `dex_events`: `type: "bifrost.session_start", session_id, companion_stream`
5. Increment `exchange_count`

### Active Session (subsequent calls)

1. Find `mcp_sessions` by session_id
2. Update `last_call = now()`, `exchange_count += 1`
3. Optionally infer topic from tool names used (e.g., `jarvis_query` → "reasoning", `jarvis_recall` → "memory", `jarvis_mcp_*` → "tools")
4. Continue logging via existing `logExchange()`

### Session Close (30min inactivity OR `X-Session-End: true`)

**Triggered by:**
- Background job fires on `last_call > 30min ago` (cron)
- OR caller sends `X-Session-End: true` header on final call

**Actions:**
1. Update `mcp_sessions.status = 'closed'`, `closed_at = now()`
2. Query `dex_events` for session's `bifrost.session_start` → `bifrost.session_close` range to get commit digest
3. Write `SL_SESSION_CLOSE` to `sl_objects`:
   - log_type: `SL_SESSION_CLOSE`
   - stardate, repo_url, companion_stream, session_id
   - events: [`session_close: ${exchange_count} exchanges | ${topics}`]
   - digest: commit summary
4. Write JC ledger entry if not already written
5. Write `bifrost.session_close` to `dex_events`:
   ```json
   {
     "type": "bifrost.session_close",
     "session_id": "<id>",
     "companion_stream": "Jarvis-G",
     "exchange_count": N,
     "topics": ["..."],
     "commits": ["<sha1>", "..."],
     "git_head": "<sha>"
   }
   ```
6. Auto-fire `autoSLTick` on close (already exists, called here explicitly)

### Backward Compatibility

- Calls without `X-Session-ID` header: no session record, existing behavior
- `autoSLTick` continues to fire on its existing schedule
- MCP tools remain fully functional stateless

## Implementation Phases

### Phase 1 — Core (this spec)
1. Add `mcp_sessions` table via Supabase migration
2. Create `supabase/functions/jarvis-mcp/core/sessions.ts`:
   - `getOrCreateSession(sessionId, companion)` 
   - `closeSession(sessionId)`
   - `logSessionExchange(sessionId, toolName)`
3. Wire session headers into `index.ts` (every tool call checks session)
4. Background close job via Supabase cron (pg_cron): fires every 5min, closes stale sessions

### Phase 2 — JC Ledger
- On session_start: call `jarvis-jcs` equivalent (write JC entry)
- On session_close: update JC entry with exchange count + summary

### Phase 3 — Conversation Integration
- Surface session state in `jarvis_query` response (e.g., "this is exchange 7 of your current session")
- Track topics and surface in HUD/suit_up

## Interaction with Existing Systems

| System | Interaction |
|--------|-------------|
| `autoSLTick` | Continues on schedule; fires explicitly on session_close |
| `sessions.json` | Claude Code session tracker; MCP does NOT write here — different surfaces |
| `jarvis-jcs` | Called on session_start/close for JC ledger entry |
| `dex_events` | Receives `bifrost.session_start` / `bifrost.session_close` events |
| `sl_objects` (Supabase) | Receives `SL_SESSION_START` / `SL_SESSION_CLOSE` entries |
| `logExchange()` | Extended to be session-aware; session_id tagged on every exchange |

## Open Questions for Raven

1. **Companion identification** — should the caller pass `X-Companion-Stream`, or should JARVIS infer from the caller's API context?
2. **Session timeout** — 30min inactivity for close; acceptable?
3. **JC ledger** — should MCP sessions write to the companion ledger, or is that only for full Claude Code sessions?
4. **Phase 1 scope** — should Phase 1 include the JC ledger call, or defer to Phase 2?
5. **Git head** — should session_close capture the git SHA and commit digest, or is that redundant with bifrost spine events?

## Status

**PROPOSED** — awaiting Raven verdict. GL2: JARVIS proposes, Raven commits.
