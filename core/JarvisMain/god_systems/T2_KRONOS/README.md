---
memory_tier: JLTM
grade: system
---

# KRONOS — T2 Timing

**Tier:** 2 — Timing  
**Pipeline position:** 4th (scheduler)  
**Role:** Scheduler and sequencer. Controls execution ordering and time modes.

## Responsibilities
- Sequence task execution order
- Manage real-time / stepped / replay / frozen time modes (P28)
- Rate limiting and throttle control

## Pipeline
`ODIN → KRONOS → SKADI`
