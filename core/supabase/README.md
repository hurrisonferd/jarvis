# Supabase

`core/supabase/` is the backend source cave.

## Main Areas

| Path | Purpose |
| --- | --- |
| `functions/` | Supabase Edge Functions, including the JARVIS MCP connector. |
| `migrations/` | Database migration history. |
| `.temp/` | Local Supabase CLI/runtime state; ignored. |

## Boundary

Secrets live in Supabase or local env, not in git.

Local source may drift from the deployed backend; use BarberHistory Supabase maps before assuming completeness.
