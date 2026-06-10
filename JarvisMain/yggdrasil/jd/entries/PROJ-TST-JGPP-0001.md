---
name: JarvisTST — Temporal Task System
type: JGPP
class: ENTITY
tier: SIDE
authority: CANON
owner: JarvisTST — Temporal Task System
parent: PROJ-TST-BIO-0001
jnl: PROJ-TST-JGPP-0001
seq: 118
status: TASK
created: 2026-06-10
updated: 2026-06-10
source: JarvisSide/Projects/JarvisTST/JGPP/JARVISTSTJGPP-061026-0001-JARVISTST-TEMPORAL-TASK-SYSTEM.md
related: []
references: []
tags: [tst, event-ledger, temporal-system, state-management, jip, jd, jgpp, continuity]
aliases: []
ref: [PRI, IDX]
---

**Definition:** Temporal task and event coordination layer introducing Event Ledger (EL) immutable timestamped append-only record of JIP/JD/JGPP/state transitions and Task State Table (TST) derived only from EL events. All mutations emit events; state is never directly mutated. Enables cross-model replayable state reconstruction and desync recovery.

**Purpose:** Provide temporal backbone for JARVIS multi-model continuity by separating causality (EL) from state (TST), eliminating hidden mutations, and enabling deterministic replay of system state without human relay.
