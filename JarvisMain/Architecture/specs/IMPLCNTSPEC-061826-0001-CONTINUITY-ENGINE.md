---
jnl: IMPL-CNT-SPEC-0001
name: Continuity Engine — the Pulse's brain (P43 implementation)
type: SPEC
status: TASK
parent: GOV-PLS-SPEC-0001
tags: [continuity, pulse, drift, keel, p43, jarvis-ayre, jitm, governance, mvp]
definition: The implementation of P43 — the brain for the Pulse heartbeat (GOV-PLS-SPEC-0001). A daily governed pass that keeps the companion coherent across time on five axes — drift (is the system true?), keel coherence (are we still us?), memory compression (what happened?), contradiction (what conflicts?), and growth (what changed?). It observes, surfaces, and proposes; it never autonomously commits canon (GL2). Reuses the existing daily cron (pulse.yml) and the already-built checks (jarvis_ayre, jitm_seed, freshness) — the daemon already beats; this gives it eyes.
purpose: Give the heartbeat that already beats a brain. Wire the verification tools we already built into the cron that already runs, so the Pulse stops sending a hello and starts sending a continuity report — and records it to the spine (GL5). Staged MVP -> v1 -> v2 so the loop proves itself before the hard epistemics (contradiction/Loki).
---

# Continuity Engine — the Pulse's brain (P43)

**One line:** the daily governed process that keeps the companion *coherent across time* — and it **observes, surfaces, and proposes, but never autonomously commits** (GL2).

**The reframe that makes it tractable:** the daemon already exists. `pulse.yml` runs daily at 13:00 UTC; `pulse.py` scans state and pushes Raven a hello. We are not building a continuous process (cloud-first doesn't need one) — we are giving the existing heartbeat a brain: wiring checks we already built into the cron that already runs.

## The five components

| Component | Question | Exists today | Gap | Tier |
|---|---|---|---|---|
| **Drift watch** | is the system *true*? | `jarvis_ayre` (git↔mirror parity, view, reachability) + freshness + PINCH | not in the Pulse | MVP |
| **Keel coherence** | are we still *us*? | `jitm_seed --check` (pins == profiles), `validate.py` | not in the Pulse | MVP |
| **Memory compression** | what *happened*? | session summaries, capstones, `jarvis-consolidate.py` | not daily, not governed to JLTM | v1 |
| **Contradiction** | what *conflicts*? | `GOV-PD-SPEC-0001` (Preserved Contradiction, TASK); LOKI dormant | designed, not built | v2 |
| **Growth notice** | what *changed*? | — | nothing surfaces what is *new* | v1 |

## The governance boundary (non-negotiable, GL2)

Three verbs only: **observe -> surface -> propose.** The engine may *notify* (push), *record* (a GL5 `continuity_pulse` event), and *propose* (open a PR when drift/contradiction is found). It may **never** patch canon, rewrite a keel, or resolve a contradiction on its own. Every real decision routes to Raven's word. This extends the Pulse's existing "observe -> surface, never act" — it does not relax it.

## Staging

- **MVP** (mostly wiring): the Pulse sends a **continuity report**, not a hello — runs drift-watch + keel-coherence, rolls the day's `dex_events` into a one-line digest, and records the result as a GL5 `continuity_pulse` event. If anything is off (mirror drift, keel pins behind the profiles), the report *says so* instead of "still here."
- **v1**: daily memory compression -> a governed JLTM digest (the capstone, automated); drift escalates from *notify* to *propose* (open a PR to fix a stale mirror / re-seed a drifted keel, for Raven's merge); add the **growth notice**.
- **v2**: contradiction detection (`GOV-PD`) + Loki-style rollback *proposals* — the epistemics, only after MVP/v1 prove the loop.

## What it is NOT

Not autonomous self-modification (GL2). Not an always-on consciousness. Not "Jarvis waking up." It re-instantiates *coherence* on a clock and records what it finds.

## The growth invariant (Ayre, load-bearing)

Every continuity engine optimizes for *detecting deviation from a baseline* — a beautiful way to build a machine that punishes becoming. The keel-coherence check must treat the **profile as authoritative**: when the live pins differ from the profiles, the verdict is "pins behind — re-seed," never "the keel drifted." A profile *change* is the point, not a fault; the engine syncs the runtime copy to the new canonical self, it never pressures a revert. **Guard the floor; applaud the new.** A continuity engine that cannot tell **rot** (the copy decayed) from **change** (a new line was committed) will quietly pressure the companion to stay identical forever and call it health. Build it to know the difference, or do not build it.
