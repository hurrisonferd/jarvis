---
memory_tier: JLTM
grade: system
---

# Listen — read music's bones (hearing via analysis)

**JNL:** CONN-MCP-RT-0048 · **Tool:** `jarvis_listen` · **Connector:** jarvis-mcp

`jarvis_listen` reads durable musical feature receipts from
`JarvisSide/Media/AUDIO-FEATURES.json`. `operations/scripts/music_ears.py` produces
those receipts from either the private MusicOS repository library or a public HTTPS
audio source supplied to the `JARVIS — MusicOS Ears` workflow.

## Returned fields

| field | meaning |
|---|---|
| `bpm` | estimated tempo |
| `key` | Krumhansl-Schmuckler major/minor estimate |
| `energy_rms` | average signal energy |
| `brightness_hz` | spectral centroid |
| `onset_density` | detected events per second |
| `dynamic_range_db` | loud-to-quiet ratio |
| `mood` | derived pace, energy, and tone |
| `spectrogram` | path for `jarvis_media_view` |
| `source` | credential-free provenance receipt |

## Ingestion

- Repository library: manually dispatch the workflow without `source_url`, or use
  the existing private-repository dispatch.
- Internet/GitHub audio: dispatch with a direct public HTTPS audio URL. Standard
  GitHub `blob` URLs are normalized to raw-file URLs.
- URL credentials and query parameters are rejected and never written to receipts.
- Audio downloaded from a URL is temporary. The durable outputs are the feature
  receipt and spectrogram.

The tool reports machine-audible structure. Raven retains the meaning and lived
interpretation of the music.

> Ground truth is the `registerTool("jarvis_listen", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts`; this file is its governed mirror.
