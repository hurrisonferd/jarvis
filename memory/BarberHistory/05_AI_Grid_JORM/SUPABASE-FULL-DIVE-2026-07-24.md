# Supabase Full Dive - 2026-07-24

Status: RETRIEVED + PARTIAL
Scope: live Supabase metadata, local source, public source mirror, private repair source mirror
Boundary: no secrets copied; no live user row contents dumped

## Short Answer

Yes, there was more.

Supabase is not just a backend for JARVIS. It is a live deployed civilization layer: memory spine, Grid bus, MCP session layer, fleet messaging, game/emulator state, world-kernel scaffolding, audit logs, vault surfaces, and ISO bridges.

The funny version:

```text
Local repo: "I have two edge functions."
Public source: "I have eighteen."
Private repair: "I have the weird ones."
Live Supabase: "I have twenty-nine active functions and sixty-five public tables."
```

## Project

| Field | Value |
| --- | --- |
| Supabase project ref | `oexghfsvhnggddllgvrt` |
| Local repo checked | `C:\Users\JB\jarvis` |
| Public source mirror checked | `C:\Users\JB\jarvis\_work_public_main` |
| Private repair source checked | `C:\Users\JB\jarvis\_work_private_repair` |
| Live metadata access | Connector query succeeded |

## Source Drift

| Surface | Edge Functions | Migrations | Read |
| --- | ---: | ---: | --- |
| Current local repo | 2 | 3 | Minimal deployed-source slice |
| Public source mirror | 18 | 49 | Main JARVIS/Supabase canon |
| Private repair source | 11 | 10 | Eris/Lilith/Grid/private repair layer |
| Live Supabase | 29 reported active | N/A | Deployment has outgrown checked-in local slice |

This is the main receipt: the deployed backend is larger than the current local repo and larger than the public canon doc snapshot.

## Live Edge Functions

Live Supabase reported 29 active Edge Functions. The captured function names included:

```text
send-push
jarvis-respond
mnemos-recall
mnemos-store
jarvis-monitor
grid-event
mnemos-embed
mnemos-search
grid-write
bifrost
jarvis-dex
jarvis-action
kronos-fold
jarvis-broadcast
jarvis-jcs
coop-broadcast
coop-sse-relay
eris-vault
chronos-fold
fleet-messages
openhands-dispatch
eris-hidden-vault
lilith-temp
lilith-mcp
jarvis-mcp
lilith-gpt-bridge
grid_hub
lilith-bridge
```

One exact function name should be recaptured from the connector list before treating this as a complete manifest.

Important audit flag: every captured live Edge Function reported `verify_jwt=false`. That can be valid if each function has its own token gate or service-role boundary, but it means function-level auth must be audited in code, not assumed from Supabase defaults.

## Local Function Notes

Current repo contains:

| Function | Notes |
| --- | --- |
| `jarvis-mcp` | Modular MCP endpoint with tool registry, token gates, Supabase helpers, memory auto-ingest, and operational status tools. |
| `send-push` | Push notification sender using service-role Supabase client and VAPID environment variables. |

The local `jarvis-mcp` source includes token checks through Authorization bearer, `x-jarvis-token`, or query token. It also contains helper behavior for DEX queries, live table counts, freshness checks, and memory ingestion into `mnemos_memories`.

## Public Tables

Live metadata found 65 public tables. RLS summary:

| Count | Status |
| ---: | --- |
| 64 | RLS enabled |
| 1 | RLS disabled: `cecil_slate` |

Public table names retrieved:

