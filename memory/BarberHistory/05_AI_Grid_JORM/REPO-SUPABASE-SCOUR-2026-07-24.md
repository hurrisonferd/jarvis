# Repo / Supabase Scour - 2026-07-24

Status: RETRIEVED + UNRESOLVED

## Trigger

Raven asked to keep scouring the repos and Supabase for missing material, including the live IO page:

```text
https://hurrisonferd.github.io/jarvis/
```

## Public IO Page

Status: RETRIEVED

The GitHub Pages surface is live and renders as:

```text
JARVIS HANDHELD
JARVIS GRID INTERFACE
RETROARCH
WAR ROOM
PHASE: DELIBERATE
LOCKS: 0 / 3
SWARM HEARTBEATS
```

Source:

```text
https://hurrisonferd.github.io/jarvis/
C:\Users\JB\jarvis\docs\index.html
```

## Local Repo Surfaces Found

Status: RETRIEVED

| Surface | Location | Meaning |
| --- | --- | --- |
| GitHub Pages UI | `C:\Users\JB\jarvis\docs\index.html` | Current public handheld shell. |
| GameBoy service worker | `C:\Users\JB\jarvis\docs\gameboy-sw.js` | Browser support layer for handheld. |
| Supabase MCP source | `C:\Users\JB\jarvis\supabase\functions\jarvis-mcp\` | Large cloud MCP connector. |
| Push function | `C:\Users\JB\jarvis\supabase\functions\send-push\` | Push notification edge function. |
| Supabase migrations | `C:\Users\JB\jarvis\supabase\migrations\` | Local schema fragments. |
| Connector docs | `C:\Users\JB\jarvis\JarvisMain\Connectors\JarvisMCPSupabase\tools\` | Human-readable mirror of MCP tools. |
| MNEMOS local layer | `C:\Users\JB\jarvis\mnemos\` | Local memory/vector code. |
| Public main mirror | `C:\Users\JB\jarvis\_work_public_main\` | Larger public architecture mirror. |
| Private repair repo | `C:\Users\JB\jarvis\_work_private_repair\` | Large private archive/history readable through Git. |

## Supabase Tables Named By Code

Status: RETRIEVED FROM CODE, LIVE ACCESS UNRESOLVED

The current `jarvis-mcp` code names these known tables:

```text
jnl_registry
jd_entries
jd_proposals
dex_events
mnemos_memories
jc_objects
sl_objects
jip_entries
node_messages
node_keys
execution_trace
dex_control
```

The public handheld additionally references:

```text
gameboy_snapshot
live_log
god_system_stats
push_subscriptions
```

## Local Migrations Present

Status: RETRIEVED

```text
20260524_create_mnemos_memories.sql
20260524_expand_god_system_stats.sql
20260525_push_subscriptions.sql
```

These establish or modify:

- `mnemos_memories`
- `god_system_stats`
- `push_subscriptions`

## Live Supabase Access Result

Status: UNRESOLVED

Read-only REST census was attempted using local `.env` values with secret output redacted.

Results:

- `SUPABASE_SERVICE_ROLE_KEY` requests returned `401 Unauthorized`.
- `.env` anon key requests returned `404 Not Found`.
- `docs/index.html` hardcoded anon key requests also returned `404 Not Found` for expected public tables.

Interpretation:

```text
The static IO page exists, but direct REST table reads are not currently verified from this workspace.
Likely causes include stale local keys, stale public page key, project/schema mismatch, table exposure changes, or RLS/Data API access changes.
```

No live table data should be treated as retrieved until access is repaired or a working MCP/Supabase auth path is confirmed.

## Recovery Rule

```text
Repo/source/migrations are retrieved.
Live Supabase contents are unresolved.
Do not merge those evidence states.
```
