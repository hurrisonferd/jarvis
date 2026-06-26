---
memory_tier: JLTM
grade: system
name: Sticky Fingers — Governance-Coverage Audit
type: REVW
class: EVENT
tier: MAIN
authority: CANON
owner: Audit
steward: 
parent: GOV-CAN-CORE-0001
jnl: AUD-GATE-REVW-0001
seq: 152
status: ACTIVE
created: 2026-06-15
updated: 2026-06-24
source: JarvisMain/Audit/sticky-fingers-governance-audit.md
related: []
references: []
tags: [audit, governance, aegis, security]
aliases: []
ref: [PRI, IDX]
---


**Definition:** Maps every state-mutation path and its gate; finds + closes the two ungated seams (github_write, pr_merge).

**Purpose:** Prove no ungated path to canon or runtime; gate every connector mutator with the AEGIS token (Raven 2026-06-15).