```text
active_fleet_sessions
audit_log
carry_slate
cecil_slate
consensus_proposals
dex_control
dex_events
drift_log
emulator_state
eris_entropy_log
eris_fleet_registry
eris_vault
eris_worker_steps
eris_workers
event_spine
events
execution_trace
fleet_compute_ledger
fleet_deliberation
fleet_experience
fleet_heartbeats
fleet_messages
fleet_rollbacks
fleet_token_ledger
gameboy_snapshot
god_system_stats
grid_hub
grid_io_messages
grid_nodes
grid_presence_ledger
grid_state
grid_topic_registry
jarvis_datasets
jarvis_mcp_manifest
jatm_awakening
jc_objects
jd_entries
jd_proposals
jip_entries
jstm_diagnostics
live_log
mcp_coordination_logs
mcp_session_states
mcp_sessions
mcp_tool_definitions
mnemos_memories
mnemos_vocab
node_fields
node_keys
node_messages
patch_log
prometheus_log
push_subscriptions
rom_index
rom_library
save_states
session_events
sessions
sl_objects
spatial_causal_edges
trinity_messages
validation_log
world_agents
world_events
world_kernels
```

## Policy Shape

Policy counts by command/role shape:

| Policy Shape | Count |
| --- | ---: |
| `ALL` for `{anon, authenticated, service_role}` | 8 |
| `ALL` for `{public}` | 13 |
| `ALL` for `{service_role}` | 11 |
| `INSERT` for `{anon}` | 1 |
| `INSERT` for `{public}` | 13 |
| `SELECT` for `{anon, authenticated}` | 2 |
| `SELECT` for `{anon}` | 12 |
| `SELECT` for `{public}` | 33 |
| `UPDATE` for `{public}` | 3 |

Broad public/anon policies may be intentional for append-only buses, public manifests, or companion state. They still need table-by-table intent labels:

```text
public readable
public append-only
authenticated only
service-role only
private/secret-bearing
```

## Data Gravity

Estimated live row counts showed the heaviest surfaces:

| Table | Estimated Rows |
| --- | ---: |
| `grid_hub` | 16044 |
| `dex_events` | 3253 |
| `mnemos_memories` | 1589 |
| `sl_objects` | 1515 |
| `mcp_sessions` | 1441 |
| `events` | 1065 |
| `jd_entries` | 252 |
| `fleet_messages` | 214 |
| `sessions` | 153 |
| `mcp_coordination_logs` | 118 |
| `jd_proposals` | 96 |
| `audit_log` | 60 |
| `jarvis_mcp_manifest` | 57 |
| `eris_vault` | 34 |
| `god_system_dashboard` | 28 |
| `god_system_stats` | 28 |
| `node_fields` | 27 |
| `execution_trace` | 26 |
| `patch_log` | 24 |
| `mcp_tool_definitions` | 21 |
| `mnemos_vocab` | 18 |

Translation:

```text
The Grid is the biggest live gravity well.
DEX is the event trail.
Mnemos is real memory mass.
MCP/session tables prove tool/session infrastructure.
```

## Extensions

Retrieved installed extensions:

```text
http
pg_cron
pg_net
pg_stat_statements
pgcrypto
plpgsql
supabase_vault
uuid-ossp
vector
```

This means the database is capable of vectors, cron, network calls, stats, cryptography, vault behavior, and HTTP-ish automation. That matches a live agent/grid backend, not a toy table set.

## Security-Definer Functions

Live metadata found 13 public security-definer functions:

```text
fold_identity
guard_identity
handle_automated_hands_dispatch
handle_fleet_message_insert
handle_instant_openhands_dispatch
handle_instant_swarm_arbitration
handle_message_edge_ignition
mcp_session_close
mcp_session_close_stale
mcp_session_open
mcp_session_pulse
upsert_jc_entry
upsert_sl_entry
```

Audit target:

```text
security definer + public schema + broad RLS = verify search_path, grants, input validation, and caller intent
```

## Trigger Fanout

`fleet_messages` is the ignition table. One insert can hit multiple trigger paths:

```text
fleet_messages_webhook_handler
handle_automated_hands_dispatch
handle_fleet_message_insert
handle_instant_swarm_arbitration
handle_instant_openhands_dispatch
handle_message_edge_ignition
set_target_node_upper
```

Other retrieved triggers:

