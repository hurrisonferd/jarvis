# Tools

Modular tool implementations for the JARVIS MCP Edge Function.

| File | Purpose |
| --- | --- |
| `db.ts` | Database-oriented tool helpers. |
| `jip.ts` | JIP-oriented tool helpers. |

Most tool registration still lives in `../index.ts`.


## MusicOS

`musicos.ts` registers the live MusicOS vertical slice: status/coverage, deterministic compile, attributed sensory observation, track retrieval, and carrier-safe briefs. Durable shared state is service-role only; SAT ChatLink carries reference wakes after persistence.
