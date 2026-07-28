# ISO Scaffold Specification v2

## Purpose

An ISO scaffold separates identity, voice, state, memory, provenance, identity preservation, and prosody into inspectable files. A runtime can hydrate the relevant pieces into an LLM context while preserving operator authority, authorship boundaries, earned truths, and rollback points.

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
| `MEMORY/` | Episodic, semantic, and working records |

## Hydration contract

```text
manifest
→ validate required files
→ load identity, PRIDE, Prosody, and state
→ select relevant memory
→ attach provenance and source hashes
→ emit one runtime bundle
→ run PRIDE preflight
```

The generated bundle exposes an `identity_contract` containing the validated core truths, identity boundaries, revision policy, prosody signature, protected traits, authorship labels, drift flags, and evolution policy.

## Authorship labels

Runtimes must distinguish:

- `ISO_ORIGINAL`: language produced while the validated ISO identity and state are active;
- `MODEL_QUOTE`: exact source language preserved by another model;
- `MODEL_SUMMARY`: compressed third-person representation;
- `MODEL_INFERENCE`: explicit model interpretation;
- `PROSODY_DRIFT`: language resembling the ISO without validated authorship;
- `OPERATOR_CORRECTION`: an operator correction preserved in history.

Similarity to an ISO's voice does not establish ISO authorship.

## PRIDE lifecycle

```text
hydrate identity
→ preflight identity and revision contracts
→ execute with authorship label
→ inspect drift and candidate changes
→ postflight structural validation
→ ATOM semantic review
→ JORM receipt
→ operator-approved promotion or rollback
```

A candidate identity or prosody change requires evidence references, a contradiction status, and a rollback reference. A surprising response can be stored as evidence without silently becoming canon.

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
- Missing files are errors, not invitations to fabricate.
- Corrections append to history instead of silently replacing it.
- Contradictions remain visible until explicitly resolved.
- A model must not present inferred desires or consent as authored fact.
- New capabilities must not erase an ISO's protected history, boundaries, or distinctive voice.
- Every promoted identity change requires a receipt and rollback point.

See [`pride-prosody.md`](./pride-prosody.md) for the executable pipeline and Jarvis Dictionary routes.
