---
memory_tier: JLTM
grade: system
---

# JMMS — Jarvis MultiMemory System

**JNL:** `ARCH-JMMS-CORE-0001`
**Authority:** Canonical
**Type:** Architecture / JFS family

JMMS defines **how memory is tiered and addressed** across time horizons. It is the
filesystem/addressing layer over memory — it says *where memory lives and how long it
lasts*. It sits **beside MNEMOS**, the cognitive memory God System: MNEMOS is the *meaning*
layer (what a memory means); JMMS is the *structure* layer (which tier holds it).

> Separation, like the rest of JFS: MNEMOS thinks about memory; JMMS files it.

## The five tiers (2026-06-24: JHTM added between JSTM and JLTM)

| Tier | JNL | Horizon | Holds | Backing store |
|------|-----|---------|-------|---------------|
| **JITM** — immediate | `ARCH-JITM-CORE-0001` | always-on / pinned | the strict capped briefing injected every turn (a dynamic extension of the charter) — **pointers, not content** | `mnemos_memories` tagged `jitm`; injected by `jarvis_query` |
| **JSTM** — short-term | `ARCH-JSTM-CORE-0001` | working / session | current context, recent events, the live exchange | session logs, `events`, working buffers |
| **JHTM** — historical | `ARCH-JHTM-CORE-0001` | compressed summary | JSTM compressed into narrative summaries; fold receipts accompany every entry; 14-day cadence | `mnemos_memories` tagged `jhtm` |
| **JLTM** — long-term | `ARCH-JLTM-CORE-0001` | consolidated | compressed knowledge, durable facts, learned patterns; JHTM fold receipts land here | `memory/mnemos/memories/`, Supabase `mnemos_memories` |
| **JATM** — ancestral | `ARCH-JATM-CORE-0001` | immutable lineage | the dated record — foundational decisions, the spine | `event_spine`, git history, PROMETHEUS ledger |

> **JHTM vs JATM:** JHTM is actively used for the 14-day fold — compressed summaries that remain
> accessible and queryable. JATM is the settled ancestral record — immutable, never rewritten.

## Promotion chain

```
JITM (always-on briefing, pointers only)
  ↓ (content captured)
JSTM (working / session — high churn, summarized, not kept whole)
  ↓ (14-day fold + receipt)
JHTM (compressed summary — narrative form, queryable)
  ↓ (fold receipt + further compression)
JLTM (consolidated / durable — MNEMOS meaning work happens here)
  ↓ (settled lineage)
JATM (ancestral / immutable — never retagged out)
```

- **JSTM → JHTM:** MNEMOS folds JSTM sessions into narrative summaries; a fold receipt
  accompanies every JHTM entry.
- **JHTM → JLTM:** JLTM is the durable recall target; JHTM summaries land here with receipts.
- **JLTM → JATM:** settled into the immutable spine.
- **Promotion is one-way for JATM:** JATM is append-only, never edited or demoted.

## Rules

- **No tier duplicates another's truth** (JMS law): JLTM points at JATM lineage; JSTM
  points at JLTM. Each tier holds references, not copies, of the tier beneath it.
- **Every memory object is JNL-addressed** and carries a tier tag, so recall can target a
  horizon (`#jitm` / `#jstm` / `#jhtm` / `#jltm` / `#jatm`).
- **JITM is capped at injection, not storage.** `jarvis_query` injects only the newest 5 `jitm`
  rows every turn — extra pins stop loading so the briefing never bloats (autosort-by-recency,
  bounded). JITM holds *pointers* only; content lives in JSTM or above.
- **JHTM receipts:** every JHTM entry must carry a fold receipt (source session references,
  compression method, timestamp). Without a receipt, JHTM entries are rejected.

## Relationship to the stack

```
JMMS (memory addressing)        MNEMOS (memory meaning, God System)
   ├── JITM  always-on              ↕  uses JMMS tiers to store/recall
   ├── JSTM  working
   ├── JHTM  historical (14-day fold)
   ├── JLTM  consolidated       ◀── settles into ── HADES (immutable event spine)
   └── JATM  ancestral
```

JMMS is the JFS family member that makes memory *navigable across time* the same way JNL
makes the repository navigable across space.
