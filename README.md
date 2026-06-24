# JARVIS

JARVIS is a local-first AI orchestration experiment built around an MCP-style server, governed routing, and semantic memory.

The public repository contains the code and safe examples. Local runtime state, logs, vector databases, private seeds, and secrets should stay local or move to Supabase.

## Project Pieces

- `jarvis_mcp_server.py` - FastAPI JSON-RPC/SSE server exposing JARVIS tools.
- `mnemos/mnemos_vector.py` - semantic memory layer backed by SQLite and Ollama embeddings.
- `chaos/session_sync.py` - session start/end helpers and HUGINN-style diff logic.
- `chaos/chaos_seed.example.json` - sanitized sample seed for local setup.
- `intake/` - GitHub-backed review lane for GPT, Claude, Codex, and other AI handoffs.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy chaos\chaos_seed.example.json chaos\chaos_seed.json
python jarvis_mcp_server.py
```

The server runs at:

```text
http://localhost:7777
```

Health check:

```text
http://localhost:7777/health
```

## Optional Supabase Sync

Set these environment variables before starting the server:

```powershell
$env:SUPABASE_URL="https://oexghfsvhnggddllgvrt.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="your-private-service-role-key"
```

Use a service-role key for server-side JARVIS sync. Do not commit it. Public anon/publishable keys should only be used after Row Level Security policies are configured.

You can also put the same values in a local `.env`; the MCP server and MNEMOS loader read it automatically.

## Optional MNEMOS Vector Search

MNEMOS expects Ollama with `nomic-embed-text`:

```powershell
ollama pull nomic-embed-text
ollama serve
```

`jarvis_end` and `jarvis_log` write local JSON, Supabase rows, and MNEMOS vectors when the required services are available.

## Continue.dev

Workspace MCP configs live in `.continue/mcpServers/`:

- `jarvis.yaml` connects Continue to the local JARVIS server at `http://localhost:7777/sse`.
- `gbrain.yaml` connects Continue to `gbrain serve` after GBrain is installed.

MCP tools only load in Continue agent mode. Start JARVIS before opening the tools:

```powershell
python jarvis_mcp_server.py
```

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

Codex is the JARVIS execution layer for local implementation work. Its archetype is Kang: production, building, execution. When Codex edits files, runs tests, applies migrations, commits, pushes, or syncs the repo, treat that as a JARVIS-executed operation under the governed workflow.

## Continuity Records

Use JC objects as the readable session event log. Keep the durable spine in git commit history plus machine-readable handoff artifacts. `chaos/session_sync.py` returns a JC-shaped continuity wrapper, and the handoff files in `JarvisMain/Implementation/task/` should point at the latest commit hash when a session exits early.
Star Logs are the summarized form of that lane, with timestamps acting as pointers that let us fetch day, week, or month slices without inventing structure on the fly. The continuity ladder and session-open bootstrap are defined in `JarvisMain/Architecture/specs/continuity-layers-and-bounded-autonomy.md`.

JARVIS stats are event-driven, not decorative. Trigger definitions live in `intake/recycle/jarvis-stats-triggers.md`, and MCP clients can read stats with `jarvis_stats`.

Long-range concepts live in `intake/recycle/`. THE GRID is tracked there as a future navigable knowledge space with JARVIS-as-Virgil guidance, Tron-inspired interface language, and Oda-scale worldbuilding.

## Repo Sync Loop

Codex can make targeted repo changes, commit them to GitHub, and JARVIS can pull the updated code through its MCP tool:

```text
Describe the change in Codex
Codex edits and pushes hurrisonferd/jarvis
Call jarvis_repo_sync with action=status
Call jarvis_repo_sync with action=pull when ready
Restart the local server if Python code changed
```

`jarvis_repo_sync` only supports `status` and fast-forward `pull`. It refuses to pull over uncommitted local changes.

## Heartbeat Watcher

The first live-mesh heartbeat is observe-only:

```powershell
python scripts\jarvis_heartbeat.py --once
python scripts\jarvis_heartbeat.py --interval 60
```

It watches repo and `intake/` changes, writes local state to `%LOCALAPPDATA%\JARVIS\heartbeat\heartbeat_state.json`, and records recent events in `%LOCALAPPDATA%\JARVIS\heartbeat\heartbeat_log.json`. It does not pull, edit, process intake, or mutate Supabase automatically.

## Keep Private

Do not commit:

- `chaos/chaos_seed.json`
- `chaos/session_log.json`
- `chaos/prometheus_log.json`
- `chaos/mnemos_vectors.db`
- `.env`
