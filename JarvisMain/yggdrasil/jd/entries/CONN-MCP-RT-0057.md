---
name: JIP — revert (propose to git)
type: RT
class: MODULE
tier: MAIN
authority: CANON
owner: Connectors
steward: 
parent: CONN-MSB-CORE-0001
jnl: CONN-MCP-RT-0057
seq: 198
status: ACTIVE
created: 2026-06-16
updated: 2026-06-25
source: JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_jip_revert.md
related: []
references: []
tags: [connector, mcp, tool]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** Roll a JD back git-first: remove its entry from jd/patches.json as a PR so seed restores the source value. AEGIS-gated.

**Purpose:** Governed mirror of the jarvis-mcp tool surface — addressable, auditable.
