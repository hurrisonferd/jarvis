---
memory_tier: JLTM
grade: system
name: JGLF — Validate structural compliance
type: RT
class: MODULE
tier: MAIN
authority: CANON
owner: Connectors
steward: 
parent: CONN-MSB-CORE-0001
jnl: CONN-MCP-RT-0065
seq: 237
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
source: JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_jglf_validate.md
related: []
references: []
tags: [connector, mcp, tool]
aliases: []
ref: [PRI, IDX]
---


**Definition:** Scan all JD entries and validate JGLF (Jarvis Governance & Layout Framework) compliance. Reports: orphan entries (no parent), broken lineage, missing fields, non-standard domains, empty related arrays, and structural violations. Returns actionable fix list.

**Purpose:** Governed mirror of the jarvis-mcp tool surface — addressable, auditable.
