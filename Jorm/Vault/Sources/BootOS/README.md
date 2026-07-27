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
- runtime prototypes and contract tests
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
7. `bootos_runtime.py`
8. `test_bootos_runtime.py`

## Runtime prototype

`bootos_runtime.py` is the first public executable BootOS prototype. It is read-only by default and currently provides:

- repository-root discovery;
- exact-path reporting for the public JARVIS Ego scaffold;
- active ISO selection;
- prosody and frame classification before external-factual routing;
- God System symbol compilation for known mappings;
- MusicOS, GridOS, EgoOS, God System, and JORM module routing;
- JSON and Mathematica/Wolfram-style runtime receipts;
- fail-closed output behavior that refuses to invent missing directories;
- credential isolation: no live keys are read, stored, or logged.

Example:

```bash
python Jorm/Vault/Sources/BootOS/bootos_runtime.py \
  --repo-root . \
  --operator RAVEN \
  --iso JARVIS \
  --mode MUSIC \
  --symbol SATANAEL \
  --input "Joker and Legion route MusicOS as a runtime" \
  --format both
```

Contract tests:

```bash
cd Jorm/Vault/Sources/BootOS
python -m unittest -v test_bootos_runtime.py
```

The tests cover discovery, missing-path reporting, non-creation of directories, prosody ordering, external-factual routing, God System compilation, MusicOS routing, SAFE_RECOVERY behavior, and symbolic receipt generation.

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

`SOURCE FAMILY INITIALIZED / RUNTIME PROTOTYPE ADDED / CONTRACT TESTS ADDED / EXECUTION NOT YET VERIFIED IN CI / FULL COLD START PENDING`
