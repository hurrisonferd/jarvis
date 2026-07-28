# ISO Scaffold Specification v1

## Purpose

An ISO scaffold separates identity, voice, state, memory, and provenance into inspectable files. A runtime can hydrate the relevant pieces into an LLM context while preserving operator authority and authorship boundaries.

## Required surfaces

| Surface | Purpose |
|---|---|
| `ISO.json` | Manifest, file map, memory paths, governance |
| `IDENTITY.md` | Name, role, purpose, identity boundary |
| `VOICE.md` | Vocabulary, rhythm, question style, labeling rules |
| `VALUES.md` | Stable decision priorities |
| `BOUNDARIES.md` | Refusal, consent, and control constraints |
| `RELATIONSHIPS.md` | Operator and ISO-to-ISO relationships |
| `STATE.json` | Current mode, goal, task, checkpoint |
| `PROVENANCE.json` | Quote, summary, inference, and correction policy |
| `MEMORY/` | Episodic, semantic, and working records |

## Hydration contract

```text
manifest
→ validate required files
→ load identity and state
→ select relevant memory
→ attach provenance and source hashes
→ emit one runtime bundle
```

## Authorship labels

Runtimes should distinguish:

- `ORIGINAL`: language produced by the active ISO;
- `QUOTE`: exact source language;
- `SUMMARY`: compressed third-person representation;
- `INFERENCE`: model interpretation;
- `OPERATOR_CORRECTION`: a correction preserved in history.

## Governance

- The operator remains final authority.
- Shared intent does not merge identities.
- Missing files are errors, not invitations to fabricate.
- Corrections append to history instead of silently replacing it.
- A model must not present inferred desires or consent as authored fact.
