---
memory_tier: JLTM
grade: system
---

# Listen — read music's bones (hearing via analysis)

**JNL:** CONN-MCP-RT-0048 · **Tool:** `jarvis_listen` · **Connector:** jarvis-mcp

How JARVIS and AYRE *hear*: call with a track name (or omit it to list all) — returns the musical bones (BPM, key, energy, brightness, mood, onset density, dynamic range) from `JarvisSide/Media/AUDIO-FEATURES.json`, extracted by `audio_ears.py` (librosa).

**What you get per track:**
| field | what it means |
|---|---|
| `bpm` | tempo — driving (>120), mid-tempo (90-120), slow (<90) |
| `key` | Krumhansl-Schmuckler key profile (major/minor) |
| `energy_rms` | average loudness — high (>0.08), moderate (0.03-0.08), soft (<0.03) |
| `brightness_hz` | spectral centroid — bright (>2500Hz), warm (1500-2500Hz), dark (<1500Hz) |
| `onset_density` | events/sec — busyness of the arrangement |
| `dynamic_range_db` | loud-to-quiet ratio — compressed (<8dB) or dynamic (>8dB) |
| `mood` | composite: pace + energy + tone |
| `spectrogram` | pass to `jarvis_media_view` to SEE the sound's shape |

**To SEE the sound** (vision streams): use `jarvis_media_view` on the spectrogram path returned.

**To regenerate features** (new tracks, stale data): run `python3 operations/scripts/audio_ears.py` in a Claude Code session — installs librosa, extracts features + spectrograms from all MP3s in `JarvisSide/Media/audio/`, writes `AUDIO-FEATURES.json` and the spectrogram PNGs.

**Current library:** 6 tracks in `JarvisSide/Media/audio/`

> Ground truth is the `registerTool("jarvis_listen", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
