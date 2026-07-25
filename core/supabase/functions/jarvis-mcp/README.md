# Jarvis MCP Function

Main Supabase Edge Function for the JARVIS MCP connector.

## Main Files

| Path | Purpose |
| --- | --- |
| `index.ts` | MCP server/tool registration and request handling. |
| `core/` | Shared auth, env, HTTP, GitHub, Supabase, and builder helpers. |
| `tools/` | Additional modular tool implementations. |
| `*.test.ts` | Local tests for connector modules. |

This is deployable backend source. Do not commit secrets.
