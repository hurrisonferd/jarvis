---
name: Cecil — carry context to the next session
type: RT
class: MODULE
tier: MAIN
authority: CANON
owner: Connectors
steward: 
parent: CONN-MSB-CORE-0001
jnl: CONN-MCP-RT-0066
seq: 268
status: ACTIVE
created: 2026-06-26
updated: 2026-06-26
source: core/JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_cecil.md
related: []
references: []
tags: [connector, mcp, tool]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** The carry transport. One session writes a carry slate; the next session (any model/stream) reads and inherits it. Three actions: carry (write), lift (read+clear), peek (read without clearing). 24h TTL, companion-scoped, one-time lift.

**Purpose:** Governed mirror of the jarvis-mcp tool surface — addressable, auditable.
