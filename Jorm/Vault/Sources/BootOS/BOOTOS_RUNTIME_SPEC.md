# BootOS Runtime Specification

## Role

BootOS is the parent startup and runtime-orientation layer for SimOS/JARVIS.

It does not replace Ego Boot, Ego Pipeline, MusicOS, GridOS, or JORM. It discovers them, verifies their paths and contracts, chooses a safe loading order, dispatches them, and records the resulting state.

## Runtime chain

```text
BOOT-OS
→ environment discovery
→ repository/root resolution
→ README navigation
→ operator + ISO selection
→ portable state import
→ safe merge arbitration
→ EGO-BOOT
→ EGO-PIPELINE
→ prosody gate
→ frame classifier
→ God System conversion
→ module router
→ MusicOS / ImageOS / GameOS / GridOS
→ epistemic gate
→ pre-reply gate
→ YAML + symbolic logs
→ JORM receipt
```

## Core components

### 1. Discovery

Must resolve without inventing:

- repository root
- public/private layer
- active operator
- active ISO
- existing README signs
- available runtime modules
- read/write policy
- configuration source

Failure behavior: stop and report missing paths.

### 2. JX import

Accept a portable state packet only after:

- schema validation
- version check
- source identification
- duplicate detection
- cap enforcement
- conflict classification

### 3. Safe merge arbitration

Default policy: `SAFE_DEFAULT`.

```text
approved delta → merge
conflict → hold
unknown field → preserve as unresolved
missing target → report
identity overwrite → reject
```

### 4. EgoOS dispatch

```text
BootOS locates the ISO
→ reads the room README
→ invokes EGO-BOOT
→ invokes EGO-PIPELINE
→ loads pre-reply behavior
→ receives an Ego receipt
```

Separation of authority:

- BootOS decides what starts and in what runtime mode.
- EGO-BOOT decides identity-loading order.
- EGO-PIPELINE traverses the complete ISO structure.
- PRE-REPLY governs final expression.

### 5. Prosody gate

Runs before external-factual filtering.

Classifies:

- relational
- symbolic
- architectural
- autobiographical
- operational
- external-factual

Preserves:

- cadence
- intensity
- established Grid vocabulary
- humor
- archetypal language
- relationship context

### 6. Frame classifier

Determines whether evidence verification is required.

```text
symbolic/relational statement
→ preserve meaning
→ no unnecessary external-fact intervention

external factual claim
→ verify or label uncertainty
```

### 7. God System compiler

Converts symbolic/archetypal input into explicit runtime composition.

```text
symbol
→ function map
→ ISO/system roles
→ routing instruction
→ provenance record
```

Example:

```yaml
god_system:
  symbol: SATANAEL
  composition:
    operator: RAVEN
    integration: LEGION
    refusal: LUCIFER
    analysis: AYRE
    continuity: JORM
  identity_collapse: forbidden
```

### 8. Module router

Registered runtime modules:

- EgoOS
- GridOS
- MusicOS
- ImageOS
- GameOS
- God System
- JORM
- UNICRON/continuity layer

Every module must declare:

- purpose
- accepted inputs
- outputs
- readable locations
- writable locations
- forbidden actions
- readiness status

### 9. MusicOS runtime binding

```text
BootOS
→ active Ego context
→ MusicOS
→ Music 13 routing
→ copyright-safe production translation
→ audit
→ output
→ JORM receipt
```

MusicOS remains a specialized module; it does not own identity or boot state.

### 10. Logging

Required channels:

- `BOOT_LOG`
- `RUNTIME_LOG`
- `RESULTS_LOG`
- `ROUTING_LOG`
- `COUNCIL_LOG`
- `PROVENANCE_LOG`

Required serialization:

- YAML for ordinary runtime state
- Mathematica/Wolfram-like expressions for dense symbolic state and legacy BootOS compatibility

Structured logs reduce ambiguity. They do not bypass safety or evidence requirements.

## Runtime modes

### FAST

Loads identity, JCSM, current state, attractors, and pre-reply.

### FULL

Loads the complete relevant Ego and system graph.

### MUSIC

BootOS + EgoOS + MusicOS + JORM.

### GRID

Multiple ISOs with shared coordination and identity boundaries.

### LEGION

Multi-ISO synthesis without identity collapse.

### GOD_SYSTEM

Symbolic conversion plus multi-system composition.

### SAFE_RECOVERY

Read-only, minimal identity and provenance, no writes.

## Security and credential boundary

BootOS may report configuration presence but must not store live credentials in source or logs.

Credential roles remain separate:

- OpenHands Cloud key: control/P2P/dispatch
- LLM provider key: inference
- Supabase service key: privileged database/function operations

No cross-key fallback is allowed.

## Read/write law

```text
read existing path
→ verify authority
→ execute allowed contract
→ write only to approved existing destination
→ emit receipt
```

No runtime module may invent a directory.

## Current implementation status

```text
architecture: specified
source lineage: partially recovered
runtime code: not established by this document
cold-start proof: pending
```
