# Topology Lens — the shape of the system

_generated: 2026-06-15T13:53:47Z (2026-06-15 09:53 EDT) · projected from `graph.json` (the canonical graph that already exists). GPT's 'Omni-Map' is this graph; this lens is the query over it — hubs, leaves, isolation, edges._

**152 nodes · 242 edges · 3 isolated · avg degree 3.18.**

## Hubs — the most-connected nodes (the system's load-bearing spine)
| node | degree | in | out | domain |
|---|---|---|---|---|
| `ARCH-GS-IDX-0001` God Systems Index | 28 | 27 | 1 | ARCH |
| `CONN-MSB-CORE-0001` MCP-Supabase Connector | 24 | 24 | 0 | CONN |
| `GOV-CAN-CORE-0001` Canon | 17 | 17 | 0 | GOV |
| `PROJ-IDX-REG-0001` Projects Registry | 17 | 16 | 1 | PROJ |
| `ARCH-JFS-CORE-0001` Jarvis File System | 16 | 11 | 5 | ARCH |
| `ARCH-JMMS-CORE-0001` Jarvis MultiMemory System | 12 | 8 | 4 | ARCH |
| `ARCH-AYR-BIO-0001` AYRE Companion Profile | 11 | 8 | 3 | ARCH |
| `IMPL-JCS-CORE-0001` JCS - Jarvis Cognitive Stack | 11 | 9 | 2 | IMPL |
| `ARCH-YGG-CORE-0001` Yggdrasil | 10 | 9 | 1 | ARCH |
| `GS-SKD-CORE-0001` SKADI | 10 | 8 | 2 | GS |
| `ARCH-JD-CORE-0001` Jarvis Dictionary | 9 | 6 | 3 | ARCH |
| `PROJ-ALL-LOG-0001` Project Log Summary | 9 | 8 | 1 | PROJ |

## Isolated — nodes with NO edges (in or out): unreachable, invisible to the loop
`ARCH-FAM-IDX-0001`, `IDEA-PAN-INS-0001`, `LOG-MED-LOG-0001`

## Edge types (the relationships that bind the graph)
| type | count |
|---|---|
| parent | 137 |
| related | 105 |

## Nodes by domain
| domain | nodes |
|---|---|
| ARCH | 37 |
| AUD | 8 |
| CONN | 21 |
| GOV | 12 |
| GS | 27 |
| IDEA | 3 |
| IMPL | 15 |
| LOG | 2 |
| PROJ | 27 |

_The map was never missing — it's `graph.json`. What this adds is the answer to 'show me the shape.' Next queries (Pressure/Drift/Resilience) are more lenses over the same graph, not new systems._

