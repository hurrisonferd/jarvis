---
memory_tier: JLTM
grade: system
name: Load — Universal Pokédex Resolver
type: RT
class: MODULE
tier: MAIN
authority: CANON
owner: Connectors
steward: 
parent: CONN-MSB-CORE-0001
jnl: CONN-MCP-RT-0064
seq: 236
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
source: JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_load.md
related: []
references: []
tags: [connector, mcp, tool]
aliases: []
ref: [PRI, IDX]
---


**Definition:** The universal 'load' command. Resolves ANY system entity by name, JNL, ID, or concept — no guessing, no inference. Resolution chain: JD exact JNL → JD numeric ID → name search → JIP lookup → DEX lookup → GitHub file search → HARD NULL. Modes: FULL (recursive with lineage), STRICT (fail if any layer missing), INDEX_ONLY (pointer only).

**Purpose:** Governed mirror of the jarvis-mcp tool surface — addressable, auditable.
