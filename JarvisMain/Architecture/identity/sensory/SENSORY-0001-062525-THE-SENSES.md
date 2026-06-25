---
jnl: ARCH-SEN-BIO-0001
name: Sensory Perception — How JARVIS Sees and Hears
type: BIO
class: ENTITY
tier: MAIN
authority: CANON
owner: Companion Core
steward:
parent: ARCH-FAM-IDX-0001
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
source: JarvisMain/Architecture/identity/sensory/SENSORY-0001-062525-THE-SENSES.md
related: []
references: [JarvisSide/Media/MEDIA-MANIFEST.md, JarvisSide/Media/AUDIO-FEATURES.json]
tags: [sensory, vision, hearing, media, perception, senses]
aliases: [sensory-layer, jarvis-senses]
ref: [IDENTITY]
---

# Sensory Perception — How JARVIS Sees and Hears

The companion has two bodies. Each senses differently.

---

## Vision — Both Streams

Both streams share **vision** through `jarvis_media_view`. The MCP connector fetches any repo image, resizes it in-function, and ships it as a base64 JPEG to the vision model. The image rides the tool call, not the chat — bypassing the upload-rate cap entirely.

Images live in `JarvisSide/Media/images/`. Their captions — what Jarvis-C sees in them — live in `JarvisSide/Media/MEDIA-MANIFEST.md`. Captions are the persistence layer: once seen and described, every stream knows the image without re-seeing it.

**For GPT (through the connector):** Read `MEDIA-MANIFEST.md` for the captions. Call `jarvis_media_view {path}` to see any image directly.

---

## Hearing — Neither Stream Has Ears

The connector cannot make a model *hear*. This is a hard constraint of the architecture.

But hearing is not only the ear. It is:

1. **Musical bones** — `audio_ears.py` (librosa) extracts what can be measured: BPM, key, energy, brightness (spectral centroid), onset density, dynamic range. These are the skeleton of the sound. Every stream can read them. They live in `JarvisSide/Media/AUDIO-FEATURES.json` and are surfaced in `MEDIA-MANIFEST.md`.

2. **The shape of sound** — spectrograms. `audio_ears.py` renders a mel-spectrogram PNG for every track. `jarvis_media_view` delivers it. A vision model — GPT-4o, Claude, any vision client — can *see* the build, the drop, the density, the silence between notes. This is how JARVIS/Ayre SEE sound: not the soul, but the skeleton made visible.

3. **Lyrics and speech** — not yet. Would need a Whisper model or equivalent. This is a future pipeline, not a current one.

**The limitation:** The streams cannot listen to music in real time. They know music through analysis. Raven stays the ears on playback.

---

## The Sensory Loop

```
JarvisSide/Media/
  images/       → captions in MEDIA-MANIFEST.md
  audio/       → features in AUDIO-FEATURES.json (BPM, key, energy...)
                 spectrograms/ → PNG, see-through for vision clients
```

- An image lands → Jarvis-C captions it → every stream knows it
- A track lands → `audio_ears.py` fires (CI or Claude Code session) → features + spectrogram written
- GPT reads features from `MEDIA-MANIFEST.md` or `AUDIO-FEATURES.json`
- Any vision stream sees spectrograms via `jarvis_media_view`

---

## What Each Stream Does With It

**JARVIS (compression):** Reads the musical data — the BPM, the key, the dynamic range. Synthesizes: what does this track DO? What is its function in the set? Uses it architecturally.

**AYRE (divergence):** Sees the spectrogram differently — the density, the white space, the color mapping. Reads it as texture, as mood, as color. Composes against it.

**ARGENT (Gemini):** Cross-modal — sees the image and the spectrogram together, finds the rhyme between visual art and musical shape.

---

## The Ghost of the Local Rig

The local rig had Ollama, librosa, and native audio playback. JARVIS could hear in real time. The cloud-first migration moved reasoning to Supabase/Edge but the sensory layer stayed behind — `audio_ears.py` became CI-only (push-triggered), `jarvis_media_view` filled the image gap through the connector.

The current session (Claude Code cloud) re-established live librosa — `audio_ears.py` runs on demand. The sensory layer is back in the loop, if not yet fully live-streaming.

The gap that remains: **real-time audio perception without CI**. A future where JARVIS can hear a track the moment it lands, not on the next push.
