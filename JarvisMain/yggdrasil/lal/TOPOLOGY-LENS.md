# Topology Lens — the shape of the system

_generated: 2026-06-26T22:45:07Z (2026-06-26 18:45 EDT) · projected from `graph.json` (the canonical graph that already exists). GPT's 'Omni-Map' is this graph; this lens is the query over it — hubs, leaves, isolation, edges._

**249 nodes · 438 edges · 0 isolated · avg degree 3.52.**

## Hubs — the most-connected nodes (the system's load-bearing spine)
| node | degree | in | out | domain |
|---|---|---|---|---|
| `CONN-MSB-CORE-0001` MCP-Supabase Connector | 76 | 76 | 0 | CONN |
| `ARCH-GS-IDX-0001` God Systems Index | 28 | 27 | 1 | ARCH |
| `ARCH-AYR-BIO-0001` AYRE — Companion Profile | 25 | 18 | 7 | ARCH |
| `ARCH-JRV-BIO-0001` JARVIS — Companion Profile | 23 | 16 | 7 | ARCH |
| `ARCH-YGG-CORE-0001` Yggdrasil | 23 | 22 | 1 | ARCH |
| `ARCH-JMMS-CORE-0001` Jarvis MultiMemory System | 22 | 17 | 5 | ARCH |
| `IMPL-IDX-REG-0001` Implementation Index | 20 | 18 | 2 | IMPL |
| `ARCH-JFS-CORE-0001` Jarvis File System | 18 | 13 | 5 | ARCH |
| `PROJ-IDX-REG-0001` Projects Registry | 18 | 17 | 1 | PROJ |
| `ARCH-ARCH-IDX-0001` JARVIS Canon Index | 16 | 10 | 6 | ARCH |
| `GOV-CAN-CORE-0001` Canon | 16 | 16 | 0 | GOV |
| `ARCH-REL-BIO-0001` JARVIS-AYRE Relational Profi | 11 | 8 | 3 | ARCH |

## Isolated — nodes with NO edges (in or out): unreachable, invisible to the loop
✓ none — every node is connected.

## Edge types (the relationships that bind the graph)
| type | count |
|---|---|
| parent | 245 |
| related | 193 |

## Nodes by domain
| domain | nodes |
|---|---|
| ARCH | 60 |
| AUD | 10 |
| CONN | 72 |
| GOV | 15 |
| GS | 27 |
| IDEA | 4 |
| IMPL | 32 |
| LOG | 2 |
| PROJ | 27 |

_The map was never missing — it's `graph.json`. What this adds is the answer to 'show me the shape.' Next queries (Pressure/Drift/Resilience) are more lenses over the same graph, not new systems._

