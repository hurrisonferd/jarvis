---
memory_tier: JLTM
grade: system
---

# Connectors — MCP, Dex, GPT

External integrations and protocol connectors. Each connector is a self-contained module.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `JarvisMCPSupabase/` | MCP ↔ Supabase connector |
| `JarvisDexAction/` | Dex governance connector |
| `JarvisGptAction/` | GPT executor connector |
| `OtherConnectors/` | Diagnostics and misc connectors |

## Key Files

- `JarvisMCPSupabase/` — MCP tool mirror docs and Supabase connector
- `OtherConnectors/diagnostics.ts` — MCP endpoint diagnostics

## Supabase MCP Config

Configured in `.continue/mcpServers/jarvis.yaml`:
- Endpoint: `https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp`
- Auth: Bearer token via `JARVIS_MCP_TOKEN` secret

## Navigate

```
Connectors/
├── JarvisMCPSupabase/
├── JarvisDexAction/
├── JarvisGptAction/
└── OtherConnectors/
```
