# JARVIS

JARVIS is a local-first AI orchestration experiment built around an MCP-style server, governed routing, and semantic memory.

The public repository contains the code and safe examples. Local runtime state, logs, vector databases, private seeds, and secrets should stay local or move to Supabase.

## Project Pieces

- `jarvis_mcp_server.py` - FastAPI JSON-RPC/SSE server exposing JARVIS tools.
- `mnemos/mnemos_vector.py` - semantic memory layer backed by SQLite and Ollama embeddings.
- `chaos/session_sync.py` - session start/end helpers and HUGINN-style diff logic.
- `chaos/chaos_seed.example.json` - sanitized sample seed for local setup.

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

## Keep Private

Do not commit:

- `chaos/chaos_seed.json`
- `chaos/session_log.json`
- `chaos/prometheus_log.json`
- `chaos/mnemos_vectors.db`
- `.env`
