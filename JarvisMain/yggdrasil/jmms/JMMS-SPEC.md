# JMMS — Jarvis MultiMemory System

**JNL:** `ARCH-JMMS-CORE-0001`
**Authority:** Canonical
**Type:** Architecture / JFS family

JMMS defines **how memory is tiered and addressed** across time horizons. It is the
filesystem/addressing layer over memory — it says *where memory lives and how long it
lasts*. It sits **beside MNEMOS**, the cognitive memory God System: MNEMOS is the *meaning*
layer (what a memory means); JMMS is the *structure* layer (which tier holds it).

> Separation, like the rest of JFS: MNEMOS thinks about memory; JMMS files it.

## The three tiers

| Tier | JNL | Horizon | Holds | Backing store |
|------|-----|---------|-------|---------------|
| **JITM** — immediate | `ARCH-JITM-CORE-0001` | always-on / pinned | the strict capped briefing injected every turn (a dynamic extension of the charter) — **pointers, not content** | `mnemos_memories` tagged `jitm`; injected by `jarvis_query` |
| **JSTM** — short-term | `ARCH-JSTM-CORE-0001` | working / session | current context, recent events, the live exchange | session logs, `events`, working buffers |
| **JLTM** — long-term | `ARCH-JLTM-CORE-0001` | consolidated | compressed knowledge, durable facts, learned patterns | `mnemos/memories/`, Supabase `mnemos_memories` |
| **JATM** — ancestral | `ARCH-JATM-CORE-0001` | immutable lineage | the dated record — foundational decisions, the spine | `event_spine`, git history, PROMETHEUS ledger |

## Flow (strengthens the loop, GL10)

```
interaction → JSTM (capture) → compression → JLTM (consolidate) → JATM (settle into lineage)
                  ▲                                                      │
                  └──────────────── reinjection (recall) ◀──────────────┘
```

- **JSTM** is high-churn and volatile — the working set. It is *summarized*, not kept whole.
- **JLTM** is the consolidation target — what compression promotes out of JSTM. Durable,
  semantic, recallable. This is where MNEMOS does its meaning work.
- **JATM** is append-only and **never rewritten**. It is the ancestral record: every commit,
  every governed decision, the immutable spine (HADES-adjacent). Truth that outlives sessions.

## Rules

- **Promotion is one-way for JATM:** memory may move JSTM → JLTM → JATM, but JATM is
  immutable — you append, you never edit. (Mirrors HADES / git history.)
- **No tier duplicates another's truth** (JMS law): JLTM points at JATM lineage; JSTM points
  at JLTM. Each tier holds references, not copies, of the tier beneath it.
- **Every memory object is JNL-addressed** and carries a tier tag, so recall can target a
  horizon (`#jitm` / `#jstm` / `#jltm` / `#jatm`).
- **JITM is capped at injection, not storage.** `jarvis_query` injects only the newest 5 `jitm`
  rows every turn — extra pins simply stop loading, so the always-on briefing can never bloat
  (autosort-by-recency, bounded). JITM holds *pointers* (where the manual/brief/fusions live,
  the current focus), never content; content lives in JSTM (working) or JLTM (durable).

## Relationship to the stack

```
JMMS (memory addressing)        MNEMOS (memory meaning, God System)
   ├── JSTM  working               ↕  uses JMMS tiers to store/recall
   ├── JLTM  consolidated
   └── JATM  ancestral  ◀── settles into ── HADES (immutable event spine)
```

JMMS is the JFS family member that makes memory *navigable across time* the same way JNL
makes the repository navigable across space.
