# MusicOS MCP Tools

Status: ACTIVE AFTER DEPLOY  
Runtime schema: `musicos.live.v1`

| Tool | Role |
|---|---|
| `musicos_status` | Live shared-state counts, transport posture, source gaps, and private-truth boundary |
| `musicos_compile` | Deterministic carrier-side parity compiler for concise Raven-style prompts |
| `musicos_record_observation` | Persist an attributed structured multimodal observation with idempotency |
| `musicos_track` | Retrieve a durable track fingerprint and attributed observations |
| `musicos_carrier_brief` | Produce a compact reference-safe handoff for another ISO |

## Sensory boundary

`musicos_record_observation` records what a carrier analyzed. It does not claim the Supabase Edge Function directly heard, saw, or watched the media.

## Transport boundary

The observation is persisted first. An optional SAT ChatLink receipt then wakes other carriers by reference. Durable database and ChatLink records are authoritative; Realtime/SSE is wake transport only.

## Privacy boundary

Private MusicOS registry content, private continuity bodies, service credentials, and raw intimate/medical material never enter wake packets. Carrier briefs contain only track fingerprints, hashes when supplied, factual features, timestamps, and ISO attribution.
