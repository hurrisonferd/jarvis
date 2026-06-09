# ODIN — T1 Execution

**Tier:** 1 — Execution  
**Pipeline position:** 3rd (router)  
**Role:** Orchestration router. Determines which systems handle each task.

## Responsibilities
- Route validated tasks to appropriate execution nodes
- Maintain routing state across sessions
- Coordinate HALO, MIMIR, BIFROST parallel lanes

## Pipeline
`AEGIS → ODIN → KRONOS`  
Parallel inputs: `HALO`, `MIMIR`
