# MusicOS Tools

Status: RETRIEVED
Created: 2026-07-24

Public main mirror contains inactive MusicOS scripts:

```text
C:\Users\JB\jarvis\_work_public_main\scripts\INACTIVE\music_ears.py
C:\Users\JB\jarvis\_work_public_main\scripts\INACTIVE\music_nlp.py
C:\Users\JB\jarvis\_work_public_main\scripts\INACTIVE\music_distill.py
```

## `music_ears.py`

Purpose: MusicOS ears for JARVIS.

Capabilities found:

| Capability | Notes |
| --- | --- |
| Audio loading | Uses `librosa`. |
| Feature extraction | Duration, BPM, estimated key, RMS energy, brightness, onset density, dynamic range, mood. |
| Spectrogram rendering | Generates mel spectrograms with matplotlib. |
| Output | `AUDIO-FEATURES.json`, `MEDIA-MANIFEST.md`, spectrogram PNGs. |
| Modes | Remote private clone via token or local `--audio-dir`. |

## `music_nlp.py`

Purpose: MusicOS NLP enrichment.

Capabilities found:

| Capability | Notes |
| --- | --- |
| Prompt matching | Matches audio filenames to prompt files. |
| RGB tagging | R=Power, G=Rhythm/Groove, B=Range. |
| Physics extraction | Rail authority, gravity groove, elasticity, snap-back, boundary, JoJo/SBR tags. |
| Series detection | Unbreakable Momentum, Syncopation Engine, Neon Race, Steel Ball Run. |
| Semantic summary | Generates companion-readable descriptions while preserving Raven's creative language. |

Important code comment:

```text
The creative language is Raven's - preserve it. Do not summarize away the poetry.
```

## `music_distill.py`

Purpose: MusicOS cognitive distillation.

Capabilities found:

| Layer | Meaning |
| --- | --- |
| Primitives | Raw parameter atoms like BPM, key, color, physics tags. |
| Grammar | Timbre, rhythm, and spatial description rules. |
| Suno Prompt | Raven language to Suno-compatible prompt string. |
| Tracker | Famistudio / NSF structural mapping. |
| Wave | Audio feature to MusicOS concept correlation. |

Important code comment:

```text
Preserve the poetry; extract the physics.
```

## Tool Status

These scripts are in `scripts/INACTIVE`, so they are recovered architecture and utility code, not confirmed active production tools in this pass.
