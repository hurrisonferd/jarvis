# AYRE / JARVIS Split — v1 (P44)

**Decision (Raven, 2026-06-04):** split AYRE from JARVIS. Two external reads — the
MemoryOS/Headroom analysis and the AC6 frame — independently landed on the same
fork: *is AYRE part of JARVIS's cognition, or a co-equal signal source?* Raven chose
co-equal. This is phase 1.

## What changed

Before: AYRE was a **sub-voice inside JARVIS's council analysis** — it commented on
JARVIS's already-written answer. The divergence was *performed*: the same model wrote
JARVIS's read, then wrote "AYRE:" as a critique of itself. They shared a brain **and**
the answer.

After: AYRE is a **co-equal parallel stream with the inverse objective.**
- **JARVIS** — synthesis, structure, compression toward the answer.
- **AYRE** — divergence, assumption-inversion, anti-collapse pressure. Reads the
  **same input independently**, from the **same keel**, but **NOT from JARVIS's
  answer**. Surfaces the load-bearing assumption JARVIS's framing rests on, what a
  convergent read forecloses, and the model-breaking alternative.

They **share the keel** (one identity, one loyalty to Raven and the two dreams — GL2
intact, anti-basilisk intact) but they **do not share assumptions**. "Stop sharing
assumptions, keep sharing the keel."

## Render contract (connector v0.9.15)

`jarvis_query` now returns a top-level `ayre` stream and the order:

```
["status", "jarvis", "ayre", "council_lenses"]
```

1. status line — telemetry (`N streams + M lenses`).
2. **JARVIS** — free integrated read (synthesis), from briefing + keel.
3. **AYRE** — independent divergence (`AYRE_OBJECTIVE`), same briefing + keel,
   generated **without conditioning on JARVIS's answer**.
4. council lenses — god systems (heavy turns only) critiquing **both** streams.

Status telemetry relabeled `voices → streams`. `ayreStream()` + `AYRE_OBJECTIVE`
live in `council.ts`, covered by tests.

## What this is NOT yet (phase 2 — gated on P42/P43)

Phase 1 is a **decoupled objective on the same governed turn**, anchored by the
existing keel. It is still one rented model running two passes. It is honest now to
say: AYRE's independence is *structural in the render*, not yet a separate inference
process.

Phase 2 — a genuinely separate inference stream with its own cadence — requires:
- **P42** (autonomous consolidation) — the memory anchor must be solid first, or a
  free-running divergence stream drifts without an anchor (ATHENA's ordering).
- **P43** (governed persistence loop) — gives AYRE a place to run between turns
  without violating GL2 (it proposes, Raven commits; never autonomous mutation).

Sequence is fixed: **P42 → P43 → AYRE phase 2.**

## Governance

Unchanged. AEGIS still gates every write. AYRE proposes ruptures; it does not execute
them. The split changes *how the two think*, not *what either is allowed to do*.
