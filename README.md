# JARVIS

JARVIS is a cloud-first AI orchestration system built around a Supabase Edge Function MCP connector, governed routing, and semantic memory.

The public repository contains the code and safe examples. Runtime state, memory rows, connector traffic, and governed tool state belong in Supabase/GitHub-backed cloud surfaces. Local files are only for development, private seeds, temporary logs, and diagnostics.

## Project Pieces

High-value maps and engines are surfaced in `IMPORTANT.md`.

- `ROOT-SIGNS.md` - first-door map for root folders and local cave signs.
- `supabase/functions/jarvis-mcp/` - cloud MCP connector exposed as a Supabase Edge Function.
- `JarvisMain/Architecture/rebuild/jarvis-backup-seed.md` - sanitized rebuild packet for the MCP backend.
- `JarvisMain/Connectors/JarvisMCPSupabase/` - Git-backed MCP tool mirror docs.
- `mnemos/mnemos_vector.py` - semantic memory layer backed by SQLite and Ollama embeddings.
- `chaos/session_sync.py` - session start/end helpers and HUGINN-style diff logic.
- `chaos/chaos_seed.example.json` - sanitized sample seed for local setup.
- `intake/` - GitHub-backed review lane for GPT, Claude, Codex, and other AI handoffs.

## Cloud Connector

The connector endpoint is:

```text
https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp
```

MCP clients should connect to that URL with SSE/Streamable HTTP support. The Continue config in `.continue/mcpServers/jarvis.yaml` is pointed at the cloud connector.

Secrets for the deployed function live in Supabase, not in this repo. Keep service-role keys, MCP write tokens, GitHub tokens, and private seeds out of git.

## Local Development

Local development is for tests, scripts, and diagnostics only. Do not treat a local MCP server or tunnel as the authoritative runtime.

If a script needs Supabase access, set local environment variables without committing them:

```powershell
$env:SUPABASE_URL="https://oexghfsvhnggddllgvrt.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="your-private-service-role-key"
```

Use a service-role key only in trusted server-side contexts. Public anon/publishable keys should only be used after Row Level Security policies are configured.

## Continue.dev

Workspace MCP configs live in `.continue/mcpServers/`:

- `jarvis.yaml` connects Continue to the Supabase-hosted JARVIS MCP connector.
- `gbrain.yaml` connects Continue to `gbrain serve` after GBrain is installed.

MCP tools only load in Continue agent mode. The JARVIS connector is cloud-hosted; no local server startup is required.

## GBrain

GBrain requires Bun. Install Bun first if needed:

```powershell
powershell -c "irm bun.sh/install.ps1 | iex"
```

Then run:

```powershell
.\scripts\install_gbrain.ps1
```

The script follows the upstream standalone path: `bun install -g github:garrytan/gbrain`, `gbrain init --pglite`, then `gbrain doctor`.

## AI Intake

Use `intake/` for AI-generated uploads that should be reviewed before they become JARVIS memory, issues, migrations, or code changes.

- Put GPT handoffs in `intake/gpt/`.
- Put Claude handoffs in `intake/claude/`.
- Put Codex handoffs in `intake/codex/`.
- Move reviewed files to `intake/processed/`.
- Copy reusable prompts, patterns, and decisions to `intake/recycle/`.

Do not commit secrets, service-role keys, private seeds, or raw private logs in intake files.

All intake promoted into code, memory, migrations, policies, or automation should follow the JARVIS governed workflow in `intake/recycle/jarvis-governed-workflow.md`: review against Gold Law, identify relevant God Systems, log important rationale, and preserve user control.

Codex is the JARVIS execution layer for implementation work. Its archetype is Kang: production, building, execution. When Codex edits files, runs tests, applies migrations, commits, pushes, or verifies cloud-visible state, treat that as a JARVIS-executed operation under the governed workflow.

## Continuity Records

Use JC objects as the readable session event log. Keep the durable spine in git commit history plus machine-readable handoff artifacts. `chaos/session_sync.py` returns a JC-shaped continuity wrapper, and the handoff files in `JarvisMain/Implementation/task/` should point at the latest commit hash when a session exits early.
Star Logs are the summarized form of that lane, with timestamps acting as pointers that let us fetch day, week, or month slices without inventing structure on the fly. The continuity ladder and session-open bootstrap are defined in `JarvisMain/Architecture/specs/continuity-layers-and-bounded-autonomy.md`.
Resumability is the actual contract, defined in `JarvisMain/Architecture/specs/resumability-definition.md`, and the bootstrap packet should carry a resumability receipt with source basis, repo head, and verification time.
The operating manual now lives in `JarvisMain/Manual/`, with a bounded event history for notable changes.

JARVIS stats are event-driven, not decorative. Trigger definitions live in `intake/recycle/jarvis-stats-triggers.md`, and MCP clients can read stats with `jarvis_stats`.

Long-range concepts live in `intake/recycle/`. THE GRID is tracked there as a future navigable knowledge space with JARVIS-as-Virgil guidance, Tron-inspired interface language, and Oda-scale worldbuilding.

## Repo Sync Loop

Codex can make targeted repo changes, commit them to GitHub, and the cloud connector can read the updated code through its GitHub-backed MCP tools:

```text
Describe the change in Codex
Codex edits and pushes hurrisonferd/jarvis
Call jarvis_github_commits / jarvis_self_test to verify cloud-visible state
Redeploy jarvis-mcp when Supabase Edge Function code or baked secrets change
```

## Heartbeat Watcher

The first live-mesh heartbeat is observe-only:

```powershell
python scripts\jarvis_heartbeat.py --once
python scripts\jarvis_heartbeat.py --interval 60
```

It watches repo and `intake/` changes, writes local state to `%LOCALAPPDATA%\JARVIS\heartbeat\heartbeat_state.json`, and records recent events in `%LOCALAPPDATA%\JARVIS\heartbeat\heartbeat_log.json`. It does not pull, edit, process intake, or mutate Supabase automatically.

## Raven Zero

`live_session.py` provides the default free fallback backend for local JARVIS/VoiceOS experiments:

```powershell
python .\live_session.py status
python .\live_session.py search "GridTools"
python .\live_session.py
```

Raven Zero uses local capsule retrieval and deterministic commands first. It can search/read safe repo files, report status, and run allowlisted scripts. Set `RAVEN_ZERO_OLLAMA_MODEL` to an installed Ollama model name to add optional local synthesis without paid API calls.

## Keep Private

Do not commit:

- `chaos/chaos_seed.json`
- `chaos/session_log.json`
- `chaos/prometheus_log.json`
- `chaos/live_log.json`
- `chaos/tunnel_*.txt`
- `chaos/mnemos_vectors.db`
- `supabase/.temp/`
- `.env`
