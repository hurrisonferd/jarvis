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
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_KEY="your-supabase-key"
```

## Optional MNEMOS Vector Search

MNEMOS expects Ollama with `nomic-embed-text`:

```powershell
ollama pull nomic-embed-text
ollama serve
```

## Keep Private

Do not commit:

- `chaos/chaos_seed.json`
- `chaos/session_log.json`
- `chaos/prometheus_log.json`
- `chaos/mnemos_vectors.db`
- `.env`
