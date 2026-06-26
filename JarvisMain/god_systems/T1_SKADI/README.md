---
memory_tier: JLTM
grade: system
---

# SKADI — T1 Execution

**Tier:** 1 — Execution  
**Pipeline position:** 5th (executor)  
**Role:** Execution runtime. Invokes tools, writes state, runs actions.

## Responsibilities
- Tool invocation and side effects
- State writes (Supabase, GitHub)
- GRID mutations (via GNPL after P29)

## Pipeline
`KRONOS → SKADI → MNEMOS`  
Parallel input: `BIFROST`

## Forbidden outbound
- `SKADI→AEGIS` — no execution loopback to gate
- `DANTE→SKADI` — post systems cannot re-invoke execution
- `JANUS→SKADI` — transition cannot re-invoke execution
