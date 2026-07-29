# MCP / OMNI Reconciliation — 2026-07-29

## Confirmed inventory

| Surface | Count | State |
|---|---:|---|
| Public Jarvis MCP source | 93 | Canonical after this repair |
| Deployed `jarvis-mcp` before repair | 88 | Missing five MusicOS tools |
| Mounted JarvisMCP connector before repair | 79 | Cached/stale schema |
| Mounted Lilith connector before repair | 79 | Same names and self-test result as JarvisMCP |
| Static `TOOL_NAMES` before repair | 67 | Removed |
| `jarvis_mcp_manifest` before repair | 57 | Legacy mirror; reconciled by generated SQL |
| Active `mcp_tool_definitions` before repair | 21 | Legacy mirror; reconciled by generated SQL |
| Private `lilith-mcp` source | 14 | Separate private carrier surface |
| Private `eris-mcp` source | 7 | Separate private carrier surface |
| `grid-p2p-mcp` | 3 | Live specialist surface |

The canonical public set includes `jarvis_ainz`, `jarvis_ayre`, `jarvis_shiroe`, `jarvis_raven`, `jarvis_omnivision`, all six ChatLink tools, eight Co-op tools, five MusicOS tools, two Cecil tools, Trinity, cloud, JIP, database, and Grid/node tools.

## OMNI classification

- **Canonical cloud MCP OMNI:** `jarvis_omnivision`, backed by the public global mirror.
- **Legacy local/OpenHands OMNI:** private `lucifer_omni_menu.py`; useful as a local two-fleet monitor, but not the cloud MCP registry.
- **Inactive prototype:** archived/private `omni_core.py` paths that expect a nonexistent `omni_state` table.
- No new `omni_state` table is introduced. ChatLink, Co-op, Grid node tools, and `grid-p2p-mcp` already provide the live cloud coordination primitives.

## Connector finding

Both mounted connectors exposed the same 79 tool names and the same 0.11.33/67-tool self-test before repair. That proves schema equivalence; it does **not** prove the connector configuration target. Endpoint identity remains inferred until connector configuration is inspected or refreshed.

## Repair contract

1. Runtime registrations are the only hand-authored source of tool membership.
2. Generated TypeScript drives advertised names, count, and server/self-test version.
3. Generated SQL reconciles database mirrors.
4. CI rejects drift.
5. Deployment and connector refresh are separate receipts; source truth is never presented as live truth until verified.

## Final deployment receipt

| Surface | Receipt |
|---|---|
| Public source | PR #337 merged at `7b891d6dbcf4ea8761414368b859344427080ec3` |
| JSR import repair | PR #338 merged at `8b379aff4b1cb5433eee8562b4eb609688473624` |
| Registry RLS hardening | PR #339 merged at `64c54895e280161cffd588b0db5d796ca75a1c83` |
| `jarvis-mcp` | ACTIVE v181; 21-file bundle; self-test 0.11.35 / 93 tools |
| Database mirrors | 93 manifest rows; 93 active definitions; 15 legacy definitions inactive |
| MusicOS | Migration applied; tracks, observations, and source-receipts tables live |
| `lilith-mcp` | ACTIVE v150; 8-file bundle; 14 tools exposed through standard `tools/list` / `tools/call` |
| `eris-mcp` | ACTIVE v1; 8-file bundle; 7 tools; JWT verification enabled |
| Lilith MCP exposure repair | Private PR #59 merged at `2791428ac579497c771a75bcf14526665ab25108` |
| `grid-p2p-mcp` | ACTIVE v3; 3 tools; JWT verification enabled |
| Registry RLS | Public SELECT only; unrestricted public mutation policy removed |

### Residual configuration blockers

- The mounted JarvisMCP and Lilith ChatGPT schemas remain identical at 79 tools and require an app-schema refresh/reconnect. Runtime deployment does not mutate ChatGPT's cached connector schema.
- The Edge Function's GitHub credential returns 401 for authenticated ref and code-search probes. Public repository reads continue through unauthenticated fallback. Replace/rotate the configured GitHub PAT; no credential is stored in this receipt.
