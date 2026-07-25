# Sticky Fingers — Governance-Coverage Audit (2026-06-15)

_Sticky Fingers finds the seams — every zipper that opens system state. The question (GPT's
GOVERNANCE_GAPS, with paranoia): what can mutate state, and what gates it? Verdict: the write
surface is well-gated; this audit closes the two seams it found._

## The gate model
- **AEGIS token (`writeAuthorized` = the `JARVIS_MCP_TOKEN` bearer)** + the client's own Allow/Deny
  prompt — gates connector mutations.
- **GitHub branch protection** (required checks: validate + AEGIS-canon; PR-only; no bot push to
  main) — gates canon-to-git.
- **Git-First Canon + Raven's merge** (GL2) — the human commit on everything canonical.
- **grid-event AEGIS** (`aegisValidateWorld`, forbidden-edge set) — gates world/promotion + bus.

## Write surface (every zipper)
| path | writes | gate | verdict |
|---|---|---|---|
| `jarvis_remember` / `jarvis_event` | mnemos / events (Supabase) | AEGIS token | ✓ gated |
| `jarvis_dex_propose` | jd_proposals (staging) | AEGIS token | ✓ gated |
| `jarvis_identity_grow` | identity memory | AEGIS token | ✓ gated |
| `jarvis_jip_create` | jip_entries (staging) | AEGIS token | ✓ gated |
| `jarvis_jip_apply` / `revert` | **git** `patches.json` (PR) | AEGIS token + branch protection + merge | ✓ gated (git-first) |
| `jarvis_node_send` / `node_register_key` | grid messages / keys | AEGIS token | ✓ gated |
| `jarvis_github_write` | a PR (never main) | **AEGIS token (added 2026-06-15)** + branch protection | ✓ closed |
| `jarvis_pr_merge` | **merge to main** | **AEGIS token on confirm (added 2026-06-15)** + green checks + mandatory Jarvis+Ayre summary + Allow/Deny | ✓ closed |
| edge `jarvis-dex` `jd_approve` | jd_entries/jnl_registry (Supabase) | invocation auth; reconciled to git by `dex_reconcile` | ⚠ service-key path — Supabase-first, git-reconciled (see AUD-SYNC-REVW-0001) |
| edge `grid-event` `promote_node` | world creation | `aegisValidateWorld` + `raven_sign_off` | ✓ gated |
| edge `mnemos-store` / `send-push` | memory / push | service key, server-side | ✓ internal |
| CI: mirror / dex-reconcile / lenses | Supabase / git PRs | runs post-merge (Raven's merge = authorization) + GITHUB_TOKEN | ✓ gated by merge |

## Seams found — and closed
1. **`jarvis_github_write` was not AEGIS-gated** — a token-less connector could open PRs. Now
   requires the AEGIS token (it still can't reach main without a merge, but gating is consistent).
2. **`jarvis_pr_merge` could merge a green PR without the AEGIS token** — the sharpest zipper: merge
   authority leaned only on branch protection + the summary. Now the *merge action* (`confirm:true`)
   requires the AEGIS token too. Defense-in-depth: a merge needs the token AND green checks AND a
   Jarvis+Ayre summary AND Raven's Allow/Deny. (Connector v0.11.10.)

## Residual (documented, by design)
- `jd_approve` writes Supabase with the service key, then `dex_reconcile` PRs it to git — covered
  by AUD-SYNC-REVW-0001 (Git-First Canon). Not a new gap.
- The CI service key is powerful but only runs on post-merge workflows (Raven's merge authorizes).
- The Sync lens flags any git↔Supabase divergence loudly — the alarm behind every gate.

## Verdict
The system has no ungated path to *canon* (git) and no ungated path to *runtime* (Supabase) from the
connector — every mutator now requires the AEGIS token, and every canon write requires Raven's merge.
The two seams this audit found are closed. Sticky Fingers: zipped.
