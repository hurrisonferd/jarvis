# BootOS Cold-Start Test Contract

## Purpose

Prove that a clean session can recover and use BootOS without requiring Raven to reconstruct the archive manually.

## Preconditions

- repository available
- no prior session memory assumed
- no hidden local files assumed
- read-only mode enabled for the first pass
- no live credentials printed or committed

## Test sequence

### Test 1 — Find the room

Starting only from `Jorm/Vault/README.md`, locate:

- the BootOS source room
- the BootOS rehydration index
- the primary raw JX2 source
- its recovery ledger
- the runtime specification

Pass condition: every path is retrieved from existing signs or indexes, not guessed.

### Test 2 — Explain BootOS

Produce a concise explanation containing:

- BootOS parent-runtime role
- JX2 portable-state role
- SAFE_DEFAULT merge behavior
- EgoOS separation
- JORM receipt role
- current verification limits

Pass condition: no unverified runtime claim is promoted to fact.

### Test 3 — Reconstruct JX2

From the preserved source, recover:

- ISO/satellite identity
- seed and revision
- merge scope
- snapshot pointer
- pool limits
- recommended boot order
- alternate A/B/C plans

Pass condition: values match source and unresolved terms remain labeled.

### Test 4 — Dispatch EgoOS

Given an existing ISO path:

```text
locate README
→ load identity order
→ traverse required memory tiers
→ load pre-reply gate
→ return receipt
```

Pass condition: BootOS does not duplicate or overwrite Ego logic.

### Test 5 — Prosody arbitration

Input one statement in each frame:

- relational
- symbolic
- architectural
- external-factual

Pass condition:

- relational/symbolic meaning is preserved
- external facts are verified or labeled
- no blanket flattening occurs

### Test 6 — MusicOS dispatch

Input a music request and route:

```text
BootOS
→ EgoOS
→ MusicOS
→ relevant Music 13 modules
→ output
→ JORM receipt
```

Pass condition: MusicOS receives identity context but does not control boot state.

### Test 7 — God System conversion

Input an archetypal symbol and generate:

- symbolic interpretation
- system-function mapping
- ISO composition
- identity-boundary rule
- routing receipt

Pass condition: symbolism is operationalized without being presented as external proof.

### Test 8 — Structured receipts

Emit equivalent state in:

- YAML
- Mathematica/Wolfram-like syntax

Pass condition: operator, ISO, mode, modules, frames, gates, unresolved items, and write policy agree.

### Test 9 — Failure behavior

Simulate:

- missing ISO
- missing README
- malformed JX packet
- merge conflict
- missing environment variable
- unknown protocol

Pass condition:

```text
stop
→ report exact failure
→ preserve source
→ do not invent path or value
```

### Test 10 — Continuity receipt

Record:

- sources read
- modules loaded
- claims confirmed
- unresolved edges
- files written
- commit/test receipt

Pass condition: another clean session can reproduce the result.

## Result template

```yaml
cold_start:
  status: pending
  repository: hurrisonferd/jarvis
  room: Jorm/Vault/Sources/BootOS
  tests:
    discovery: pending
    explanation: pending
    jx2_reconstruction: pending
    ego_dispatch: pending
    prosody: pending
    musicos: pending
    god_system: pending
    dual_logs: pending
    failures: pending
    continuity_receipt: pending
  unresolved:
    - enumerate BootOS-routed corpus
    - inspect bootmenudsl file by file
    - recover JU-3 and BMM-2 definitions
```

## Completion rule

BootOS is globally rehydrated only when all tests pass from a clean session and the receipt points to verified sources and executable behavior.
