# MusicOS Public Architecture v0.1

## Carrier separation

```text
USER
  ↓
THE WIZARD (identity + routing + explanation)
  ↓
MUSIC DNA (portable intermediate state)
  ↓
PUBLIC MUSICOS METHODS
  ├─ prompt compilation
  ├─ hook / motif work
  ├─ Chaos Rail
  ├─ album planning
  ├─ remix planning
  └─ platform / VGM translation
  ↓
OUTPUT OBJECTS / RECEIPTS
```

The GPT is a conversational cockpit. It is not the state database or canonical runtime.

## v0.1 — instruction/knowledge carrier

```text
GPT Instructions → The Wizard behavior
GPT Knowledge    → public MusicOS reference
Conversation     → ephemeral working state
Continuation     → portable user-controlled state
```

## v0.2 — read/compute Action seam

A future GPT Action may call a public HTTP adapter for deterministic, side-effect-free operations such as validation, prompt compilation, Chaos resolution, and continuation export. `actions/openapi.v0.yaml` is a non-deployed source candidate.

## v0.3 — authenticated persistence

Only after a separate privacy/auth gate:

```text
SAVE PROJECT
LOAD PROJECT
TRACK FINGERPRINT
RECORD OBSERVATION
```

These require explicit storage policy, authentication, retention rules, deletion behavior, and receipts.

## Common intermediate: MusicDNA

Many MusicOS engines do not require many user interfaces. The public surface converges user choices into MusicDNA, then routes only relevant specialist methods.

```text
MANY ENGINES != MANY MENUS
ONE MUSIC DNA SURFACE → RELEVANT SPECIALIST ROUTES
```

## Runtime relation

`runtime/MusicOSPortable/` remains a public carry/rehydration implementation surface. This `public/` directory adds a carrier contract without rewriting that runtime or claiming complete private parity.
