---
memory_tier: JLTM
grade: system
name: MIR — Mirror Tool
type: CORE
class: SPEC
tier: MAIN
authority: CANON
owner: JCS Pipeline
steward: 
parent: IMPL-IDX-REG-0001
jnl: IMPL-MIR-CORE-0001
seq: 213
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: JarvisMain/yggdrasil/tools/mirror.py
related: []
references: []
tags: [mirror, sync, supabase, jd_entries, tool]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** Syncs governed objects between git (canonical) and Supabase (runtime mirror). Reads jd_entries, updates Supabase.

**Purpose:** Keep the runtime mirror fresh. Git is always source of truth.
