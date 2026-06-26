---
memory_tier: JLTM
grade: system
name: JarvisTST — Temporal Task System
type: JGPP
jnl: PROJ-TST-JGPP-0001
status: TASK
created: 2026-06-10
tags: [tst, event-ledger, temporal-system, state-management, jip, jd, jgpp, continuity]
definition: Temporal task and event coordination layer introducing Event Ledger (EL) immutable timestamped append-only record of JIP/JD/JGPP/state transitions and Task State Table (TST) derived only from EL events. All mutations emit events; state is never directly mutated. Enables cross-model replayable state reconstruction and desync recovery.
purpose: Provide temporal backbone for JARVIS multi-model continuity by separating causality (EL) from state (TST), eliminating hidden mutations, and enabling deterministic replay of system state without human relay.
related: []
---

# PROJ-TST-JGPP-0001 — JarvisTST — Temporal Task System
