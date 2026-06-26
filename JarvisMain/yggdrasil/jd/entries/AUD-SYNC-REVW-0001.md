---
name: TUSK Act 4 — Git/Supabase Sync Audit
type: REVW
class: EVENT
tier: MAIN
authority: CANON
owner: Audit
steward: 
parent: GOV-CAN-CORE-0001
jnl: AUD-SYNC-REVW-0001
seq: 151
status: ACTIVE
created: 2026-06-15
updated: 2026-06-26
source: JarvisMain/Audit/tusk-act4-sync-audit.md
related: []
references: []
tags: [audit, sync, governance, git-first]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** Penetrating audit of git<->Supabase sync; finds the connector-first canon-write paths (jd_approve, jip_apply/revert) that bypass git.

**Purpose:** Establish Git-First Canon: canon writes go to git first, then mirror to Supabase (Raven 2026-06-15).
