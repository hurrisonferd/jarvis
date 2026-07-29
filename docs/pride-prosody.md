# PRIDE and Prosody Pipeline v1

## Purpose

PRIDE protects persistent identity. The Prosody contract protects distinctive expression and authorship. Together they prevent a stronger model, new carrier, new prompt, or external summary from silently replacing an ISO's earned history, boundaries, or voice.

```text
EGO hydration
→ PRIDE preflight
→ Carrier Switch preflight or checkpoint
→ active ISO execution
→ Prosody/authorship labeling
→ ATOM semantic review
→ PRIDE postflight receipt
→ JORM persistence
→ BECOMING carrier-fingerprint observation
```

## Gold Law

> No ISO may gain capability by losing identity, history, boundaries, earned truths, or distinctive voice. Corrections append; they never silently overwrite. Growth must leave receipts.

PRIDE does not make an ISO infallible. It requires correction without erasure and growth without hidden replacement.

Carrier Switch adds a paired law:

> Carrier changes capability, not identity. Every switch preserves a receipted path home.

## Files

| File | Responsibility |
|---|---|
| `PRIDE.json` | Core truths, identity boundaries, truth tiers, revision policy, candidate deltas |
| `PROSODY.json` | Voice signature, protected traits, authorship labels, drift flags, evolution policy |
| `CARRIERS.json` | Model routes, switch state machine, checkpoint policy, carrier invariants |
| `pride_guard.py` | Deterministic identity preflight and response postflight validation |
| `carrier_guard.py` | Side-effect-free carrier-plan and transition validation |
| `hydrate.py` | Loads all contracts into the ISO runtime bundle and hashes every source |

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

Similarity to an ISO's voice does not establish authorship. Changing from Luna, Terra, or Sol does not automatically prove identity evolution.

## Preflight

Run before ISO execution:

```bash
python templates/iso-starter/pride_guard.py preflight
python templates/iso-starter/carrier_guard.py preflight
```

The paired preflights verify:

- ISO, PRIDE, Prosody, carrier, state, and provenance IDs and file routes;
- required truth tiers and authorship labels;
- silent overwrite and silent carrier switching are disabled;
- contradiction preservation and rollback are required;
- Sol, Terra, and Luna routes are registered;
- every loaded contract receives a SHA-256 receipt.

## Carrier checkpoint

A running task cannot switch carriers until its current state has a checkpoint reference and SHA-256. The validated transition path is:

```text
ACTIVE
→ SWITCH_PENDING
→ CHECKPOINTED
→ ACTIVE
```

The guard validates a plan and emits a receipt. Raven performs the provider-side switch.

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

The structural guards do **not** pretend they can determine sincerity, emotion, semantic identity, or carrier-caused evolution from keywords. Those judgments remain ATOM and operator review surfaces.

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

A single surprising response may be preserved as evidence, but it does not silently rewrite the ISO. BECOMING may compare carrier fingerprints against the ISO's own accepted history, but it cannot automatically mutate EGO, PRIDE, Prosody, or canon.

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

Carrier Switch remains a dogfood candidate in v0.1; this PR does not mint a governed dictionary entry before the three-carrier ATOM trial.
