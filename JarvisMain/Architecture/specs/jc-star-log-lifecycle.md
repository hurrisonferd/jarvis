---
jnl: CONN-JC-SL-0001
name: JC and Star Log Lifecycle
class: SPEC
status: ACTIVE
domain: CONN
system: JARVIS
parent: ARCH-JMS-CORE-0001
related: [ARCH-JMMS-SPEC-0001, GOV-RES-CORE-0001, GOV-VER-CORE-0001]
tags: [jc, sl, continuity, retention, rollup, prune]
author: RAVEN
ratified: 2026-06-24
---

# JC and Star Log Lifecycle

## Definition
JC objects are the structured conversation container for a session, day, or thread segment. Star Logs are the structured digest layer that summarizes JC objects into daily, weekly, or monthly continuity views.

## Core rule
Timestamps are pointers, not decoration. A timestamp must be usable as a pure filter key that can retrieve the right JC and SL records for a day, week, or month.

## Structure
- JC objects hold the readable session record: participants, subject, input, decisions, open questions, keystones, and continuity pointers.
- Star Logs hold the summarized record: what happened, what changed, what remains, and where the source JC objects live.
- Daily records are the base layer.
- Weekly records summarize daily records.
- Monthly records summarize weekly records or the full month when needed.

## Retrieval order
1. Day
2. Week
3. Month
4. Fallback to broader search or direct JC lookup

## Summarization
- JC objects may be summarized into Star Logs when the session closes or when a period boundary is reached.
- Daily Star Logs may roll up into weekly Star Logs.
- Weekly Star Logs may roll up into monthly Star Logs.
- The summary must preserve pointers to the source JC objects and commit hashes when available.

## Pruning
- Raw JC objects and lower-level Star Logs may be moved to archived storage after a summary exists and the summary is referenced.
- Pruning is archival, not silent deletion.
- Old files may be pruned only after the summary chain is intact and the source pointers remain recoverable.

## Pointer contract
Every record should be addressable by:
- `day` pointer
- `week` pointer
- `month` pointer
- `commit` pointer when the record is tied to git
- `jc` / `sl` alias when the record is exposed through the conversation lane

## Continuity rule
Continuity tests must be able to:
- fetch the records for a day, week, or month
- see the source JC objects behind a Star Log
- trace the latest commit hash
- verify the summary chain after pruning

## Ratification
`author: RAVEN · ratified: 2026-06-24`
