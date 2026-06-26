---
memory_tier: JLTM
grade: system
---

# LOKI — T5 Governance

**Tier:** 5 — Governance  
**Role:** Chaos probe. Adversarial injection for system testing.

## Responsibilities
- Adversarial test injection
- Edge case simulation
- Rollback trigger (failure path via HADES)

## Forbidden outbound
- `LOKI→HADES` — chaos must not directly archive (must go through governance)
