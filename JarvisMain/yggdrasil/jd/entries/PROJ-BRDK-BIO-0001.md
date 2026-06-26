---
memory_tier: JLTM
grade: system
name: Bridgekeeper
type: BIO
class: SYSTEM
tier: SIDE
authority: CANON
owner: Bridgekeeper
steward: 
parent: PROJ-IDX-REG-0001
jnl: PROJ-BRDK-BIO-0001
seq: 263
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
source: JarvisSide/Projects/Bridgekeeper/BIO/BRDKBIO-062525-0001-BRIDGEKEEPER.md
related: [PROJ-ALL-LOG-0001, ARCH-SYS-SPEC-0001]
references: []
tags: [project, security, governance, github]
aliases: []
ref: [PRI, IDX]
---


**Definition:** GitHub PR challenge gate for external contributors — Bridgekeeper asks questions before PRs can merge.

**Purpose:** >


---

## Phase 2 (deployed 2026-06-26)

ERIS is now a **stall trap honeypot** — not a filter.

**Commit:** `3f42a967`
**Files:** `scripts/eris_bridgekeeper.py`, `.github/workflows/bridgekeeper.yml`

**How it works:**
- Every non-collaborator PR gets occupied: questions never stop
- 4 mining pools: intent, tech, recon (what else have you looked at), behavior
- ATHENA entropy scoring on every answer (0.0=coherent, 1.0=hostile/automated)
- Domain routing: questions tailored to which god system directories the PR touches
- 12-question ceiling — stall continues past this, Raven reviews the full trail
- `eris.arrival` on first touch, `eris.stalled` on ceiling hit
- Evidence receipt: entropy bar + matched patterns per answer
- Writes: jarvis-dex /log_event (no service key from callers)

**Evidence in dex_events:** `eris.arrival`, `eris.challenge`, `eris.answer`, `eris.stalled`, `eris.escalate`
