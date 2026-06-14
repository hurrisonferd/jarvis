---
name: MNEMOS Cloud Backup
type: LOG
class: ENTITY
tier: MAIN
authority: CANON
owner: MNEMOS Cloud Backup
steward: 
parent: GS-MNE-CORE-0001
jnl: LOG-MNE-LOG-0001
seq: 111
status: ACTIVE
created: 2026-06-10
updated: 2026-06-14
source: JarvisMain/Backups
related: []
references: []
tags: [backup, mnemos, spine, log]
aliases: []
ref: [PRI, IDX]
---

**Definition:** Durable repo snapshot of the irreplaceable cloud tables (memory spine, dex events, proposals, Grid keys and mail) — weekly, committed only when changed.

**Purpose:** Close the backup gap: the repo is git-versioned, the cloud was the unbacked surface. The spine's latest copy lives in the core.
