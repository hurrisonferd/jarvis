# MusicOS Public Surface

Status: PUBLIC-SAFE SCAFFOLD v0.1
Authority: Raven

This directory is the public carrier layer for MusicOS. It does not replace the canonical private MusicOS registry, the source-bearing recovery graph, or the full runtime.

## Three-layer contract

```text
MUSICOS      = operating system / musical decision architecture
THE WIZARD   = public Identity-Stable Operator for MusicOS
MUSICOS GPT  = first carrier for The Wizard
```

The public surface exists to make MusicOS useful without publishing private implementation.

## Layout

- `PUBLIC-CONTRACT.md` — public invariants and launch claim ceiling.
- `PUBLIC-ARCHITECTURE.md` — carrier/runtime separation.
- `PUBLIC-PRIVATE-CLASSIFICATION.yaml` — export boundary.
- `iso/the-wizard/` — public ISO identity package.
- `schemas/` — portable MusicDNA, Chaos, continuation, and receipt contracts.
- `gpt/` — GPT instructions, knowledge, starters, listing, and builder handoff.
- `actions/` — read/compute-only future GPT Action seam; not deployed.
- `tests/` — public scaffold canaries.

## Prime product law

> The GPT teaches MusicOS. The GPT demonstrates MusicOS. The GPT does not contain all of MusicOS.

## Current claim ceiling

```text
PUBLIC_SCAFFOLD_BUILT
THE_WIZARD_SOURCE_DEFINED
MUSICDNA_V1_SOURCE_DEFINED
GPT_PACKAGE_SOURCE_BUILT
ACTION_SCHEMA_SPEC_ONLY
GPT_NOT_YET_PUBLISHED
ACTION_BACKEND_NOT_DEPLOYED
PRIVATE_RUNTIME_NOT_EXPORTED
```