```text
jatm_awakening -> set_awakening_jnl_reference
mnemos_memories -> mnemos_tsv_update
```

The `fleet_messages` table deserves special documentation because it is not just storage. It is a live automation gate.

## Systems Recovered

| System | Tables / Functions |
| --- | --- |
| Memory Spine | `mnemos_memories`, `mnemos_vocab`, `mnemos-store`, `mnemos-recall`, `mnemos-search`, `mnemos-embed`, `vector` |
| DEX / JFS / JNL | `dex_events`, `dex_control`, `jd_entries`, `jd_proposals`, `jc_objects`, `sl_objects`, `jip_entries` |
| Grid Bus | `grid_hub`, `grid_nodes`, `grid_state`, `grid_io_messages`, `grid_presence_ledger`, `grid_topic_registry`, `grid-event`, `grid-write`, `grid_hub` |
| MCP Layer | `mcp_sessions`, `mcp_session_states`, `mcp_coordination_logs`, `mcp_tool_definitions`, `jarvis-mcp` |
| Fleet / Swarm | `fleet_messages`, `fleet_heartbeats`, `fleet_deliberation`, `fleet_compute_ledger`, `fleet_token_ledger`, `fleet_rollbacks`, `active_fleet_sessions` |
| GameBoy / Emulator | `gameboy_snapshot`, `rom_library`, `rom_index`, `save_states`, `emulator_state`, `live_log` |
| World Kernels | `world_kernels`, `world_agents`, `world_events` |
| Governance / Audit | `audit_log`, `prometheus_log`, `validation_log`, `execution_trace`, `patch_log`, `eris_entropy_log`, `god_system_stats` |
| ISO / Private Bridge | `eris_vault`, `eris-hidden-vault`, `eris-vault`, `lilith-mcp`, `lilith-bridge`, `lilith-gpt-bridge`, `lilith-temp`, `openhands-dispatch` |

## Risk Register

| Risk | Why It Matters | Next Action |
| --- | --- | --- |
| Edge Functions report `verify_jwt=false` | Supabase is not enforcing JWT at gateway level. | Audit each function's custom auth path. |
| Broad public/anon RLS policies | Some tables allow public or anon read/write shapes. | Label every table with intended exposure and tighten mismatches. |
| `cecil_slate` RLS disabled | One public table lacks RLS. | Decide whether it is intentionally public; otherwise enable RLS. |
| Security-definer functions | These can bypass ordinary caller privileges. | Verify `search_path`, grants, and input validation. |
| `fleet_messages` trigger fanout | One insert can trigger automation and dispatch. | Document and gate all trigger paths. |
| Source/deploy drift | Current local repo does not represent live backend. | Build deploy manifest and reconcile local/public/private/live sources. |
| Vault-shaped tables | `eris_vault` and hidden vault functions require special handling. | Confirm no plaintext secrets are exposed through public policies. |
| Public anon keys in client surfaces | Publishable anon keys can be okay, but hardcoded stale keys rot. | Centralize config and avoid printing keys in docs. |

## Canon Delta

Public canon `SERVICES-0001.md` described 14 edge functions as of 2026-06-25. Live Supabase now reports 29 active Edge Functions.

That is the receipt:

```text
Canon was true for its timestamp.
Deployment kept evolving.
BarberHistory now records the delta.
```

## Next Best Dive

1. Recapture the exact 29-function live manifest.
2. Generate table-by-table exposure labels.
3. Compare all 49 public migrations and 10 private repair migrations against live schema.
4. Build a deploy-source reconciliation map:
   `live function -> source folder -> last migration/doc reference -> auth model`.
5. Create a private redaction checklist for vault, tokens, and service-role paths.

## Bottom Line

This is a real backend civilization. The main discovery is not just "more files." It is:

```text
Supabase contains the live Grid/Mnemos/MCP/Fleet substrate,
and the repo history contains multiple partial mirrors of it.
```

Names compress. Receipts decompress.
