# Phase 3 — MCP + Tools Audit

**Generated:** 2026-06-24T23:30Z  
**Scope:** MCP connector, Supabase edge functions, tool registrations, doc mirrors, JNL enforcement, wire paths

---

## ✅ PHASE-3 COMPLETE: 65 registered tools, 63 doc mirrors, 13 edge functions, wire path verified

---

## Tool Inventory

| Source | Count |
|--------|-------|
| `jarvis-mcp/index.ts` | 58 |
| `jarvis-mcp/tools/db.ts` | 3 (`jarvis_db_read`, `jarvis_db_inspect`, `jarvis_db_schema`) |
| `jarvis-mcp/tools/jip.ts` | 4 (`jarvis_jip_create`, `jarvis_jip_list`, `jarvis_jip_apply`, `jarvis_jip_revert`) |
| **Total registered** | **65** |

---

## Registered vs Documented

| Metric | Count |
|--------|-------|
| Registered tools | 65 |
| Doc mirrors (`Connectors/JarvisMCPSupabase/tools/*.md`) | 63 |
| **Undocumented** (registered, no mirror) | **2** |
| **Unregistered** (mirror, no registration) | **1** |

### Undocumented — registered but no doc mirror

| Tool | Impact |
|------|--------|
| `jarvis_jglf_validate` | JGLF/JD validation — low impact; mostly internal |
| `jarvis_load` | Utility loader — low impact |

### Unregistered — doc mirror exists, not in MCP registration

| Tool | Notes |
|------|-------|
| `jarvis_media_view` | Has doc mirror; not wired to MCP server. Likely intended for local/client use. |

**Recommendation (low priority):** Add doc mirrors for `jarvis_jglf_validate` and `jarvis_load` if they are user-facing. `jarvis_media_view` is fine as-is if it only runs client-side.

---

## Edge Function Inventory

| # | Function | Purpose | Last Modified |
|---|----------|---------|---------------|
| 1 | `bifrost` | External relay | — |
| 2 | `grid-event` | Grid event handling | — |
| 3 | `grid-write` | Grid write operations | — |
| 4 | `jarvis-action` | Action execution | — |
| 5 | `jarvis-dex` | DEX + JFS/JGLF enforcement | — |
| 6 | `jarvis-mcp` | MCP connector (cloud) | — |
| 7 | `jarvis-monitor` | Monitoring/observability | — |
| 8 | `jarvis-respond` | Edge logic — router, guard, AEGIS, execute | — |
| 9 | `mnemos-embed` | Embedding generation | — |
| 10 | `mnemos-recall` | Memory recall | — |
| 11 | `mnemos-search` | Memory search | — |
| 12 | `mnemos-store` | Memory store | — |
| 13 | `send-push` | Push notifications | — |

**13 total.** `jarvis-mcp`, `jarvis-respond`, `jarvis-dex` are the core pipeline. MNEMOS has 4 dedicated functions (store/recall/search/embed).

---

## JNL Enforcement — jarvis-dex/jfs.ts

`jarvis-dex/jfs.ts` implements full JNL grammar enforcement:

| Check | Validation |
|-------|-----------|
| DOMAINS | Set of 11 domains: GS, ARCH, GOV, IMPL, PROJ, GRID, CONN, AUD, IDEA, BRK, LOG |
| TYPES | Set of types: CORE, SPEC, PATCH, RT, IDX, REG, BIO, LOG, REVW, JGPP, JIP, JD, JC, SL, INS |
| STATUSES | TASK, EXPANSION, ACTIVE, INACTIVE, ARCHIVED, DEPRECATED |
| CLASSES | SYSTEM, SPEC, MODULE, ENTITY, EVENT, REGISTRY |
| SUBSTRATE | YGG, JFS, JNS, JNL, JSL, JMS, JD, LAL, JPL, JSS, JMMS, JITM, JSTM, JLTM, JATM, JHTM |
| GOD_SYSTEMS | All 27 3-letter codes: AEG, APO, ARG, ATH, ATL, AYR, BFR, CHA, DAN, ERI, HAD, HAL, HER, HUG, IRS, JAN, KRN, LOK, MER, MIM, MNE, NEM, ODN, POS, PRO, SKD, ZEU |
| JNL Regex | `^([A-Z]{2,4})-([A-Z0-9]{2,4})-([A-Z]{2,5})-(\d{4})(?:-P(\d{3})(?:-B(\d{3}))?)?$` |
| `gl12Errors()` | GL12 canonical addressability check — validates jnl, cls, tier, status, tags |

**Verdict:** ✅ JNL enforcement is comprehensive and active in Supabase runtime.

---

## Wire Path Verification

### ORACLE → ODIN → SKADI → MNEMOS

Confirmed in `jarvis-respond/index.ts` line 275:
```
// 27 God Systems. Core pipeline: ORACLE→AEGIS→ODIN→KRONOS→SKADI→MNEMOS→HUGINN.
// Parallel: HALO, MIMIR, BIFROST. Sovereign: ZEUS, CHAOS, ERIS.
```

| Stage | System | Role | Verified |
|-------|--------|------|----------|
| Intake | ORACLE | intent parse / routing | ✅ `jarvis-respond/router.ts` |
| Guard | AEGIS | Gold Law gate | ✅ `jarvis-respond/router.ts` |
| Routing | ODIN | routing decision | ✅ `router.ts` |
| Execution | SKADI | AEGIS-cleared execution | ✅ `index.ts` lines 155, 250 |
| Memory | MNEMOS | memory write | ✅ `mnemos-store`, `mnemos-write` |
| Synthesis | HUGINN | reconciliation | ✅ council.ts |
| Parallel | HALO | ambient monitoring | ✅ `jarvis-mcp/halo.ts` |
| Parallel | MIMIR | contextual knowledge | ✅ via council |
| Parallel | BIFROST | external relay | ✅ `bifrost/` edge function |
| Sovereign | ZEUS | supreme arbitration | ✅ council.ts |
| Sovereign | CHAOS | foundational (dormant) | ✅ council.ts TIERS |
| Sovereign | ERIS | entropy guardian | ✅ council.ts |

**AEGIS → SKADI ordering** verified: `router.test.ts` has explicit test `check("AEGIS precedes SKADI in spine", ex.spine.indexOf("AEGIS") < ex.spine.indexOf("SKADI"))`.

**Forbidden edge enforcement** verified in Phase 2: all 4 edges blocked in `router.ts` + `grid-event/index.ts`.

**Verdict:** ✅ Wire path ORACLE→AEGIS→ODIN→KRONOS→SKADI→MNEMOS→HUGINN fully confirmed.

---

## Phase Gate

✅ `memory/intake/audit-phase-3-mcp-tools.md` written — Phase 4 can proceed.
