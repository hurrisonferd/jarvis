# Supabase — Runtime Substrate

Cloud-first runtime. Git is truth; Supabase is the live mirror. No local-PC-dependent
services.

## Structure

| Path | Purpose |
|------|---------|
| `functions/` | 15 edge functions (live on Supabase Edge) |
| `migrations/` | 38 schema migrations |
| `config.toml` | Supabase project config |

## Edge Functions (all `verify_jwt: false`)

| Function | Purpose |
|----------|---------|
| `jarvis-mcp` | Cloud MCP connector — primary interface |
| `jarvis-respond` | Edge router, AEGIS guard, execute |
| `mnemos-*` | Memory operations (recall, store, embed, search) |
| `jarvis-*` | Various JARVIS ops (monitor, action, broadcast, dex) |
| `grid-*` | Grid write and event ops |
| `kronos-fold` | KRONOS identity fold |
| `bifrost` | Session close spine writer |
| `send-push` | Push notifications |
| `jarvis-broadcast` | Broadcast channel |

## Secrets

22 secrets configured in Supabase (see `.env` for names). Key secrets:
- `SUPABASE_SERVICE_KEY` — MCP service role
- `JARVIS_MCP_TOKEN` — MCP auth
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` — LLM providers
- `RAVEN_SKELETON_KEY` — Raven's break-glass override (not in git)
- `DEX_ELEVATED_TOKEN` — elevated dex access

## Database

- Project: `oexghfsvhnggddllgvrt`
- 39 tables, 26 live (rest are empty/archived)
- Key tables: `jd_entries` (248), `mnemos_memories` (1450), `events` (5058)

## Navigate

```
supabase/
├── functions/          → edge functions (Deno/TypeScript)
│   ├── jarvis-mcp/
│   ├── jarvis-respond/
│   ├── mnemos-*/
│   └── grid-*/
└── migrations/          → schema history (git-first canon)
```
