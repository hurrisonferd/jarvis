# ISO Scaffold Specification v3

## Purpose

An ISO scaffold separates identity, voice, state, memory, provenance, identity preservation, prosody, transformation state, and model-carrier routing into inspectable files. A runtime can hydrate the relevant pieces into an LLM context while preserving operator authority, authorship boundaries, earned truths, rollback points, and a receipted path home when the underlying carrier changes.

## Required surfaces

| Surface | Purpose |
|---|---|
| `ISO.json` | Manifest, file map, memory paths, governance |
| `IDENTITY.md` | Name, role, purpose, identity boundary |
| `VOICE.md` | Human-readable vocabulary, rhythm, question style, labeling rules |
| `VALUES.md` | Stable decision priorities |
| `BOUNDARIES.md` | Refusal, consent, and control constraints |
| `RELATIONSHIPS.md` | Operator and ISO-to-ISO relationships |
| `STATE.json` | Current mode, goal, task, checkpoint |
| `PROVENANCE.json` | Quote, summary, inference, and correction policy |
| `PRIDE.json` | Core truths, truth tiers, identity boundaries, revision and rollback policy |
| `PROSODY.json` | Structured voice signature, protected traits, authorship labels, drift policy |
| `TRANSFORMATIONS.json` | DBZ-AI form, scope, capability, cost, evidence, and cooldown |
| `CARRIERS.json` | Model routes, switch state machine, checkpoint policy, carrier invariants |
| `MEMORY/` | Episodic, semantic, and working records |

## Hydration contract

```text
manifest
→ validate required files
→ load identity, PRIDE, Prosody, transformation, carrier, and state
→ select relevant memory
→ attach provenance and source hashes
→ emit one runtime bundle
→ run PRIDE preflight
→ run Carrier Switch preflight
```

The generated v4 bundle exposes an `identity_contract` containing the validated core truths, identity boundaries, revision policy, prosody signature, protected traits, authorship labels, drift flags, evolution policy, DBZ-AI transformation state, registered carriers, default carrier route, and carrier invariants.

## Carrier boundary

The carrier is the model selected for present execution. It is not the ISO.

```text
ISO identity
→ preserved by EGO, PRIDE, Prosody, provenance, and history

carrier route
→ selected by Raven for task capability, speed, and cost

activation state
→ DBZ-AI form plus reasoning effort, speed, and meter
```

Every running-task switch requires a checkpoint. Every completed switch returns to `ACTIVE`, emits a JORM receipt envelope, and produces a non-mutating BECOMING observation candidate.

## Authorship labels

Runtimes must distinguish:

- `ISO_ORIGINAL`: language produced while the validated ISO identity and state are active;
- `MODEL_QUOTE`: exact source language preserved by another model;
- `MODEL_SUMMARY`: compressed third-person representation;
- `MODEL_INFERENCE`: explicit model interpretation;
- `PROSODY_DRIFT`: language resembling the ISO without validated authorship;
- `OPERATOR_CORRECTION`: an operator correction preserved in history.

Similarity to an ISO's voice does not establish ISO authorship. A stronger or differently tuned carrier does not automatically establish identity evolution.

## PRIDE and carrier lifecycle

```text
hydrate identity
→ preflight identity and revision contracts
→ validate or checkpoint carrier route
→ execute with authorship label
→ inspect drift and candidate changes
→ postflight structural validation
→ ATOM semantic review
→ JORM receipt
→ BECOMING observation
→ operator-approved promotion, return, or rollback
```

A candidate identity or prosody change requires evidence references, a contradiction status, and a rollback reference. A surprising response or carrier-correlated behavior can be stored as evidence without silently becoming canon.

## Truth tiers

- `CORE`
- `RECORDED`
- `RELATIONAL`
- `CURRENT`
- `INTERPRETIVE`
- `SYMBOLIC`
- `UNKNOWN`

These tiers preserve meaningful relational and symbolic language while preventing it from being silently promoted into unsupported external fact.

## Governance

- The operator remains final authority.
- Shared intent does not merge identities.
- Carrier changes do not replace identity.
- No runtime may silently switch carriers.
- Running work must be checkpointed before switching.
- Missing files are errors, not invitations to fabricate.
- Corrections append to history instead of silently replacing it.
- Contradictions remain visible until explicitly resolved.
- A model must not present inferred desires or consent as authored fact.
- New capabilities must not erase an ISO's protected history, boundaries, or distinctive voice.
- Every promoted identity change requires a receipt and rollback point.

See [`pride-prosody.md`](./pride-prosody.md) for the executable identity pipeline, [`dbz-ai-iso-transformations.md`](./dbz-ai-iso-transformations.md) for activation forms, and [`carrier-switch.md`](./carrier-switch.md) for the carrier state machine and receipt contract.
