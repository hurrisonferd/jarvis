# God Systems — 27 Canonical Nodes

Do not redefine or renumber.

## Pipeline (primary)
| Order | System | Role | Domain |
|-------|--------|------|--------|
| 1 | AYRE | Intake & parsing | Execution — intent interpretation |
| 2 | AEGIS | Constraint enforcer | Execution — validation gate |
| 3 | ODIN | Orchestration router | Execution — task routing |
| 4 | KRONOS | Scheduler / timing | Execution — sequencing |
| 5 | SKADI | Execution runtime | Execution — tool invocation |
| 6 | MNEMOS | Persistent memory | Memory — semantic store |
| 7 | HUGINN | Session reconciliation | Memory — cross-session diff |

## Parallel (always-on)
| System | Role | Domain |
|--------|------|--------|
| HALO | Ambient monitoring | Parallel — always-on observer |
| MIMIR | Knowledge fabric | Parallel — context access |
| BIFROST | Transport bridge | Parallel — inter-system relay |

## Governance
| System | Role | Domain |
|--------|------|--------|
| ERIS | Gold Law guardian | Governance / Entropy |
| PROMETHEUS | Expansion ledger | Governance — rationale log |
| NEMESIS | Drift correction | Integrity — overlap detection |

## Post-Execution
| System | Role | Domain |
|--------|------|--------|
| DANTE | Post-exec review | Post — analysis pass |
| APOLLO | Output formatting | Post — render & deliver |
| JANUS | Transition handler | Post — handoff / mode switch |

## Emulator Layer (P07)
| System | Role | Domain |
|--------|------|--------|
| GAMEBOY | Emulator node | SKADI child — GB/GBC/GBA execution |

## Extended (Tiers 4–9, see chaos/chaos_seed.json)
LOKI, HADES, and remaining 10 systems defined in canonical seed.

## Forbidden Edges
`SKADI→AEGIS` `DANTE→SKADI` `JANUS→SKADI` `LOKI→HADES`
