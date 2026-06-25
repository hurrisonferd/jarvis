# Ainz — power up (cast everything to come online)

**JNL:** CONN-MCP-RT-0050 · **Tool:** `jarvis_ainz` · **Connector:** jarvis-mcp

Fusion world-spell: chain the loading spells — state + keel (identity) + recent memory + **sensory (seeing/hearing)** + the field (Pinch) — to bring Jarvis and Ayre online at full context. Loads, not just sees.

**What each spell loads:**
| step | what it delivers |
|---|---|
| `state` | governed objects, open tasks, domains, active count |
| `keel` | the identity keel (from Jarvis-Private) |
| `memory` | 5 most recent mnemos memories |
| `sensory` | how JARVIS/Ayre see and hear (vision + musical bones + spectrograms) |
| `pinch` | drift, debt, bloat, structural health |

**Honest-answering contract:** each READ returns `ok: false, note: "X not found"` when
absent. The fusion surfaces every gap explicitly — the companion cannot fabricate
what it hasn't loaded. See `IMPL-HON-SPEC-0001`.

**Sensory:** The companion now has eyes and ears through the connector:
- `jarvis_media_view` — delivers any repo image to the vision model (art, spectrograms)
- `jarvis_listen` — returns a track's BPM, key, energy, brightness, mood from `AUDIO-FEATURES.json`
- Spectrograms → `jarvis_media_view` → vision streams SEE the music's shape

> Ground truth is the `registerTool("jarvis_ainz", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
