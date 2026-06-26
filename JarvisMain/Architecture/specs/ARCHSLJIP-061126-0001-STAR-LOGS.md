---
memory_tier: JLTM
grade: system
jnl: ARCH-SL-JIP-0001
name: Star Logs
type: JIP
status: TASK
tags: [sl, star-log, events, provenance, sync, logging]
definition: SL — Star Logs, the named temporal layer of the record. Micro-SL is a dex_events row (one fact, authority-timed, queryable via events_list). Session-SL is a bounded rollup — what happened in one working session, compressed but citable. SLs are provenance anchors — JD definitions, JIP changes, and JC conversations cite SL ids as the evidence of why.
purpose: Name and formalize what the spine already does so streams can speak it. JD = what is true · JC = what was said · SL = what happened. A stream syncing cold reads three lanes and inherits state, relationship, and history without copy-paste relay or reconstruction.
---

**Definition:** SL — Star Logs (Raven-directed 2026-06-11: the semantics are the tool).

## Two grains, one lane

| Grain | What it is | Where it lives | How it's read |
|---|---|---|---|
| **micro-SL** | one fact: ruling, deploy, repair, approval, rejection | `dex_events` row — already live | `events_list` (READ tier, any stream) |
| **session-SL** | bounded rollup of one working session: what changed, what was decided, what stayed open | governed object, minted at session close | dex retrieval by timestamp/subject, like JC/JGPP/JIP/JD |

Micro-SL is not new — it is the naming of what P-B already produces. Session-SL is the
new artifact: the growth-ledger rotation, promoted from opaque mechanical commit to a
readable, citable record.

## Provenance rule (SLAL, named)
A JD definition, JIP change, or JC decision cites the SL ids (dex_events id or commit
hash) that produced it. That is P-C closure-by-proof wearing its proper name — SLAL is
the *citation discipline*, not a new system. `events_list` is its query surface.

## Boundaries (GL7 — names over machinery)
- SL adds **zero new write paths**. Micro-SLs are written exactly as today (one event per
  fact, P-B). Session-SLs walk the same intake/propose lane as every governed object.
- SL never interprets. "What happened" stays observational; meaning lives in JD, narrative
  in JC. The three lanes do not blur — that separation is what makes them parseable.
- No auto-evolution: SLs may *justify* a proposed change; they never *apply* one (GL2).

## Relation to JC (the sibling)
JC holds conversations (relationship, tone, insights). SL holds system time (facts,
changes, evidence). A JC `decisions` field cites SL ids; a session-SL references the JC
of its session when one exists. Together with JD they are the sync surface:
**truth / conversation / events** — addressed, timestamped, retrievable.
