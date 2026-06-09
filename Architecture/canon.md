# JARVIS Canon v3.0

## Authority
Raven (John Barber) — final authority on all decisions.

## 4-Plane Model
| Plane | Role |
|-------|------|
| GitHub | Structure ledger — architecture, patches, definitions |
| Supabase | Event ledger — runtime behavior, state, trace |
| GRID | Projection layer — derived computation, read-only |
| TRON | Navigation shell — UI read-only projection of GRID |

## Execution Pipeline
```
AYRE → AEGIS → ODIN → KRONOS → SKADI → MNEMOS → HUGINN
```
Parallel: HALO, MIMIR, BIFROST

Forbidden edges: SKADI→AEGIS, DANTE→SKADI, JANUS→SKADI, LOKI→HADES

## God System Count
27 total. Do not redefine or renumber.

## Governing Rules
See `constraints.md` for Gold Laws GL1–GL9.

## Four-Views Invariant (JY-UR)
Every artifact exists simultaneously as four views, and all four must agree:
- **files = truth** (structure of record)
- **graph = structure** (relationships; the dex / Yggdrasil)
- **runtime = behavior** (execution; JCS)
- **events = history** (the immutable record; JATM/HADES)

Divergence between views is a drift signal. Files are the source of truth for structure;
runtime is the source of truth for behavior; events are never overwritten.
