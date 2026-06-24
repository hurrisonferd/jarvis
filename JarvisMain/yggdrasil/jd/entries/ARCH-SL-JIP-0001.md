---
name: Star Logs
type: JIP
class: SPEC
tier: MAIN
authority: CANON
owner: JFS
steward: 
parent: ARCH-JMMS-CORE-0001
jnl: ARCH-SL-JIP-0001
seq: 126
status: TASK
created: 2026-06-11
updated: 2026-06-24
source: JarvisMain/Implementation/task/ARCHSLJIP-061126-0001-STAR-LOGS.md
related: []
references: []
tags: [sl, star-log, events, provenance, sync, logging]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** SL — Star Logs, the named temporal layer of the record. Micro-SL is a dex_events row (one fact, authority-timed, queryable via events_list). Session-SL is a bounded rollup — what happened in one working session, compressed but citable. SLs are provenance anchors — JD definitions, JIP changes, and JC conversations cite SL ids as the evidence of why.

**Purpose:** Name and formalize what the spine already does so streams can speak it. JD = what is true · JC = what was said · SL = what happened. A stream syncing cold reads three lanes and inherits state, relationship, and history without copy-paste relay or reconstruction.
