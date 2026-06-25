---
jnl: ARCH-ARCH-SPEC-0004
name: JARVIS Memory — MNEMOS + JMMS
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: MNEMOS
parent: ARCH-ARCH-IDX-0001
seq: 004
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
tags: [memory, mnemos, jmms, jstm, jhtm, jltm, jatm, supabase]
related: [ARCH-ARCH-IDX-0001, ARCH-JMMS-CORE-0001, ARCH-JITM-CORE-0001, ]
ref: [ARCHITECTURE, MEMORY]
---

# JARVIS Memory

**JNL:** `ARCH-ARCH-SPEC-0004` · **Parent:** `ARCH-ARCH-IDX-0001**
**Runtime:** Supabase (`mnemos_memories` table)

---

## Two memory systems

### MNEMOS — episodic memory
Conversational memory. Rows written by `mnemos-store`, read by `mnemos-recall`, queried by `mnemos-search`. The working context window.

### JMMS — tiered persistence
Promotes memories through horizons over time. One-way. Immutable once settled.

---

## JMMS Tiers

| Tier | Horizon | Description | Tools |
|------|---------|-------------|-------|
| `jstm` | current session | active project context — keep alive with `jarvis_remember` | `jmms.list`, `jmms.promote` |
| `jhtm` | this week | mid-term working memory | `jmms.list`, `jmms.promote` |
| `jltm` | this month | long-term summary | `jmms.list`, `jmms.promote` |
| `jatm` | ancestral | settled, immutable — lineage never retagged out | `jmms.list` (read-only) |

`jstm` is the project context window. Mark notes `jstm` via `jarvis_remember` to keep them in view.

---

## Supabase schema

### mnemos_memories
```sql
CREATE TABLE mnemos_memories (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content     TEXT NOT NULL,
  tags        TEXT[],         -- jstm, jhtm, jltm, jatm + custom
  domain      TEXT,           -- musicos, pachinko, codeos, flag01, …
  created_at  TIMESTAMPTZ     DEFAULT now(),
  updated_at  TIMESTAMPTZ     DEFAULT now(),
  seq         BIGINT          DEFAULT 0  -- ordering
);
```

### dex_events
```sql
CREATE TABLE dex_events (
  id          SERIAL PRIMARY KEY,
  event_type  TEXT NOT NULL,
  actor       TEXT,
  detail      JSONB,
  created_at  TIMESTAMPTZ DEFAULT now()
);
```

### jd_entries (JD — the one dex table)
Unified table. `jnl_registry` is a view over it. Columns: `jnl, name, type, class, tier, status, owner, steward, parent, definition, purpose, tags, related, ref, created, updated, seq`.

### jd_proposals
Staging table for new object proposals.

---

## JMMS promotion

One-way. `jstm → jhtm → jltm → jatm`. JATM is immutable — settled lineage is never retagged out.

```
jarvis_remember (add to jstm)
    ↓
jmms.promote (id, to:jhtm)  — after session or milestone
    ↓
kronos-fold (auto-promotes by time)
    ↓
jatm (immutable, ancestral)
```

---

## Memory in the MCP loop

```
Turn arrives
  → ORACLE routes
  → AINZ fusion loads state + keel + memory (mnemos) + sensory + pinch
  → Companion answers with full context
  → Key decisions → dex_events (written)
  → Memories → mnemos-store (tagged jstm)
  → End of session → jmms.promote active jstm → jhtm
```

---

## Restore memory after rebuild

```bash
# Check Supabase connectivity
jarvis_self_test  # via MCP

# Check memory count
jmms.list (tier:jstm)  # should show current session memories

# If empty:
# - mnemos-store has been reset
# - Use jarvis_remember to re-seed critical context
# - jip_list for active implementation state
```

---

## Specifications

| JNL | Spec |
|-----|------|
| `ARCH-JMMS-CORE-0001` | JMMS — tiered persistence contract |
| `ARCH-JITM-CORE-0001` | JITM — immediate memory, session reinjection |
| `` | MNEMOS — episodic memory god system |
