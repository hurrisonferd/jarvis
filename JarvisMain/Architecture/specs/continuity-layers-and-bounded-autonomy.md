---
jnl: ARCH-CONN-LOOP-0001
name: Continuity Layers and Bounded Autonomy
class: SPEC
status: ACTIVE
domain: ARCH
system: JARVIS
parent: ARCH-JMS-CORE-0001
related: [ARCH-JMMS-SPEC-0001, CONN-JC-SL-0001, GOV-RES-CORE-0001, GOV-VER-CORE-0001]
tags: [continuity, resumability, autonomy, event-log, session-open, retention]
author: RAVEN
ratified: 2026-06-24
---

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
- Observe: capture the current turn, drift, and new state.
- Record: write the event to git, JC objects, and the session handoff lane when needed.
- Compress: roll older material into Star Logs and memory summaries.
- Reinject: load the latest JITM, JC pointers, and open-task context at session start.
- Retrieve: fetch by pointer first, then by meaning.
- Propose: surface governed changes without acting yet.
- Gate: require AEGIS or Raven approval when the action crosses a hard stop.
- Act: only execute inside the approved scope.

## Session-open protocol
A fresh session should begin with a bootstrap packet that includes:
- `jarvis_self_test`
- latest JC pointer
- latest Star Log pointer for day, week, and month
- current open tasks
- current drift signals
- a resumability receipt showing source basis, repo head, and verification time

The bootstrap is a connector behavior, not a custom-instructions trick. The connector should be the first place that continuity gets enforced.

## Event log discipline
- Git is the durable spine.
- JC objects are the readable session event log.
- Star Logs are the summarized lane for day, week, and month windows.
- Handoff artifacts are the next instruction when work remains incomplete.
- Every layer should point at the layer below it when a summary or handoff is created.

## Bounded autonomy envelope
For every autonomous action, the system should know:
- what the action is
- how risky it is
- who can authorize it
- how it can be rolled back
- where the audit trail lives

Default authority ladder:
- Low risk: execute inside scope
- Medium risk: propose and wait for Raven
- High risk: hold and surface to Raven

## Retention and pruning
- Raw JC objects can be archived after a summary exists and pointers remain recoverable.
- Star Logs may roll up from day to week to month.
- Pruning is allowed only when the summary chain is intact.
- Timestamps are pointers, not decoration.

## Continuity tests
The system should be able to prove:
- a cold start can reconstruct the same working brief
- day/week/month retrieval returns the expected JC and SL slices
- pruning does not break pointer recovery
- the bootstrap packet still works after restart
- the bootstrap packet identifies its source basis explicitly

## Ratification
`author: RAVEN`
