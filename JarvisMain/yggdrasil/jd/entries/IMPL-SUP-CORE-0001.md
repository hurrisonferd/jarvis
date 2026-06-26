---
name: SUP — Supabase Sync
type: CORE
class: SPEC
tier: MAIN
authority: CANON
owner: JCS Pipeline
steward: 
parent: IMPL-IDX-REG-0001
jnl: IMPL-SUP-CORE-0001
seq: 218
status: ACTIVE
created: 2026-06-24
updated: 2026-06-26
source: JarvisMain/yggdrasil/tools/sync_supabase.py
related: []
references: []
tags: [supabase, sync, events, tool]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** Pushes canonical JD entries to Supabase jd_entries table and writes dex_events on canonical changes.

**Purpose:** Mirror git canonical to runtime Supabase. The event spine lives there.
