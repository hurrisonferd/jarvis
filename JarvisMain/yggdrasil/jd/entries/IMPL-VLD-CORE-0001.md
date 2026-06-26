---
memory_tier: JLTM
grade: system
name: VLD — Validate Tool
type: CORE
class: SPEC
tier: MAIN
authority: CANON
owner: JCS Pipeline
steward: 
parent: IMPL-IDX-REG-0001
jnl: IMPL-VLD-CORE-0001
seq: 210
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: JarvisMain/yggdrasil/tools/validate.py
related: []
references: []
tags: [validate, jve, gl12, governance, tool]
aliases: []
ref: [PRI, IDX]
---


**Definition:** JVE — enforces GL12 closure: every governed file has a JNL, valid JSE frontmatter, no dangling edges, zero ungoverned files.

**Purpose:** Be the hard gate before every commit. Fail loud — no silent governance gaps.
