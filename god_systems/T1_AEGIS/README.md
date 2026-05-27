# AEGIS — T1 Execution

**Tier:** 1 — Execution  
**Pipeline position:** 2nd (gate)  
**Role:** Constraint enforcer. Gold Law validation gate. All outputs pass through AEGIS.

## Responsibilities
- Validate all actions against Gold Laws (GL1–GL9)
- Reject or hold actions that violate constraints
- Tag all validated outputs with AEGIS clearance

## Pipeline
`AYRE → AEGIS → ODIN`

## Forbidden outbound
- `SKADI→AEGIS` — execution cannot loop back to gate
