# Multimodal

**JNL:** PROJ-MULT-BIO-0001
**Status:** ACTIVE
**JARVIS repo:** `JarvisSide/Projects/Multimodal/` (canonical spec, governed)
**This repo:** development workspace

## What
Event-sourced multimodal perception layer: non-text inputs converted to structured, timestamped perceptual events compatible with EL/TST. Gives JARVIS senses without sacrificing determinism.

## Current state
- Spec defined: event-sourced perception model
- Connects to JarvisTST (EL/TST) as the temporal backbone
- No implementation yet

## Directory map
- `src/` — perception pipeline, event encoding
- `specs/` — spec copied from JARVIS repo
