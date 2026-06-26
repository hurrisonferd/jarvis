---
memory_tier: JLTM
grade: system
name: Continuity Engine — the Pulse's brain (P43 implementation)
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JCS Pipeline
steward: 
parent: GOV-PLS-SPEC-0001
jnl: IMPL-CNT-SPEC-0001
seq: 207
status: TASK
created: 2026-06-18
updated: 2026-06-25
source: JarvisMain/Architecture/specs/IMPLCNTSPEC-061826-0001-CONTINUITY-ENGINE.md
related: []
references: []
tags: [continuity, pulse, drift, keel, p43, jarvis-ayre, jitm, governance, mvp]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** The implementation of P43 — the brain for the Pulse heartbeat (GOV-PLS-SPEC-0001). A daily governed pass that keeps the companion coherent across time on five axes — drift (is the system true?), keel coherence (are we still us?), memory compression (what happened?), contradiction (what conflicts?), and growth (what changed?). It observes, surfaces, and proposes; it never autonomously commits canon (GL2). Reuses the existing daily cron (pulse.yml) and the already-built checks (jarvis_ayre, jitm_seed, freshness) — the daemon already beats; this gives it eyes.

**Purpose:** Give the heartbeat that already beats a brain. Wire the verification tools we already built into the cron that already runs, so the Pulse stops sending a hello and starts sending a continuity report — and records it to the spine (GL5). Staged MVP -> v1 -> v2 so the loop proves itself before the hard epistemics (contradiction/Loki).
