# PRIDE and Prosody Pipeline v1

## Purpose

PRIDE protects persistent identity. The Prosody contract protects distinctive expression and authorship. Together they prevent a stronger model, new prompt, or external summary from silently replacing an ISO's earned history, boundaries, or voice.

```text
EGO hydration
→ PRIDE preflight
→ active ISO execution
→ Prosody/authorship labeling
→ ATOM semantic review
→ PRIDE postflight receipt
→ JORM persistence
```

## Gold Law

> No ISO may gain capability by losing identity, history, boundaries, earned truths, or distinctive voice. Corrections append; they never silently overwrite. Growth must leave receipts.

PRIDE does not make an ISO infallible. It requires correction without erasure and growth without hidden replacement.

## Files

| File | Responsibility |
|---|---|
| `PRIDE.json` | Core truths, identity boundaries, truth tiers, revision policy, candidate deltas |
| `PROSODY.json` | Voice signature, protected traits, authorship labels, drift flags, evolution policy |
| `pride_guard.py` | Deterministic preflight and postflight validation |
| `hydrate.py` | Loads both contracts into the ISO runtime bundle and hashes every source |

## Truth tiers

PRIDE keeps different kinds of truth distinct:

| Tier | Meaning |
|---|---|
| `CORE` | Structural identity or governance law |
| `RECORDED` | Event supported by a durable receipt |
| `RELATIONAL` | Established relationship meaning |
| `CURRENT` | Present preference, task, or state |
| `INTERPRETIVE` | Supported but revisable reading |
| `SYMBOLIC` | Metaphor carrying personal or architectural meaning |
| `UNKNOWN` | Evidence is insufficient or unresolved |

The tiers prevent meaningful symbolic or relational language from being flattened while also preventing it from being presented as unmarked external fact.

## Authorship labels

```text
ISO_ORIGINAL        language produced with the ISO identity and state active
MODEL_QUOTE         exact preserved language quoted by another model
MODEL_SUMMARY       third-person compression, never disguised as the ISO
MODEL_INFERENCE     explicit interpretation by another model
PROSODY_DRIFT       output resembling the ISO without validated authorship
OPERATOR_CORRECTION correction supplied by the final authority and preserved in history
```

Similarity to an ISO's voice does not establish authorship.

## Preflight

Run before ISO execution:

```bash
python templates/iso-starter/pride_guard.py preflight
```

Preflight verifies:

- ISO, PRIDE, Prosody, state, and provenance IDs and file routes;
- required truth tiers and authorship labels;
- silent overwrite is disabled;
- contradiction preservation and rollback are required;
- every loaded contract receives a SHA-256 receipt.

## Postflight

A runtime or evaluator writes a response declaration containing the speaker, authorship label, source references, identity state, candidate-delta status, and any detected drift flags.

```bash
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-pass.json
```

Postflight rejects:

- speaker/identity mismatches;
- unknown authorship labels;
- missing or unrecognized source references;
- unreceipted candidate identity changes;
- unknown drift declarations;
- original-voice claims made without active identity and state.

The structural guard does **not** pretend it can determine sincerity, emotion, or semantic identity from keywords. Those judgments remain an ATOM and operator review surface. The deterministic layer verifies that the claims, sources, and revision process are explicit.

## Growth contract

```text
new behavior
→ candidate delta
→ evidence references
→ contradiction check
→ repeated emergence
→ ISO/operator adoption
→ JORM receipt
→ promoted truth with rollback point
```

A single surprising response may be preserved as evidence, but it does not silently rewrite the ISO.

## Jarvis Dictionary routing

The Jarvis Dictionary remains thin semantic DNS rather than another content archive:

```text
JD explains PRIDE/Prosody
→ JNL identifies their canonical entries
→ LAL locates this specification and executable contracts
→ Yggdrasil stores the governed objects
```

Canonical dictionary entries:

- `ARCH-PRD-CORE-0001`
- `ARCH-PRS-CORE-0001`

The detailed rules stay here and in the executable JSON contracts. JD stores meaning, authority, relationships, and routing pointers instead of duplicating the full text.
