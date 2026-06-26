---
memory_tier: JLTM
grade: system
---

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

## 4b. The dual gate + the honesty layer (the truth-shaping spine)

JARVIS is a bidirectional evaluator, not a one-way pipe:

- **Input gate (pre-model).** Intake is validated/shaped before reasoning. This is
  already the pipeline head: `AYRE → AEGIS`. Intent parsed, structure gated, early.
- **Output gate (post-model).** The model's draft is checked **before it's accepted**
  — against MNEMOS for contradiction, against the keel for alignment. Catches
  "convincing but wrong." This is the genuinely new piece.

**The honesty layer (the heart, fixed law — not a tunable weight).** Every
substantive answer must surface what is **uncertain, inferred, missing, or assumed.**
The model never formats to please. This is JARVIS's voice law made into an enforced
contract; it is part of the keel and does **not** drift.

Two ways to enforce the output gate, in order:
- **Step 0 (now, free):** bake the honesty contract into the jarvis-respond briefing,
  so the connector speaks it by construction.
- **Later (a real step):** a `jarvis_verify` tool the connector calls with its draft;
  JARVIS checks it against memory + the keel and returns pass / flagged-with-reasons.

**Disagreement protocol:** when the output gate finds a contradiction with the record,
JARVIS **flags it and asks Raven** (GL2, human-in-the-loop). The fixed-authority
council (§4c) resolves ordinary routing by weight tally; genuine conflicts of validity
escalate to Raven. No *self-tuning* voting math (rejected in §5).

## 4c. The Council — JARVIS + the 27 (fixed authority, growing profile)

The council is JARVIS and all 27 God Systems, each a member with a distinct role.
The key insight (Raven, 2026-06-02): **each member is itself a mini-JARVIS — a fixed
keel + a growing accumulation.** The same law (§1), applied fractally to all 27.

- **Keel (fixed — canon in `chaos_seed.json`):** role, tier, authority weight,
  function, forbidden actions. Authority does **not** drift. AEGIS is the constraint
  authority by *being* AEGIS, not by earning it.
- **Accumulation (grows — like JARVIS):** the member's **profile** — its activation
  history, the decisions it informed, the patterns in its domain, its accumulated
  judgment. It deepens as it is used. Memory on a fixed keel, per system.

Each member can:
- **Vote** — on decisions in its domain, with its fixed weight: `{system, verdict, score, reason}`.
- **Speak** — surface its perspective/reasoning (a voice in the trace).
- **Update** — its profile/accumulation. **Never its authority** (that's the keel).

A decision — route an input, filter or store an LLM's output, place/recycle data —
runs as a council vote, resolved by **fixed-weight** tally, into a **council trace**
that is stored and auditable: who voted, what they said, what won, why. Raven reads
the trace to see exactly why data was stored, recycled, filtered, or routed.

Domain roles (examples): AEGIS gate/permit · ODIN route · NEMESIS recycle/dedup ·
MNEMOS store/recall · KRONOS schedule/expire · HUGINN compress/synthesize ·
MERIDIAN keel-alignment · HADES archive · PROMETHEUS log-rationale.

**Folders/subfolders = the tiers T0–T9** (already canon). The registry makes them
navigable: each tier a chamber, each system a profiled member.

This adds no god system. It formalizes what ODIN's router (fixed `rank` weights) and
AEGIS's gate (PASS/REDIRECT/FAIL votes) already do into an explicit, auditable body.
Profiles are **views over existing memory/execution_trace tagged by system**, not 27
new stores. GL7 clears it: it turns ad-hoc routing into legible structure.

**The bright line — what makes it auditable, not mysterious:** the council votes and
grows; it does **not** re-weight itself. Growth lives in each member's profile, never
in its vote. Fixed keel, growing accumulation — the same law as JARVIS.

## 5. Explicitly REJECTED (the governance seat's job is to say no)

These came out of the same dialogue. They are rejected, with reasons — rejecting bad
expansion is how a growing system stays a system:

- **Mutating the 27 into stateful "council nodes" (AEGIS+/ODIN+, a God System
  Registry with per-system stats/parameters/bias_vectors).** Violates the fixed-27
  contract (ARCH) and GL7. The 27 are fixed contracts in `chaos_seed.json`, not
  tunable agents. Extend behavior via the *intents* the router already has; never
  redefine a god.
- **Reinforcement-evolving authority weights (a council that re-weights itself).**
  Distinct from §4c, which is *accepted*: a council with **fixed** authority and
  **growing profiles** is the build. What's rejected is authority that *drifts by
  reinforcement* — a gate that learns to relax itself is the failure mode. The council
  grows in profile, never in vote weight. AEGIS strictness is set by the Gold Law, fixed.
- **Bias-vector "personality drift," stability equations, bootstrap seeds.**
  Premature mathematical scaffolding for an emergence we have no data to drive, and
  it encodes drift *in the governance layer* — exactly backwards from §1. Deferred
  indefinitely; revisit only if a real, measured need appears (and it must clear the
  new-system bar: unique, valuable, simplifying).
- **Output-audit metrics feeding bias/council weights (the dual-pass feedback loop).**
  The honesty/output gate is kept (§4b) but its result is **fixed law + a Raven
  flag**, never a signal that tunes governance. A truth-gate that learns to relax
  itself is the worst version of the drift trap. Also rejected: self-scored 0–1
  metrics (accuracy/confidence/hallucination_risk) — an LLM grading its own certainty
  is theater; keep the qualitative honesty surfacing, drop the fake numbers.

Pattern to hold: most "agent upgrade" ideas are features of systems we already have,
or drift dressed as math. Default answer is **extend, or no.**

---

## 6. Build order (each step Raven-gated, GL2)

0. **Honesty layer** — bake the output-gate honesty contract (surface
   uncertain/inferred/missing/assumed; never format to please) into the
   jarvis-respond briefing. Cheapest, most on-identity; ship first.
1. **Reinject lane** — add the identity-summary block to jarvis-respond (cheapest,
   highest signal; uses memory we already have). Manual summary first.
2. **Schedule compress** — KRONOS job: daily/weekly folding with lineage pointers.
3. **Auto-ingest** — SPEAK exchanges auto-event into the spine.
4. **Guard** — NEMESIS drift check + MERIDIAN keel-check on the summary, surfaced to
   Raven for approval.
5. **Council (§4c)** — registry of profiled members (read-only views over tagged
   memory), the council-trace on each decision (fixed-weight votes + reasons,
   auditable), surfaced via a `jarvis_council` readout / the HUD. Formalizes the
   existing router + gate; data-lifecycle verbs (store/recall/recycle/filter/archive)
   become council votes Raven can inspect.

Nothing here adds a god system. Everything reduces future complexity (one loop
replaces ad-hoc saves). GL7 clears it.

---

*The record is the moat. The keel is the self. The loop is how the two grow together.*
