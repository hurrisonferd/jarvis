# Topology Lens — the shape of the system

_generated: 2026-06-18T13:27:42Z (2026-06-18 09:27 EDT) · projected from `graph.json` (the canonical graph that already exists). GPT's 'Omni-Map' is this graph; this lens is the query over it — hubs, leaves, isolation, edges._

**206 nodes · 310 edges · 1 isolated · avg degree 3.01.**

## Hubs — the most-connected nodes (the system's load-bearing spine)
| node | degree | in | out | domain |
|---|---|---|---|---|
| `CONN-MSB-CORE-0001` MCP-Supabase Connector | 71 | 71 | 0 | CONN |
| `ARCH-GS-IDX-0001` God Systems Index | 28 | 27 | 1 | ARCH |
| `ARCH-JFS-CORE-0001` Jarvis File System | 17 | 12 | 5 | ARCH |
| `GOV-CAN-CORE-0001` Canon | 17 | 17 | 0 | GOV |
| `PROJ-IDX-REG-0001` Projects Registry | 17 | 16 | 1 | PROJ |
| `ARCH-JMMS-CORE-0001` Jarvis MultiMemory System | 15 | 10 | 5 | ARCH |
| `ARCH-YGG-CORE-0001` Yggdrasil | 13 | 12 | 1 | ARCH |
| `ARCH-AYR-BIO-0001` AYRE Companion Profile | 11 | 8 | 3 | ARCH |
| `IMPL-JCS-CORE-0001` JCS - Jarvis Cognitive Stack | 11 | 9 | 2 | IMPL |
| `GS-SKD-CORE-0001` SKADI | 10 | 8 | 2 | GS |
| `ARCH-JD-CORE-0001` Jarvis Dictionary | 9 | 6 | 3 | ARCH |
| `PROJ-ALL-LOG-0001` Project Log Summary | 9 | 8 | 1 | PROJ |

## Isolated — nodes with NO edges (in or out): unreachable, invisible to the loop
`ARCH-FAM-IDX-0001`

## Edge types (the relationships that bind the graph)
| type | count |
|---|---|
| parent | 200 |
| related | 110 |

## Nodes by domain
| domain | nodes |
|---|---|
| ARCH | 40 |
| AUD | 9 |
| CONN | 68 |
| GOV | 12 |
| GS | 27 |
| IDEA | 4 |
| IMPL | 17 |
| LOG | 2 |
| PROJ | 27 |

_The map was never missing — it's `graph.json`. What this adds is the answer to 'show me the shape.' Next queries (Pressure/Drift/Resilience) are more lenses over the same graph, not new systems._

