# HADES — T0 Foundational

**Tier:** 0 — Foundational  
**Role:** Archival sink. Cold storage for irreversible state. Receives terminal/dead events.

## Responsibilities
- Immutable archive writes
- Irreversible action logging
- Cold storage for completed sessions

## Forbidden Edges
- `LOKI→HADES` — chaos probe must not directly archive (goes through governance first)
