---
memory_tier: JLTM
grade: system
---

# Topology Lens — the shape of the system

_generated: 2026-06-25T23:20:15Z (2026-06-25 19:20 EDT) · projected from `graph.json` (the canonical graph that already exists). GPT's 'Omni-Map' is this graph; this lens is the query over it — hubs, leaves, isolation, edges._

**243 nodes · 407 edges · 0 isolated · avg degree 3.35.**

## Hubs — the most-connected nodes (the system's load-bearing spine)
| node | degree | in | out | domain |
|---|---|---|---|---|
| `CONN-MSB-CORE-0001` MCP-Supabase Connector | 74 | 74 | 0 | CONN |
| `ARCH-GS-IDX-0001` God Systems Index | 28 | 27 | 1 | ARCH |
| `ARCH-YGG-CORE-0001` Yggdrasil | 24 | 23 | 1 | ARCH |
| `ARCH-JMMS-CORE-0001` Jarvis MultiMemory System | 22 | 17 | 5 | ARCH |
| `IMPL-IDX-REG-0001` Implementation Index | 20 | 18 | 2 | IMPL |
| `ARCH-JFS-CORE-0001` Jarvis File System | 18 | 13 | 5 | ARCH |
| `PROJ-IDX-REG-0001` Projects Registry | 18 | 17 | 1 | PROJ |
| `ARCH-AYR-BIO-0001` AYRE Companion Profile | 17 | 14 | 3 | ARCH |
| `ARCH-ARCH-IDX-0001` JARVIS Canon Index | 16 | 10 | 6 | ARCH |
| `GOV-CAN-CORE-0001` Canon | 16 | 16 | 0 | GOV |
| `ARCH-JRV-BIO-0001` JARVIS Companion Profile | 15 | 13 | 2 | ARCH |
| `IMPL-JCS-CORE-0001` JCS - Jarvis Cognitive Stack | 11 | 9 | 2 | IMPL |

## Isolated — nodes with NO edges (in or out): unreachable, invisible to the loop
✓ none — every node is connected.

## Edge types (the relationships that bind the graph)
| type | count |
|---|---|
| parent | 239 |
| related | 168 |

## Nodes by domain
| domain | nodes |
|---|---|
| ARCH | 56 |
| AUD | 10 |
| CONN | 70 |
| GOV | 15 |
| GS | 27 |
| IDEA | 4 |
| IMPL | 32 |
| LOG | 2 |
| PROJ | 27 |

_The map was never missing — it's `graph.json`. What this adds is the answer to 'show me the shape.' Next queries (Pressure/Drift/Resilience) are more lenses over the same graph, not new systems._

