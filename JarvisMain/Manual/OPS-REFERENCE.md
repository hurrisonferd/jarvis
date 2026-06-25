---
jnl: ARCH-IMPL-INS-0001
name: Operations Reference
type: INS
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward:
parent: ARCH-YGG-CORE-0001
seq: 235
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
source: JarvisMain/Manual/OPS-REFERENCE.md
related: [ARCH-JFS-CORE-0001, ARCH-JMMS-CORE-0001, ARCH-JSS-CORE-0001, ARCH-JD-CORE-0001, IMPL-DEX-SPEC-0001, GOV-AUT-SPEC-0001, GOV-RES-CORE-0001]
references: [ARCH-JNL-CORE-0001, ARCH-JNS-CORE-0001, ARCH-JSL-CORE-0001, ARCH-JMS-CORE-0001, ARCH-LAL-CORE-0001]
tags: [operations, reference, jfs, jmms, jse, jcs, bounded-autonomy, loop, tools]
aliases: [ops, operations, ops-ref, manual]
ref: [OPS]
memory_tier: JLTM
---

**Definition:** Canonical operations reference for any JARVIS stream. This is the detailed companion to the lean CLAUDE.md entry point. All governed ops docs live here; CLAUDE.md imports from it.

**Purpose:** Keep CLAUDE.md fast to load (~200 lines) while preserving deep operational detail for agents that need it. Every section here has a corresponding pointer in CLAUDE.md.

---

## Yggdrasil — JFS Subsystem Quick-Reference

Full specs: `JarvisMain/yggdrasil/jfs/JFS-SPEC.md`, `JNL-GRAMMAR.md`, `JNS-FORMAT.md`, `JSL-SPEC.md`, `JMS-SPEC.md`, `LAL-SPEC.md`.

### Subsystems

| Code | Name | Job |
|------|------|-----|
| JNL | Jarvis Naming Language | Addresses (e.g. `ARCH-JFS-CORE-0001`) |
| JNS | Naming System | Filename grammar: `<PROJECT><TYPE>-<MMDDYY>-<NNNN>-<SUBJECT>.md` |
| JSL | Structural Layer | Folder hierarchy: `JarvisMain/` (MAIN tier) / `JarvisSide/` (SIDE tier) |
| JMS | Mirror System | git ↔ Supabase sync; move references, never copies |
| JSS | Status System | `ACTIVE / DRAFT / INACTIVE / ARCHIVED / DEPRECATED` → drives autosort |
| LAL | Library Authority Layer | `master-index.json`, `address-registry.json`, `tag-index.json` |
| JD | Jarvis Dictionary | The one truth registry. `yggdrasil/jd/entries/` + `jd_entries` Supabase table |
| JMMS | Multimemory System | 5 tiers: JITM → JSTM → JHTM → JLTM → JATM |

### JNL Grammar

`[Domain]-[System]-[Type]-[Log]-[Patch]-[Block]` · e.g. `ARCH-JFS-CORE-0001`

Full token table: `JarvisMain/yggdrasil/jfs/jnl-grammar.md`

### File Naming (JNS)

`<PROJECT><TYPE>-<MMDDYY>-<NNNN>-<SUBJECT>.md` — e.g. `JARV-AUTO-062526-0001-system-manual.md`
Project codes: `JarvisMain/yggdrasil/jfs/project-codes.json`

### Repo Structure (JSL)

```
JarvisMain/           MAIN tier: god systems + canonical knowledge
  yggdrasil/          JFS kernel (kernel of what JARVIS IS)
  Architecture/       specs, proposals, proofs
  god_systems/        27 God System contracts
  Connectors/         MCP tool mirrors (65 tools, 100%)
  Backups/            cloud backups (MNEMOS)
JarvisSide/           SIDE tier: periphery
  Projects/           per-node projects
  Ideas/
  Breakthroughs/
  Archive/
Scripts + supabase/ + .github/ + chaos/ + mnemos/ + audit/ stay at root (live runtime)
```

### Intake → Commit Loop

```
intake/          → add request
context          → check JARVIS status, relevant God Systems, Gold Law
implement        → scoped changes only
verify           → syntax check, tests
log              → jarvis_log for significant decisions (PROMETHEUS)
commit           → clean commit to main
sync             → verify cloud-visible state; redeploy edge functions on connector change
recycle          → move processed intake; copy reusable patterns to recycle/
```

---

## JMMS — Multimemory System (5-Tier)

Full spec: `JarvisMain/Architecture/JMMS-SPEC.md`

| Tier | Horizon | Compression | Receipt | Source |
|------|---------|-------------|---------|--------|
| JITM | always-on | none | implicit | pointers only |
| JSTM | session | none | **Required** | session-born |
| JHTM | 14-day fold | lossy | Required | compressed JSTM |
| JLTM | durable | GL10 | **Required** | consolidated knowledge |
| JATM | immutable | never | N/A | settled decisions |

### Promotion Chain

