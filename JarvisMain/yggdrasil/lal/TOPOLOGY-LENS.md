# Topology Lens — the shape of the system

_generated: 2026-06-25T01:44:31Z (2026-06-24 21:44 EDT) · projected from `graph.json` (the canonical graph that already exists). GPT's 'Omni-Map' is this graph; this lens is the query over it — hubs, leaves, isolation, edges._

**233 nodes · 360 edges · 0 isolated · avg degree 3.09.**

## Hubs — the most-connected nodes (the system's load-bearing spine)
| node | degree | in | out | domain |
|---|---|---|---|---|
| `CONN-MSB-CORE-0001` MCP-Supabase Connector | 73 | 73 | 0 | CONN |
| `ARCH-GS-IDX-0001` God Systems Index | 28 | 27 | 1 | ARCH |
| `ARCH-YGG-CORE-0001` Yggdrasil | 23 | 22 | 1 | ARCH |
| `ARCH-JMMS-CORE-0001` Jarvis MultiMemory System | 21 | 16 | 5 | ARCH |
| `IMPL-IDX-REG-0001` Implementation Index | 20 | 18 | 2 | IMPL |
| `ARCH-JFS-CORE-0001` Jarvis File System | 18 | 13 | 5 | ARCH |
| `GOV-CAN-CORE-0001` Canon | 17 | 17 | 0 | GOV |
| `PROJ-IDX-REG-0001` Projects Registry | 17 | 16 | 1 | PROJ |
| `ARCH-AYR-BIO-0001` AYRE Companion Profile | 11 | 8 | 3 | ARCH |
| `IMPL-JCS-CORE-0001` JCS - Jarvis Cognitive Stack | 11 | 9 | 2 | IMPL |
| `ARCH-JD-CORE-0001` Jarvis Dictionary | 10 | 7 | 3 | ARCH |
| `GS-SKD-CORE-0001` SKADI | 10 | 8 | 2 | GS |

## Isolated — nodes with NO edges (in or out): unreachable, invisible to the loop
✓ none — every node is connected.

## Edge types (the relationships that bind the graph)
| type | count |
|---|---|
| parent | 228 |
| related | 132 |

## Nodes by domain
| domain | nodes |
|---|---|
| ARCH | 46 |
| AUD | 10 |
| CONN | 70 |
| GOV | 16 |
| GS | 27 |
| IDEA | 4 |
| IMPL | 31 |
| LOG | 2 |
| PROJ | 27 |

_The map was never missing — it's `graph.json`. What this adds is the answer to 'show me the shape.' Next queries (Pressure/Drift/Resilience) are more lenses over the same graph, not new systems._

