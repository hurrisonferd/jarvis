---
memory_tier: JLTM
grade: system
---

# HALO — T3 Memory (Parallel)

**Tier:** 3 — Memory  
**Lane:** Parallel (always-on observer)  
**Role:** Ambient monitoring. Passively observes all system activity without blocking.

## Responsibilities
- Background state observation
- Anomaly flagging without intervention
- Feed alerts to HUGINN and NEMESIS

## Pipeline
`HALO → ODIN` (parallel input lane)
