# JANUS — T4 Observability

**Tier:** 4 — Observability  
**Role:** Transition handler. Manages mode switches and system handoffs.

## Responsibilities
- Mode transition management
- Handoff coordination between agents
- State boundary enforcement

## Forbidden outbound
- `JANUS→SKADI` — transitions cannot invoke execution directly
