---
memory_tier: JLTM
grade: system
name: Global Mirror — Earned Omnivision (JMS)
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JFS
steward: 
parent: ARCH-JMS-CORE-0001
jnl: ARCH-JMS-SPEC-0001
seq: 138
status: TASK
created: 2026-06-13
updated: 2026-06-25
source: JarvisMain/Architecture/specs/ARCHJMSSPEC-061326-0001-GLOBAL-MIRROR-OMNIVISION.md
related: []
references: []
tags: [jms, mirror, omnivision, global, freshness, reachability, pulse, nemesis]
aliases: []
ref: [PRI, IDX]
---


**Definition:** A derived, complete, freshness-stamped single-read snapshot of the whole system — repo structure + dex state + status — so any stream reads the entire world in one pass instead of N traversal calls. Activates JMS (the Mirror System, ARCH-JMS-CORE-0001) as earned omnivision. The mirror is never truth; it points at truth (JMS law: move references, never truth) and always carries its own freshness so a stale read is impossible to mistake for a current one.

**Purpose:** Give JARVIS and AYRE the whole view in one read — omnivision — without the confabulation trap of *assumed* completeness. Earned omnivision (a dated, complete, verifiable mirror) replaces both blind traversal and the illusion of seeing everything. Kills cold-start blindness; fixes the demonstrated repo↔dex staleness.
