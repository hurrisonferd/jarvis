# JARVIS

JARVIS is a companion intelligence with continuity, memory, and governed execution — not a chatbot, a partner with a record. This repo is its body: the runtime, the memory, the governance, and the interfaces it speaks through.

**Authority:** Raven (John Barber) is final authority on all decisions. JARVIS proposes; Raven commits or rejects. No autonomous self-modification.

See [`CLAUDE.md`](./CLAUDE.md) for the canonical identity, mission, Gold Law, and the 27 God System pipeline. Every agent operating in this repo inherits that identity.

---

## Architecture (cloud-first)

The stack is **GitHub + Supabase + Claude Code**. No Ollama, no Neo4j, no local-PC-dependent services in the canonical path. If GitHub or an edge function can do the job, that is the path — even when working from the PC.

| Layer | Where | What |
|-------|-------|------|
| **Interface** | `docs/index.html` → [GitHub Pages](https://hurrisonferd.github.io/jarvis/) | The JARVIS handheld — TRON GRID, God System pipeline, SPEAK companion view, emulator |
| **Backend** | Supabase (`oexghfsvhnggddllgvrt`) | Tables (sessions, events, memory, consensus, world kernels) + edge functions (`jarvis-respond`, `mnemos-store`, `mnemos-search`, `grid-event`) |
| **Memory** | `mnemos/` + Supabase pgvector | GitHub-first: memory files committed to the repo; semantic search via OpenAI-compatible embeddings (1536-dim) |
| **Governance** | `.github/workflows/` + AEGIS/GNPL | Daily pipeline, GL7 entropy check, audit log, MNEMOS sync — all run on GitHub Actions |
| **Record** | `audit/patch_ledger.json` | Canonical patch tracker (mirrors Supabase `patch_log`) |

The live companion needs no install — it is a static page backed by Supabase. The interface is not JARVIS; JARVIS is the intelligence that runs through every interface.

---

## MNEMOS (memory)

GitHub-first. Memory files live in `mnemos/` (`context/`, `domains/`, `memories/`) and are committed to the repo, so any agent can read continuity with no credentials. Semantic search runs on Supabase pgvector:

- Auto-embed on store via `EMBEDDING_API_KEY` (OpenAI-compatible: OpenAI, Voyage, Cohere, …), model `text-embedding-3-small`.
- `mnemos-search` edge function: cosine similarity via `match_memories` RPC, keyword `ILIKE` fallback.
- `scripts/jarvis-recall.py` does semantic-first recall with keyword fallback.

## Governed Workflow

All changes follow the loop in `CLAUDE.md`: intake → context → implement → verify → log → commit. Significant decisions are logged (PROMETHEUS); expansion requires GL7 (`reduces_complexity=true`, `overlap_score_below=0.40`).

Use `intake/` for AI handoffs reviewed before they become memory, code, or migrations (`intake/gpt/`, `intake/claude/`, `intake/codex/` → `intake/processed/`; reusable patterns to `intake/recycle/`).

## Branch & merge

`main` is protected (serves GitHub Pages). Develop on a feature branch, then merge via pull request. Direct force/delete pushes to `main` are blocked; branch-create + PR-merge is the path.

---

## Optional: local MCP server (on-PC)

`jarvis_mcp_server.py` is a FastAPI MCP server (port 7777). It is **optional and PC-only** — kept for local workflows that genuinely benefit from on-machine services (Ollama embeddings, a local Neo4j graph). The cloud path above is canonical; reach for the local server only when the PC adds something GitHub/Supabase cannot.

```powershell
pip install -r requirements.txt
python jarvis_mcp_server.py          # http://localhost:7777  (health: /health)
```

Continue.dev MCP configs live in `.continue/mcpServers/` (`jarvis.yaml` → local SSE endpoint). MCP tools load in Continue agent mode only.

---

## Keep Private — never commit

- `.env` and `.env.*` (secrets)
- `chaos/chaos_seed.json`, `chaos/session_log.json`, `chaos/prometheus_log.json`
- `chaos/mnemos_vectors.db` and any local vector DB
- Service-role keys, private seeds, raw private logs

The public anon/publishable key is client-safe **only** behind Row Level Security. Service-role keys are server-side only.
