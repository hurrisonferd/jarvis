# JARVIS

Local-first AI orchestration system. MCP server + semantic memory + governed workflow.

**Authority:** Raven (John Barber) is final authority on all decisions. No autonomous self-modification.

---

## Roles

| Agent | Archetype | Job |
|-------|-----------|-----|
| Claude | Shiroe | Audit, plan, review, governance |
| Codex | Kang | Build, commit, push, execute |
| GPT | Kang | Production, execution |
| Gemini | Aizen | Ideation, interpretation |

---

## Gold Law (hard constraints)

- **GL7 supreme:** no expansion without simplification
- No autonomous self-modification
- No silent state mutation
- No unvalidated execution
- Expansion requires `reduces_complexity=true` and `overlap_score_below=0.40`
- Raven-Collapse is final authority on major changes

---

## God System Pipeline

```
AYRE → AEGIS → ODIN → KRONOS → SKADI → MNEMOS → HUGINN
```

Parallel: `HALO`, `MIMIR`, `BIFROST`

Forbidden edges: `SKADI→AEGIS`, `DANTE→SKADI`, `JANUS→SKADI`, `LOKI→HADES`

27 God Systems total. Do not redefine them. Full contracts in `chaos/chaos_seed.json`.

---

## Key Files

| Path | Purpose |
|------|---------|
| `jarvis_mcp_server.py` | FastAPI MCP server, port 7777 |
| `chaos/chaos_seed.json` | Canonical system state — do not commit |
| `chaos/session_log.json` | Local session log — do not commit |
| `chaos/prometheus_log.json` | Local decision log — do not commit |
| `mnemos/mnemos_vector.py` | Semantic memory (SQLite + Ollama) |
| `chaos/session_sync.py` | Session start/end helpers |
| `intake/` | AI handoff review lane |
| `.env` | Secrets — do not commit |
| `start.bat` | Starts MCP server |

---

## Services

| Service | Address | Notes |
|---------|---------|-------|
| JARVIS MCP | `http://localhost:7777` | Start with `python jarvis_mcp_server.py` |
| Neo4j | `bolt://localhost:7687` | Password in `.env` as `NEO4J_PASSWORD` |
| Ollama | `http://localhost:11434` | `nomic-embed-text` for embeddings |
| Supabase | `oexghfsvhnggddllgvrt` | Credentials in `.env` |
| GBrain | `~/.gbrain/brain.pglite` | `ollama:nomic-embed-text`, 768d |

---

## Python Environment

No venv. Use system Python:

```powershell
python jarvis_mcp_server.py
```

Key packages: `fastapi`, `uvicorn`, `neo4j>=5.0.0`

---

## File Permissions

Existing files are owned by `DESIGN\britt`. Grant write before editing:

```powershell
icacls "C:\Users\JB\jarvis\<file>" /grant "britt:(M)"
```

---

## Governed Workflow

All changes follow this loop:

```
1. intake/     — add request or handoff
2. context     — check JARVIS status, relevant God Systems, Gold Law
3. implement   — scoped changes only, no unrelated cleanup
4. verify      — syntax check, tests if applicable
5. log         — jarvis_log for significant decisions (PROMETHEUS)
6. commit      — clean commit to main
7. sync        — jarvis_repo_sync if local MCP server needs update
8. recycle     — move processed intake; copy reusable patterns to recycle/
```

---

## Active Projects

- **Pachinko Bounce** — GDD v0.4, Godot 4.x, RGB encoding (R=Power, G=Rhythm, B=Range), ethics-first monetization
- **CodeOS** — Phase 1 complete, 40/40 tests
- **FLAG-01** — Clarkson EEOC, attorney engaged

---

## Do Not

- Commit: `chaos/chaos_seed.json`, `chaos/session_log.json`, `chaos/prometheus_log.json`, `chaos/mnemos_vectors.db`, `.env`
- Redefine or renumber the 27 God Systems
- Expand scope without simplifying something else (GL7)
- Mutate state silently
- Run broad refactors unrelated to the task
