# World Kernel Spec — P30

## Invariants

The World Kernel is the minimal, immutable contract that all JARVIS components must satisfy.
These invariants cannot be overridden by any patch, agent, or runtime condition.

### Plane Model
| Plane | Role | Mutation allowed |
|-------|------|------------------|
| GitHub | Structure ledger — what is allowed to exist | Via PR only (Raven authority) |
| Supabase | Event ledger — what happened | Append-only (no UPDATE to event rows) |
| GRID | Projection — derived computation | Read-only, recomputed from Supabase |
| TRON | Navigation shell | Read-only, UI projection of GRID |

### Pipeline Invariants
1. `INTENT` must enter via AYRE — no direct injection into later stages
2. `AEGIS` must gate every BUS event before dispatch
3. `SKADI` executes only after ODIN has set `tool_id`
4. `HUGINN` reconciles every session end — no orphan sessions
5. `LOG` (execution_trace insert) is mandatory for every stage transition

### Event Contract
Every event emitted via BUS must have:
- `type`: string
- `patch_id`: Pxx reference
- `stage`: one of AYRE|AEGIS|ODIN|KRONOS|SKADI|MNEMOS|HUGINN
- `correlation_id`: uuid chain

### Consensus Requirements (P29 GNPL)
| Proposal Type | Required Quorum | Blocking Systems |
|--------------|----------------|------------------|
| `tool_execution` | 1 (AEGIS only) | AEGIS |
| `state_transition` | 2 (AEGIS + ODIN) | AEGIS, ODIN |
| `resource_access` | 2 (AEGIS + HALO) | AEGIS, HALO |
| `expansion` | 3 (AEGIS + ODIN + PROMETHEUS) | AEGIS, ODIN, PROMETHEUS |

### Forbidden Topology
- `SKADI → AEGIS` (execution cannot route back to validation)
- `DANTE → SKADI` (post-execution cannot re-enter runtime)
- `JANUS → SKADI` (handoff cannot re-enter runtime)
- `LOKI → HADES` (chaos cannot enter terminus)

### Gold Law Reference
See `architecture/constraints.md` for GL1–GL9 definitions.
GL7 SUPREME governs all expansion decisions.

## Kernel Version
`world_kernel_version: 1.0`
`authority: Raven (John Barber)`
`effective: 2026-05-28`
