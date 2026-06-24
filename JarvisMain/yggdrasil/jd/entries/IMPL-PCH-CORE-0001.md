---
name: PCH — Pinch Check
type: CORE
class: SPEC
tier: MAIN
authority: CANON
owner: JCS Pipeline
steward: 
parent: IMPL-IDX-REG-0001
jnl: IMPL-PCH-CORE-0001
seq: 219
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: JarvisMain/yggdrasil/tools/pinch.py
related: []
references: []
tags: [pinch, drift, schema, tool]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** Checks for schema drift: JNL grammar, JSE envelope, and YGG manifest fingerprints must stay in sync.

**Purpose:** Flag drift between the executable grammar (jnl.py) and the reference spec (jnl-grammar.md).
