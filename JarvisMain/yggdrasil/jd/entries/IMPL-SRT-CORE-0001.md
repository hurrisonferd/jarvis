---
memory_tier: JLTM
grade: system
name: SRT — Autosort Tool
type: CORE
class: SPEC
tier: MAIN
authority: CANON
owner: JCS Pipeline
steward: 
parent: IMPL-IDX-REG-0001
jnl: IMPL-SRT-CORE-0001
seq: 211
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: JarvisMain/yggdrasil/tools/autosort.py
related: []
references: []
tags: [autosort, jss, status, placement, tool]
aliases: []
ref: [PRI, IDX]
---


**Definition:** Relocates files to match their JSS status. ACTIVE→parent dir; INACTIVE→inactive/; ARCHIVED→JarvisSide/Archive; DEPRECATED→Deprecated/.

**Purpose:** Keep the tree honest. Status drives placement — autosort enforces it.
