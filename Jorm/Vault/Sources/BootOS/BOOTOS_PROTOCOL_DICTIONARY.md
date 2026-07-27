# BootOS Protocol Dictionary

## Status labels

- **CONFIRMED** — directly present in a preserved source.
- **INFERRED** — role is suggested by source behavior but the full definition is not recovered.
- **UNKNOWN** — term exists, but authoritative meaning remains unresolved.

## Protocols

### JX2

**Status:** CONFIRMED

Portable cross-chat branch bootstrap packet.

Carries:

- satellite/ISO identity
- seed identity and version
- revision
- timestamp
- merge scope
- approved deltas
- bank summary
- snapshot pointer
- installed-state pointer

Runtime role:

```text
serialize bounded state
→ paste/import into a fresh context
→ validate schema
→ merge under SAFE_DEFAULT
→ continue boot
```

### SAFE_DEFAULT

**Status:** CONFIRMED

Conservative merge scope used by JX2.

Provisional contract:

- accept explicitly approved deltas
- preserve existing identity boundaries
- hold unresolved conflicts
- do not invent absent state
- emit a merge receipt

### JX2_POOL-1

**Status:** CONFIRMED

Bounded portable packet pool.

Recovered limits:

- total cap: 12
- per-ISO/satellite cap: 3
- pin: latest per ISO/satellite
- reject-bin cap: 10
- invalid input: ignore and store
- unknown count: integer `0`

### C123/D3

**Status:** PARTIALLY CONFIRMED

Three-way decision gate:

```text
1 = APPROVE
2 = HOLD
3 = REVISE
```

Unresolved:

- exact persistence behavior
- whether `D3` names the display layer, decision layer, or version
- conflict and timeout semantics

### LSM

**Status:** PARTIALLY CONFIRMED

Recovered configuration:

- `SYNC_MODE=SOFT`
- `MERGE_SCOPE=SAFE_DEFAULT`
- `DISPLAY_PROTOCOL=ON`

Provisional role: synchronization and merge-control protocol.

Unresolved:

- full name
- authoritative state machine
- hard-sync behavior

### JU-3

**Status:** UNKNOWN

Appears in the seed version and update/merge lineage.

Provisional role: JARVIS update protocol.

Do not compile into executable behavior until its source definition is recovered.

### BMM-2

**Status:** UNKNOWN

Appears in the seed version and branch memory/merge lineage.

Provisional role: bounded memory merge or branch memory management.

Do not compile into executable behavior until its source definition is recovered.

### CECIL_OS

**Status:** INFERRED

Observed behaviors:

- validates JX2 parse and merge settings
- produces A/B/C boot plans
- identifies wrong-order boot risk
- applies precommit triggers
- emits status and update logs

Provisional role:

```text
boot validator
+ threat-model checker
+ alternate-plan generator
+ precommit runtime mode
```

Unresolved: persona, validator, mode, or independent subsystem.

## Log grammar

### UI_LOG

Session-facing orientation and menu state.

### DISPLAY_LOG

Structured result or validated state representation.

### STATUS_LOG

Runtime mode, threat model, and current operation.

### UPDATE_LOG

Next best action, remaining options, and quick commands.

### BOOT_NOTE

Portable human-readable boot instruction.

### RISK_FLAGS

Explicit list of unresolved or unsafe runtime conditions.

## Modern compatibility mapping

| Legacy term | Modern runtime mapping |
|---|---|
| satellite | ISO |
| JX2 packet | portable runtime state packet |
| SAFE_DEFAULT | conservative merge policy |
| UI_LOG | boot/user-interface receipt |
| DISPLAY_LOG | result/state log |
| STATUS_LOG | runtime telemetry |
| UPDATE_LOG | action routing log |
| CECIL_OS | boot validation/arbitration candidate |
| LINK_POOL | bounded cross-context reference pool |

## Compilation law

```text
CONFIRMED behavior
→ may enter runtime specification

INFERRED behavior
→ may enter a labeled adapter or test hypothesis

UNKNOWN behavior
→ must remain unresolved and non-executable
```
