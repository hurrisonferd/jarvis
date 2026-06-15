# Topology Lens — the shape of the system

_generated: 2026-06-15T07:38:17Z (2026-06-15 03:38 EDT) · projected from `graph.json` (the canonical graph that already exists). GPT's 'Omni-Map' is this graph; this lens is the query over it — hubs, leaves, isolation, edges._

**133 nodes · 194 edges · 7 isolated · avg degree 2.92.**

## Hubs — the most-connected nodes (the system's load-bearing spine)
| node | degree | in | out | domain |
|---|---|---|---|---|
| `ARCH-GS-IDX-0001` God Systems Index | 28 | 27 | 1 | ARCH |
| `CONN-MSB-CORE-0001` MCP-Supabase Connector | 22 | 22 | 0 | CONN |
| `ARCH-JFS-CORE-0001` Jarvis File System | 16 | 11 | 5 | ARCH |
| `IMPL-JCS-CORE-0001` JCS - Jarvis Cognitive Stack | 11 | 9 | 2 | IMPL |
| `ARCH-JMMS-CORE-0001` Jarvis MultiMemory System | 10 | 6 | 4 | ARCH |
| `GS-SKD-CORE-0001` SKADI | 10 | 8 | 2 | GS |
| `ARCH-JD-CORE-0001` Jarvis Dictionary | 8 | 5 | 3 | ARCH |
| `GOV-CAN-CORE-0001` Canon | 8 | 8 | 0 | GOV |
| `GS-AYR-CORE-0001` AYRE | 8 | 6 | 2 | GS |
| `PROJ-ALL-LOG-0001` Project Log Summary | 8 | 8 | 0 | PROJ |
| `ARCH-YGG-CORE-0001` Yggdrasil | 7 | 6 | 1 | ARCH |
| `GS-AEG-CORE-0001` AEGIS | 7 | 5 | 2 | GS |

## Isolated — nodes with NO edges (in or out): unreachable, invisible to the loop
`ARCH-FAM-IDX-0001`, `ARCH-JC-JIP-0001`, `ARCH-JD-JIP-0001`, `ARCH-SL-JIP-0001`, `GOV-CHO-JD-0001`, `GOV-LC-SPEC-0001`, `GOV-PD-SPEC-0001`

## Edge types (the relationships that bind the graph)
| type | count |
|---|---|
| related | 101 |
| parent | 93 |

## Nodes by domain
| domain | nodes |
|---|---|
| ARCH | 28 |
| AUD | 5 |
| CONN | 21 |
| GOV | 9 |
| GS | 27 |
| IDEA | 2 |
| IMPL | 14 |
| LOG | 1 |
| PROJ | 26 |

_The map was never missing — it's `graph.json`. What this adds is the answer to 'show me the shape.' Next queries (Pressure/Drift/Resilience) are more lenses over the same graph, not new systems._

