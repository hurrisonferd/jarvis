---
memory_tier: JLTM
grade: system
---

# JIP-DEX-0001 — Dex Connector & Access Tiers

**JNL:** `IMPL-DEX-SPEC-0001` · **class:** SPEC · **tier:** MAIN · **status:** ACTIVE

Design contract for `jarvis-dex` — a modular Supabase edge function that lets JARVIS (and
agents) read and *govern* the dex without touching the live `jarvis-mcp` connector. Goal:
**perfect governance + hygiene for autonomy, with a human-in-the-loop commit gate.**

## Two representations (and the reconciliation rule)
- **Files (git) = truth.** `JarvisMain/`, `yggdrasil/jd/entries/` — JMS law: truth lives here.
- **Supabase = the live mirror.** `jd_entries`, `jnl_registry` — what the connector reads/writes.

The connector writes to Supabase. A GitHub Action reconciles approved/ACTIVE Supabase rows
back to files (`seed.py` + commit), closing the loop: *propose → approve → Action writes files
→ re-sync*. Canon is only ever **files**; Supabase rows are proposals/mirror until reconciled.

## Privilege ladder (mapped onto JSS status)

| Tier | Token | Tools | Effect |
|------|-------|-------|--------|
| **READ** | none | `jd_lookup` · `jnl_resolve` · `jd_list` · `jd_graph` · `jd_diff` | resolve, list, graph, and **preview** a write (no mutation). Only access for `ARCHIVED`/`DEPRECATED`. |
| **PROPOSE** | agent | `jd_propose` | auto-format + validate → `jd_proposals` (status `TASK`). Canon untouched. |
| **DRAFT** | elevated | `jd_draft` | write into `jd_entries` directly as `TASK`/`EXPANSION` (visible, non-ACTIVE). |
| **COMMIT** | Raven (AEGIS) | `jd_approve` · `jd_reject` · `jd_archive` · `jd_deprecate` | move objects along the lifecycle; `approve` → `ACTIVE` + triggers file reconciliation. |
| **OVERRIDE** | Raven (skeleton key / ZEUS) | all of the above · `dex_halt` · `dex_resume` · `dex_status` | break-glass for when governance is stuck. Outranks COMMIT; bypasses the halt. |

## OVERRIDE — the skeleton key (ZEUS)

A single break-glass key, **Raven-only**, for emergencies. It maps to **ZEUS** (emergency
override + system-wide halt). Read by the connector from the `RAVEN_SKELETON_KEY` secret —
**the value never lives in the repo**. The OVERRIDE tier:
- outranks every other tier (can invoke any tool, even if the normal RAVEN_TOKEN is lost);
- can **`dex_halt`** — freeze all writes (PROPOSE/DRAFT/COMMIT) instantly; only READ and
  OVERRIDE work while halted. **`dex_resume`** lifts it. State lives in `dex_control`.
- every override action is logged to `dex_events` (GL5).

Use it only when the normal loop is compromised. It is the system's last word, and it is Raven's.

## Auto-formatting (what the connector derives)
A proposer supplies only **meaning**: `{name, domain, type, definition, purpose, tags}`.
The connector derives the rest — the JFS hygiene, automatically:
- **JNL** — next sequence for `domain-system-type` (parsed + grammar-validated).
- **class** — `ontology_class()`; **tier** — `MAIN`/`SIDE`; **owner**; **timestamps**.
- **status** — defaults to `TASK` (propose) or as specified (draft).
- **location** — derived from tier + status (auto-sort target).

## Governance mapping
- **GL2** — JARVIS proposes, Raven commits. Proposals never auto-enter canon (files).
- **GL6** — AEGIS validates JNL grammar + GL12 before anything is staged.
- **GL5** — every propose/draft/approve emits a BUS event + PROMETHEUS decision log.
- **GL12** — a staged object without a valid JNL/tags/class/tier is rejected at the gate.
- **JSS** — status is the lifecycle; the access tier governs who may transition it.

## Read tools (detail)
- `jd_lookup(term)` — name / JNL / tag → entry (semantic DNS).
- `jnl_resolve(jnl)` — JNL → location + class/tier/status/owner.
- `jd_list({domain?,class?,tier?,status?,tag?})` — index-backed filter.
- `jd_graph(jnl?, depth?)` — neighborhood from the YVG graph.
- `jd_diff(candidate)` — compute the would-be JNL/class/tier and diff against canon. **No write.**

## Build order
1. `jd_proposals` staging table (migration) + RLS.
2. `jarvis-dex` edge function — READ tools first (safe), then PROPOSE/DRAFT, then COMMIT.
3. AEGIS token tiers (read/agent/elevated/raven).
4. Reconciliation GitHub Action (approved Supabase rows → files → `seed.py` → commit).
5. CI: validator stays the gate; reconciliation re-runs `validate.py` before commit.
