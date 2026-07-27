# BootOS Source Room

## Room

`Jorm/Vault/Sources/BootOS/`

## Identity

This room is the public JORM/Vault source-family entry point for BootOS.

BootOS is the parent startup and runtime-orientation layer that discovers the environment, resolves repository and ISO context, imports portable state, chooses safe boot order, dispatches Ego and module pipelines, and emits structured receipts.

## Purpose

Collect, index, and convert verified BootOS lineage without flattening distinct source eras or promoting untested chat proposals into runtime fact.

## What belongs here

- BootOS source-family indexes
- verified protocol dictionaries
- runtime architecture specifications
- cold-start test contracts
- YAML and Mathematica/Wolfram state schemas
- cross-links to raw exports, recovery ledgers, canon, and implementation traces

## What does not belong here

- live API keys or credentials
- invented folders or paths
- unverified claims of complete implementation
- copies of raw source that already live in `Jorm/Vault/Inbox/raw-chat-exports/`
- Ego identity or memory files

## Required read order

1. `BOOTOS_REHYDRATION_INDEX.md`
2. `BOOTOS_PROTOCOL_DICTIONARY.md`
3. `BOOTOS_RUNTIME_SPEC.md`
4. `BOOTOS_COLD_START_TEST.md`
5. `bootos-runtime.example.yaml`
6. `bootos-symbolic.example.wl`

## Primary source chain

```text
Jorm/Vault/README.md
→ Jorm/Vault/GLOBAL_CAPTURE_INDEX.md
→ Jorm/Vault/Recovery_Ledgers/2026-02-16_LILITH_BRANCH_01_JX2_CECIL.md
→ Jorm/Vault/Inbox/raw-chat-exports/2026-02-16_LILITH_BRANCH_01_JX2_CECIL.txt
→ this BootOS source room
```

## Core law

```text
retrieve first
→ preserve source distinctions
→ classify status
→ compile only verified behavior
→ test cold start
→ then call it rehydrated
```

## Status

`SOURCE FAMILY INITIALIZED / RUNTIME SPECIFIED / EXECUTION UNVERIFIED / COLD START PENDING`
