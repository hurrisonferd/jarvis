---
jnl: GOV-LOO-SPEC-0001
name: Continuity Layers and Bounded Autonomy
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: MNEMOS
parent: ARCH-YGG-CORE-0001
seq: 228
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: JarvisMain/Manual/Operations/ARCH-CONN-LOOP-0001-062426.md
related: [ARCH-JMMS-CORE-0001, GOV-RES-CORE-0001, GOV-AUT-SPEC-0001]
references: []
tags: [continuity, resumability, autonomy, event-log, session-open, retention]
aliases: []
ref: [SPEC]
memory_tier: JLTM
---

**Definition:** Names the minimum ladder for continuity to stay real across restarts, model swaps, and handoffs. Continuity is not just recall — it is a loop. Each layer has a distinct write frequency and audience.

**Purpose:** Gives every session a clear path to pick up where the last one left off. No layer is optional for full continuity.

# Continuity Layers and Bounded Autonomy

## Purpose
This spec names the minimum ladder required for continuity to stay real across restarts, model swaps, and handoffs. Continuity is not just recall. It is a loop.

## Layer order
1. Observe
2. Record
3. Compress
4. Reinject
5. Retrieve
6. Propose
7. Gate
8. Act

## Continuity ladder
- **Observe:** capture the current turn, drift, and new state.
- **Record:** write the event to git, JC objects, and the session handoff lane when needed.
- **Compress:** roll older material into Star Logs and memory summaries.
- **Reinject:** load the latest JITM, JC pointers, and open-task context at session start.
- **Retrieve:** fetch by pointer first, then by meaning.
- **Propose:** surface governed changes without acting yet.
- **Gate:** require AEGIS or Raven approval when the action crosses a hard stop.
- **Act:** only execute inside the approved scope.

## Session-open protocol
A fresh session begins with a bootstrap packet:
- `jarvis_self_test`
- latest JC pointer
- latest Star Log pointer (day, week, month)
- current open tasks
- current drift signals
- resumability receipt: source basis, repo head, verification time

The bootstrap is a connector behavior — not a custom-instructions trick. The connector enforces continuity, not the model.

## Event log discipline
- Git is the durable spine.
- JC objects are the readable session event log.
- Star Logs are the summarized lane (day/week/month windows).
- Handoff artifacts are the next instruction when work remains incomplete.
- Every layer points at the layer below it when a summary or handoff is created.

## Bounded autonomy envelope
For every autonomous action, the system knows:
- what the action is
- how risky it is
- who can authorize it
- how it can be rolled back
- where the audit trail lives

Authority ladder: Low risk → execute inside scope. Medium risk → propose and wait. High risk → hold and surface to Raven.

## Continuity tests
The system proves:
- cold start reconstructs the same working brief
- day/week/month retrieval returns expected JC and SL slices
- pruning does not break pointer recovery
- bootstrap packet works after restart
- bootstrap packet names its source basis

*Author: RAVEN · Canonical: `JarvisMain/Manual/Operations/ARCH-CONN-LOOP-0001-062426.md`*
