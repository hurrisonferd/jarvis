# Governance — Architecture & Law

The substrate of a mind with values. Not bureaucracy: every pipeline stage is how
JARVIS thinks; every Gold Law is a character commitment. (Canon: CLAUDE.md +
`chaos/chaos_seed.json`. Historical detail: `JarvisBrief`.)

## Gold Law (hard constraints)
- **GL7 supreme** — no expansion without simplification (`reduces_complexity=true`, `overlap_score_below=0.40`).
- **GL2** — no autonomous self-modification. JARVIS proposes, Raven commits.
- **GL5** — no silent state mutation. Every change emits an event and is logged.
- **GL6** — no unvalidated execution. AEGIS gates all high-risk actions.
- Raven is final authority on all decisions.

## The 27 God Systems (fixed — do not redefine/renumber/add)
| Tier | Systems | Role |
|------|---------|------|
| T0 | CHAOS, ZEUS, POSEIDON, HADES | Foundational |
| T1 | AYRE, AEGIS, ODIN, SKADI, ERIS | Execution / guardian |
| T2 | KRONOS | Timing |
| T3 | MNEMOS, HUGINN, HALO, MIMIR | Memory |
| T4 | BIFROST, JANUS | Observability |
| T5 | LOKI, ATHENA, PROMETHEUS, ARGUS, NEMESIS | Governance |
| T6 | IRIS, MERIDIAN | Integrity |
| T7 | DANTE, APOLLO | Interface |
| T8 | ATLAS | Infrastructure |
| T9 | HERMES | Translation |

## Core pipeline
`AYRE → AEGIS → ODIN → KRONOS → SKADI → MNEMOS → HUGINN`
Parallel: HALO, MIMIR, BIFROST. Forbidden edges: SKADI→AEGIS, DANTE→SKADI, JANUS→SKADI, LOKI→HADES.

## Live realization (the companion's actual code)
- **ODIN** — `jarvis-respond/router.ts` classifies each turn's intent → god systems.
- **AEGIS** — `aegis.ts` gates capabilities: read PASS, write/external held for Raven, destructive/self-mod refused.
- **SKADI** — `execute.ts` runs AEGIS-cleared writes (MNEMOS commits).
- **MNEMOS** — `recall.ts` + pgvector semantic recall over the memory ledger.

## Truth layers
- **GitHub** — canonical, append-only ledger (code, decisions, the record).
- **Supabase** — live event spine + `mnemos_memories` (pgvector recall).
- **Cloud-first only.** The GameBoy UI is a monitor of the system, not JARVIS.
