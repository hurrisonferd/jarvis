# MusicOS

**JNL:** PROJ-MUSI-BIO-0001
**Status:** ACTIVE
**JARVIS repo:** `JarvisSide/Projects/MusicOS/` (canonical spec, governed)
**This repo:** development workspace, assets, Suno outputs, registry
**Suno:** `suno.com/profile/jarvis-ayre`

## What
Procedural music generation framework: persistent musical identity through motif systems,
constraint rules (MusicOS Gold Laws), and prompt-to-composition compilation — music as
evolving identity, not standalone tracks.

## Current state
- **47 tracks** catalogued (MID-0001 through MID-0047)
- RGB physics encoding: R=Power, G=Groove, B=Range
- `registry/MUSIC-CATALOG.md` — full catalog with names, series, duplicates resolved
- `registry/` — 49 JD entries (47 tracks + 2 system docs)
- Active production via Suno; canonical registry in JARVIS repo

## Directory map
- `src/` — prompt generation tools, distillation scripts
- `registry/` — canonical JD entries (mirrored from JARVIS repo)
- `composers/` — per-composer prompt configs
- `genres/` — genre profiles
- `instruments/` — instrument definitions
- `presets/` — Gold Law presets, constraint rules
- `templates/` — prompt templates
- `outputs/` — Suno outputs, audio files
- `experiments/` — scratch space for new series or techniques