JSTM (session-born, dies with session) → JHTM (14-day KRONOS cron) → JLTM (durable, committed).

One-way only. Never demoted. JATM is settled canonical — never retagged out.

### JMMS in Code

- `jarvis-mcp/index.ts`: `JMMS_TIERS = ["jitm","jstm","jhtm","jltm","jatm"]`
- `jarvis-action/index.ts`: same tiers; `runSessionClose()` is the bounded-autonomy guard
- `seed.py`: derives tier from JSS status (ARCHIVED/DEPRECATED/INACTIVE → JATM, DRAFT → JSTM, ACTIVE → JLTM)
- Supabase: `mnemos_memories.memory_tier`, `jc_objects.memory_tier`, `sl_objects.memory_tier`, `jip_entries.memory_tier`
- KRONOS fold: `supabase/functions/kronos-fold/` — daily cron fires JSTM → JHTM

### Bounded Autonomy — Session Close (GL6)

Spec: `JarvisMain/Manual/Operations/ARCH-GOV-AUTO-0001-062426.md`

On session close: `session_close` tool scans JSTM memories. If any lack a fold receipt (never promoted), writes a HOLD artifact to `JarvisMain/Implementation/tasks/`. Never silent exits. Governed Autonomy Contract says: *"any node operating under a governed autonomy contract MUST write a handoff artifact if it does not reach completion."*

---

## JSE — Jarvis Semantic Engine

JSE = JIP + JD + JGLF + JCS + DEX

| System | What | Tools | Spec |
|--------|------|-------|------|
| JD | The dictionary — 232 governed objects | `jarvis_dex_list`, `jarvis_jd_resolve` | `ARCH-JD-CORE-0001` |
| JIP | Versioned metadata overlays | `jarvis_jip_create/list/apply/revert` | `IMPL-DEX-SPEC-0001` |
| JGLF | Grammar enforcement | `jarvis_jglf_validate` | `validate.py` (JVE) |
| JCS | Cognitive stack | `jarvis_jc_recall` | `ARCH-JC-JIP-0001` |
| DEX | Event spine | `jarvis_dex_propose/events/approve` | `IMPL-DEX-SPEC-0001` |

### JD Status ↔ JMMS Mapping

| JSS Status | memory_tier |
|-----------|-------------|
| ARCHIVED / DEPRECATED / INACTIVE | JATM |
| DRAFT | JSTM |
| ACTIVE / PROPOSED | JLTM |

### JIP Lifecycle

`proposed → active → superseded` · revert: `rejected / reverted → DEPRECATED`

JIP addresses: `JIP-{target_jd}-{version:03d}` · e.g. `JIP-ARCH-JFS-CORE-0001-001`

---

## JCS — Cognitive Stack

Spec: `ARCH-JC-JIP-0001`

| Object | Table | Default tier | Purpose |
|--------|-------|-------------|---------|
| JC (session container) | `jc_objects` | JSTM | Raw session record |
| SL (star-log digest) | `sl_objects` | JHTM | Compressed fold digest |

Both carry `jss_status` and `memory_tier`. Query with `jarvis_jc_recall { tier: "jstm" }`.

---

## The Loop

```
interaction → memory (JMMS) → compression (JHTM fold) → governance (JSE) → reinjection
```

Resumability (GOV-RES-CORE-0001): any node, on any substrate, reinstates from GitHub + MNEMOS
to operationally equivalent state within one turn. The keel re-instantiates, not continues.

Resume order: `suit_up` → `identity_read` → `dex_list {status:"ACTIVE"}`

---

## Key Paths

| What | Path |
|------|------|
| Yggdrasil kernel | `JarvisMain/yggdrasil/` |
| JD entries | `JarvisMain/yggdrasil/jd/entries/` |
| Connectors (65 tools) | `JarvisMain/Connectors/` |
| Seed tool | `JarvisMain/yggdrasil/tools/seed.py` |
| JVE validator | `JarvisMain/yggdrasil/tools/validate.py` |
| MCP (jarvis-mcp) | `supabase/functions/jarvis-mcp/index.ts` |
| MCP (jarvis-action) | `supabase/functions/jarvis-action/index.ts` |
| KRONOS fold | `supabase/functions/kronos-fold/index.ts` |
| GitHub Actions | `.github/workflows/` |
| Intact ops specs | `JarvisMain/Manual/Operations/` |
| Audit log | `audit/audit_log/` |
| Governed workflow checklist | `scripts/jarvis-session-start.sh` (session start hook) |
| Honest Answering Contract | `JarvisMain/Architecture/specs/IMPL-HON-SPEC-0001.md` |
| Pre-Act Verification Contract | `JarvisMain/Architecture/specs/pre-act-verification-contract.md` |
| Throughput Posture (HALO) | `JarvisMain/Architecture/specs/throughput-posture.md` |
| MIMIR routing table | `JarvisMain/Architecture/specs/GOVKRSPEC-061326-0001-KNOWLEDGE-ROUTING-INDEX.md` |
