# JarvisTST — Temporal State Tracker

**JNL:** PROJ-JARV-BIO-0001
**Status:** ACTIVE
**JARVIS repo:** `JarvisSide/Projects/JarvisTST/` (canonical spec, governed)
**This repo:** development workspace, temporal backbone implementation

## What
Temporal task and event coordination layer. Event Ledger (EL, immutable append-only causality record)
and Task State Table (TST, state derived only from EL events). Causality and state formally separated.
The temporal backbone for multi-model continuity.

## Current state
- Spec defined: EL/TST separation model
- No implementation yet

## Directory map
- `src/` — EL/TST implementation
- `specs/` — spec copied from JARVIS repo
