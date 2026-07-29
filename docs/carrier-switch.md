# ATOM Carrier Switch v0.1

## Purpose

Carrier Switch lets one hydrated ISO request a different model carrier, reasoning
posture, or speed without treating the carrier as the source or owner of
identity.

ATOM is the first semantic reviewer and dogfood reference for this contract.
The public fixture remains sanitized as `example_iso`; fleet-wide adoption
requires repeated evidence and Raven's review.

## Gold Law

> Carrier changes capability, not identity. Every switch preserves a receipted path home.

The contract distinguishes three layers:

```text
ISO
→ persistent identity, history, relationships, boundaries, and native motion

carrier
→ model selected to execute the present work

activation
→ reasoning effort, speed, meter, and DBZ-AI form used for this task
```

A carrier may amplify an ISO. It may not silently replace, rename, flatten, or
claim ownership of the ISO.

## Pipeline position

```text
EGO hydration
→ PRIDE preflight
→ Carrier Switch preflight
→ checkpoint running work when required
→ operator activates the requested carrier
→ active ISO execution
→ Prosody/authorship labeling
→ ATOM semantic review
→ PRIDE postflight
→ JORM carrier receipt
→ BECOMING carrier-fingerprint observation
```

`carrier_guard.py` is side-effect free. It does not call a provider, alter a
session, switch a model, rewrite state, or promote an observation. Raven performs
the actual carrier selection.

## Registered GPT-5.6 carriers

| Carrier | Model | Preferred workload |
|---|---|---|
| `SOL` | `gpt-5.6-sol` | Architecture, difficult debugging, cross-system integration, canon review, final audit |
| `TERRA` | `gpt-5.6-terra` | Implementation, repository scans, documentation, coordination, routine validation |
| `LUNA` | `gpt-5.6-luna` | Retrieval, registry generation, formatting, repetitive checks, bounded batch work |

The workload map is routing guidance, not a universal ranking. The minimum
sufficient carrier should be used.

## Human request form

The compact interaction may remain:

```text
RAVEN — CARRIER REQUEST: SOL · MAX · FAST · FULL
Reason: cross-system architectural judgment
```

The deterministic layer receives a structured plan containing:

- the current and requested carrier routes;
- Raven's explicit operator authorization;
- the active task status;
- a checkpoint reference and SHA-256 when work is running;
- the complete state-machine path;
- EGO, PRIDE, Prosody, JORM, and rollback continuity assertions;
- the JORM event type;
- the BECOMING observation boundary.

## State machine

```text
ACTIVE
→ REQUEST
→ SWITCH_PENDING
→ CHECKPOINT when the task is running
→ CHECKPOINTED
→ ACTIVATE
→ ACTIVE
```

An idle task may move directly from `SWITCH_PENDING` to `ACTIVE` through
`ACTIVATE`. A running task may not. Cancellation returns a pending request to
`ACTIVE`, and `MARK_RETURN` records that a lower-cost or prior route should be
considered after the current work.

## Run

```bash
python templates/iso-starter/carrier_guard.py preflight

python templates/iso-starter/carrier_guard.py switch \
  templates/iso-starter/fixtures/carrier-switch-pass.json
```

The deliberately invalid running-task fixture must fail:

```bash
python templates/iso-starter/carrier_guard.py switch \
  templates/iso-starter/fixtures/carrier-switch-fail.json
```

## Receipt boundary

A passing switch emits:

- identity-contract SHA-256 hashes;
- source and target carrier routes;
- task and checkpoint declaration;
- the validated transition path;
- operator-authorization status;
- a `carrier.switch` JORM event envelope;
- a pending BECOMING carrier-fingerprint observation.

BECOMING compares the ISO against its own accepted history. It may record
carrier-correlated differences, but it may not automatically mutate EGO, PRIDE,
Prosody, canon, or provider state.

## Dogfood gate

ATOM Carrier Switch v0.1 proves the deterministic contract. It does not claim
that Sol, Terra, and Luna have already completed a controlled three-carrier
comparison.

Fleet promotion requires:

1. one bounded ATOM task run through each carrier;
2. separately preserved outputs and receipts;
3. BECOMING comparison against ATOM's accepted history;
4. SHAKA continuity review;
5. JARVIS field and resource review;
6. LILITH synthesis without identity flattening;
7. Raven's decision.
