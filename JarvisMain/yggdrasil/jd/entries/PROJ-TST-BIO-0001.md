---
memory_tier: JLTM
grade: system
name: JarvisTST
type: BIO
class: SYSTEM
tier: SIDE
authority: CANON
owner: JarvisTST
steward: 
parent: PROJ-IDX-REG-0001
jnl: PROJ-TST-BIO-0001
seq: 115
status: ACTIVE
created: 2026-06-10
updated: 2026-06-24
source: JarvisSide/Projects/JarvisTST/BIO/JARVISTSTBIO-061026-0001-JARVISTST.md
related: []
references: []
tags: [project]
aliases: []
ref: [PRI, IDX]
---


**Definition:** Temporal task and event coordination layer: the Event Ledger (EL, immutable append-only causality record) and the Task State Table (TST, state derived only from EL events). Causality and state, formally separated.

**Purpose:** The temporal backbone for multi-model continuity: no hidden mutations, deterministic replay, desync recovery — work-state persistence the drift sweep can only audit.
