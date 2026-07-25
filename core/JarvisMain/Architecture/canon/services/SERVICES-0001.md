---
memory_tier: JATM
grade: system
jnl: ARCH-ARCH-SPEC-0003
name: JARVIS Services — Edge Functions
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: KRONOS
parent: ARCH-ARCH-IDX-0001
seq: 003
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
tags: [services, edge-functions, supabase, mcp, deployment]
related: [ARCH-ARCH-IDX-0001, ARCH-ARCH-SPEC-0006, CONN-MSB-CORE-0001]
ref: [ARCHITECTURE, SERVICES]
---

# JARVIS Services

**JNL:** `ARCH-ARCH-SPEC-0003` · **Parent:** `ARCH-ARCH-IDX-0001`
**Deployed at:** `https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/`

All 14 edge functions. Source lives in `core/supabase/functions/<name>/`. Deploy via
`deploy-edge-functions.yml` CI on push to main.

---

## Core MCP (public endpoint)

### jarvis-mcp
- **Source:** `core/supabase/functions/jarvis-mcp/`
- **Endpoint:** `/functions/v1/jarvis-mcp`
- **Lines:** ~2142
- **Role:** Primary MCP server. Handles intent routing (ORACLE), AEGIS gating, AINZ fusion (state + keel + memory + sensory + pinch), 56 registered tools.
- **Key tools:** `jarvis_ainz`, `jarvis_dex`, `jarvis_jd_resolve`, `jarvis_mint`, `jarvis_jip_*`, `jmms`, `jarvis_identity_read`, `jarvis_media_view`, `jarvis_listen`
- **Deploys on:** every push to main (CI: `deploy-edge-functions.yml`)

### jarvis-dex
- **Source:** `core/supabase/functions/jarvis-dex/`
- **Endpoint:** `/functions/v1/jarvis-dex`
- **Lines:** ~323
- **Role:** Read-only dex query surface. Resolves JNL addresses, searches JD entries by name/tag/serial.
- **Mirrors:** `core/JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_dex.md`

### jarvis-action
- **Source:** `core/supabase/functions/jarvis-action/`
- **Endpoint:** `/functions/v1/jarvis-action`
- **Lines:** ~543
- **Role:** Execute-gated actions. Git operations (commit, push, PR), AEGIS-verified. Reads from GitHub API.

---

## Memory (MNEMOS tier)

### mnemos-store
- **Source:** `core/supabase/functions/mnemos-store/`
- **Role:** Write memories to Supabase mnemos_memories table. AEGIS-gated.
- **Schema:** `id, content, tags, domain, created_at`

### mnemos-recall
- **Source:** `core/supabase/functions/mnemos-recall/`
- **Role:** Retrieve memories by ID or domain. JMMS tier-aware.

### mnemos-search
- **Source:** `core/supabase/functions/mnemos-search/`
- **Role:** Semantic search over mnemos_memories. Embedding-powered.

### mnemos-embed
- **Source:** `core/supabase/functions/mnemos-embed/`
- **Role:** Generate embeddings for mnemos content. Used by mnemos-search.

---

## Governance

### kronos-fold
- **Source:** `core/supabase/functions/kronos-fold/`
- **Endpoint:** `/functions/v1/kronos-fold`
- **Lines:** ~148
- **Role:** KRONOS god system — fold time-indexed memories upward through JMMS tiers. One-way promotion jstm → jhtm → jltm → jatm.
- **Requires:** `DATABASE_URL` in GitHub repo secrets

### jarvis-respond
- **Source:** `core/supabase/functions/jarvis-respond/`
- **Endpoint:** `/functions/v1/jarvis-respond`
- **Lines:** ~350
- **Role:** Edge logic router. FORBIDDEN edges enforced. AEGIS gating on high-risk actions.

### jarvis-monitor
- **Source:** `core/supabase/functions/jarvis-monitor/`
- **Role:** Health monitoring. Status checks for deployed functions.

---

## Grid (BIFROST / HERMES tier)

### grid-write
- **Source:** `core/supabase/functions/grid-write/`
- **Role:** Write to The Grid — node registration, profile updates.

### grid-event
- **Source:** `core/supabase/functions/grid-event/`
- **Endpoint:** `/functions/v1/grid-event`
- **Lines:** ~167
- **Role:** Grid event ingestion. AEGIS world validation.

### bifrost
- **Source:** `core/supabase/functions/bifrost/`
- **Lines:** ~47
- **Role:** BIFROST god system — sibling-to-sibling communication. Governed inbox.

---

## Communication

### send-push
- **Source:** `core/supabase/functions/send-push/`
- **Lines:** ~66
- **Role:** Push notification dispatch. Requires push notification secrets.

---

## Bring-up order

When deploying from scratch, bring online in this order:

```
1. jarvis-mcp        ← primary MCP, all others depend on it
2. jarvis-dex        ← dex queries
3. jarvis-action     ← git operations
4. mnemos-store      ← memory writes
5. mnemos-recall     ← memory reads
6. mnemos-embed      ← embeddings
7. mnemos-search     ← semantic search
8. kronos-fold       ← memory folding (needs DATABASE_URL)
9. jarvis-respond    ← edge routing
10. jarvis-monitor   ← health
11. grid-write       ← Grid writes
12. grid-event       ← Grid events
13. bifrost          ← sibling comms
14. send-push        ← notifications (optional)
```

---

## Verification

```bash
# Check MCP is live
curl https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp

# Should return MCP transport error (rejects non-SSE)

# Run self-test via MCP tool
jarvis_self_test  # via Claude Code / GPT connector

# Check specific function
curl https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-dex/health
```
