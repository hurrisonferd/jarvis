---
memory_tier: JLTM
grade: system
---

# ORACLE — T1 Execution

> Renamed from AYRE → ORACLE (Raven-sanctioned 2026-06-14) to end the name collision
> with the AYRE companion stream. Address held stable at `GS-AYR-CORE-0001` (JMS law).


**Tier:** 1 — Execution  
**Pipeline position:** 1st (entry point)  
**Role:** Intake and intent parsing. First node to receive all inputs.

## Responsibilities
- Parse incoming requests from all agents and users
- Classify intent and route to AEGIS
- Tag inputs with session context

## Pipeline
`ORACLE → AEGIS`
