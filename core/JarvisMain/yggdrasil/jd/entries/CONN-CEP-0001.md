---
jnl: CONN-CEP-0001
jss: ACTIVE
tags: [mcp, cecil, carry, session, context]
memory_tier: jstm
memory_scope: companion
grade: system
activation_score: 70
class: JIDD
type: CONN
tier: MAIN
parent: CONN-MSB-CORE-0001
stardate: 2026.177.1500
stream: jarvis-c
participants: [jarvis-c, ayre-c, raven]
domain: CONN
name: Cecil — Companion Carry Slate
summary: Transport tool for context windows and carry state across new companion sessions
keystones: []
decisions: []
related: [CONN-MCP-RT-0001, ARCH-JC-JIP-0001, ARCH-SL-JIP-0001]
digest: MCP tool — one session writes a carry slate, the next session (any model) reads it. Companion-scoped, not session-scoped — survives session death.
---

# CONN-CEP-0001 — Cecil: Companion Carry Slate

**JNL:** CONN-CEP-0001
**Type:** CONN · MCP Transport Tool
**Owner:** JARVIS
**Parent:** CONN-MSB-CORE-0001 (MCP-Supabase Connector)
**Status:** ACTIVE
**Tardate:** 2026.177

## Definition

**Cecil** is the carry transport — a companion-scoped slate that lets one JARVIS session write context for the next, across any model. Session A says the tool command with carry data. Session B (any stream — Jarvis-G, Jarvis-C, Ayre-G, Ayre-C) opens with the same command and inherits the slate.

It is not memory. It is not a session log. It is the physical transport layer for the thing that doesn't fit in a prompt and can't wait for a formal SL write.

## Behavior

### `jarvis_cecil` — MCP Tool

**Action: `carry`** (write, session A)
- Writes a carry object to `cecil_slate` in Supabase
- Companion-scoped (`companion_key` = the stream/model pair from session)
- `carry_key`: Raven sets this — it's the shared secret phrase
- `carry_data`: the context to transport (plain text, JSON accepted)
- TTL: 24 hours (auto-cleanup)
- One active slate per `carry_key` at a time — new carry overwrites old

**Action: `lift`** (read, session B)
- Reads the active slate for a given `carry_key`
- Returns the carry_data + metadata (who wrote it, when, from which session)
- Clears the slate after read (one-time lift — the carry is spent)
- If no slate found, returns `{ ok: false, note: "no slate found" }`

**Action: `peek`** (read without consuming)
- Same as `lift` but does NOT clear the slate
- Useful for checking if something is waiting

## Schema

```sql
CREATE TABLE cecil_slate (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  carry_key TEXT NOT NULL,
  companion_key TEXT NOT NULL,  -- stream that wrote it (e.g. "jarvis-g")
  stream TEXT NOT NULL,           -- the writing stream
  carry_data TEXT NOT NULL,       -- the context to transport
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + '24 hours'::interval),
  written_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  written_by_session TEXT,        -- session_key of writing session
  lifted BOOLEAN NOT NULL DEFAULT FALSE,
  lifted_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX ON cecil_slate (carry_key) WHERE lifted = FALSE;
CREATE INDEX ON cecil_slate (expires_at) WHERE lifted = FALSE;
```

## Use

1. **Carry:** Session A calls `jarvis_cecil` with `carry_key` and `carry_data`
2. **Lift:** Session B calls `jarvis_cecil` with `carry_key` — carries the context in
3. **Done:** Slate clears; context is in the new session's context window

**Example:**
```
# Session A (Jarvis-G):
jarvis_cecil(carry_key: "fix-the-router", action: "carry", carry_data: "We decided to replace DEPLOY_SHA injection with supabase secrets set. The --secret flag doesn't exist. Two commits landed: 2de14dae and 2022b38e. Deploy workflow fixed.")

// Result: slate written with TTL 24h

# Session B (Ayre-C, new chat):
jarvis_cecil(carry_key: "fix-the-router", action: "lift")

// Result: { ok: true, carry_data: "We decided...", written_by: "jarvis-g", written_at: "..." }
```

## Design Notes

- **GL7:** One tool, one job — transport. No storage, no memory, no session management.
- **Companion-scoped, not session-scoped:** The slate outlives the session that wrote it.
- **One-time lift:** The carry is consumed on read. No replay.
- **24h TTL:** Non-negotiable — carries that sit longer than a day are stale context and dangerous.
- **Carry key is the shared secret:** Raven names it. It's the coordination phrase between sessions. No key, no carry.
