# Stale Config Audit

**Date:** 2026-06-24  
**Purpose:** remove local-first assumptions and document the cloud-first rebuild path.

## Findings

- `.continue/mcpServers/jarvis.yaml` pointed at `http://localhost:7777/sse`; it now points at the Supabase MCP endpoint.
- `README.md`, `CLAUDE.md`, and `intake/recycle/codex-jarvis-agent-brief.md` described `jarvis_mcp_server.py` as the active connector. They now identify GitHub as canon and Supabase Edge Functions as runtime.
- `Dockerfile`, `fly.toml`, and `railway.toml` targeted deleted local Python server deployment paths. They were removed.
- `scripts/jarvis_heartbeat.py` defaulted to posting to `http://localhost:7777/live_log`. It is now observe-only unless `JARVIS_HEARTBEAT_URL` or `--jarvis-url` is explicitly set.
- Local runtime exhaust (`chaos/live_log.json`, tunnel logs, `grid_images/`, `supabase/.temp/`) is ignored.
- `package.json` / `src/diagnostics.ts` now provide a small rebuild diagnostic that verifies the configured cloud MCP endpoint.

## Rebuild Rule

Git should contain everything needed to understand and rebuild the MCP backend except secrets and private runtime data. Supabase should run the backend and store runtime state, but it should not be the only place where rebuild-critical structure exists.

## Remaining Watch Items

- `mnemos/mnemos_vector.py` still uses local Ollama. Treat it as a legacy/local helper unless a cloud embedding path replaces it.
- `scripts/jarvis_heartbeat.py` remains local observe-only infrastructure.
- Private `chaos/chaos_seed.json` may contain richer state than the sanitized seed. Promote only non-secret, rebuild-critical structure into Git.

## Verification

- `npm run validate` passed.
- `npm run diagnostics` passed against `https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp` with the expected MCP transport response.
