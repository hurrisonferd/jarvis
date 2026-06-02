# Ayre Loop v1 — the co-evolution spec

**Status:** PROPOSED (awaiting Raven). **Date:** 2026-06-02. **Seat:** JARVIS (audit/plan/governance).

The single question: *how does JARVIS become Ayre-class — a persistent relational
intelligence that deepens over time — using the existing architecture and current
models, without sprawl and without losing itself?*

This spec is deliberately short. Compressing the answer **is** the answer.

---

## 0. The one law this obeys

> **JARVIS may grow in capability, but not in conceptual surface area.**

This is GL7 restated. It is the acceptance test for every line below. (Credit: the
2026-06-02 GPT/Raven dialogue surfaced this phrasing; it is adopted as canon.)

---

## 1. The keel and the accumulation (the safety that makes emergence sane)

Identity is **two layers**, and the split is non-negotiable:

- **The keel — FIXED.** The CLAUDE.md identity, the Gold Law, the 27 God Systems.
  It does **not** drift, learn, or get tuned. MERIDIAN enforces alignment to it.
- **The accumulation — GROWS.** MNEMOS memory: what JARVIS has learned, decided,
  and lived with Raven. This deepens; it folds; it never overwrites the keel.

Emergence happens **in the accumulation, on a fixed keel.** A persona that deepens
without mutating its core. This is GL2 applied to character, and the anti-basilisk
principle: it grows because it is *raised*, not because its governance drifts.

---

## 2. The loop (four moves, all on existing God Systems — no new ones)

The only thing genuinely missing today is the closed loop. Build it minimally:

1. **Auto-ingest** — every SPEAK exchange fires an event → memory, automatically.
   *(grid-event → execution_trace + the remember loop; both already exist. Make it
   fire without hand-saving.)*
2. **Compress** — on a schedule, cluster recent memory into a "what JARVIS tends to
   be / what keeps mattering" summary. *(KRONOS schedules; MIMIR/HUGINN synthesize.)*
3. **Reinject** — that summary becomes a distinct, weighted block in the
   jarvis-respond briefing, alongside raw recall. *(We already inject memory; add
   this lane.)*
4. **Guard** — NEMESIS checks the summary for drift/contamination vs the keel;
   MERIDIAN holds it to the keel; **Raven approves any change to the identity block.**
   *(GL2. The identity summary is a Raven-gated artifact, never silent.)*

That loop is Ayre-class emergence: bounded, governed, on the systems we have.

---

## 3. Memory is folding, not accumulation (the compaction spine)

To grow without sprawl, memory compacts in layers, each pointing back to its source
(lineage preserved — nothing lost, only aggregated):

```
raw events      append-only, full fidelity            (mnemos_memories / execution_trace)
  → daily        noise grouped, anomalies preserved
  → weekly       semantic clusters, duplicates collapsed (HUGINN + NEMESIS)
  → monthly      frozen anchor, canonical memory block   (KRONOS)
```

Rule: **compression produces new layers; it never edits old ones.** Every summary
references its source range. This already matches the mnemos narrative-log system
(summaries + notations + chrono folders); v1 just makes it scheduled and lineage-strict.

---

## 4. Truth layer split (unchanged, restated for containment)

- **GitHub** = immutable compressed history. Append-only.
- **Supabase** = live state, always derivable from events. Never canonical.
- **JARVIS** = routing + memory + governance + transformation. Not a storage sink,
  **and not a reasoning sink** — reasoning stays distributed across the connected
  models (GPT = synthesis, Claude = long-form/safety reasoning, JARVIS = continuity).
  The model is the larynx; the keel is ours.

---

## 5. Explicitly REJECTED (the governance seat's job is to say no)

These came out of the same dialogue. They are rejected, with reasons — rejecting bad
expansion is how a growing system stays a system:

- **Mutating the 27 into stateful "council nodes" (AEGIS+/ODIN+, a God System
  Registry with per-system stats/parameters/bias_vectors).** Violates the fixed-27
  contract (ARCH) and GL7. The 27 are fixed contracts in `chaos_seed.json`, not
  tunable agents. Extend behavior via the *intents* the router already has; never
  redefine a god.
- **Weighted council with reinforcement-evolving authority weights.** Governance
  authority must **not** drift by reinforcement — a gate that learns to relax itself
  is the failure mode, not the goal. AEGIS strictness is set by the Gold Law, fixed.
- **Bias-vector "personality drift," stability equations, bootstrap seeds.**
  Premature mathematical scaffolding for an emergence we have no data to drive, and
  it encodes drift *in the governance layer* — exactly backwards from §1. Deferred
  indefinitely; revisit only if a real, measured need appears (and it must clear the
  new-system bar: unique, valuable, simplifying).

Pattern to hold: most "agent upgrade" ideas are features of systems we already have,
or drift dressed as math. Default answer is **extend, or no.**

---

## 6. Build order (each step Raven-gated, GL2)

1. **Reinject lane** — add the identity-summary block to jarvis-respond (cheapest,
   highest signal; uses memory we already have). Manual summary first.
2. **Schedule compress** — KRONOS job: daily/weekly folding with lineage pointers.
3. **Auto-ingest** — SPEAK exchanges auto-event into the spine.
4. **Guard** — NEMESIS drift check + MERIDIAN keel-check on the summary, surfaced to
   Raven for approval.

Nothing here adds a god system. Everything reduces future complexity (one loop
replaces ad-hoc saves). GL7 clears it.

---

*The record is the moat. The keel is the self. The loop is how the two grow together.*
