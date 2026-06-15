# TUSK ACT 4 — Git ↔ Supabase Sync Audit (2026-06-15)

_The audit that spins through every defense to ground truth. Commissioned by Raven 2026-06-15:
"is Supabase perverting what we actually use?" Verdict: the direction is right, but two creation
paths exist and one of them makes Supabase the origin of canon. The law below closes it._

## The law (Raven-verdicted 2026-06-15) — **Git-First Canon**
> Every **canonical** write — a JD object, its `jd_entries`/`jnl_registry` row, any change to
> definition/parent/status — lands in **git first** (file → `seed.py` → commit/PR → merge), and
> the mirror syncs git → Supabase afterward. **Supabase never originates canon.** Supabase is the
> READ/runtime mirror plus its own native live tables (`dex_events`, `mnemos_memories`,
> `jd_proposals`) — events, memory, and staging, which are *meant* to live only there. A connector
> "approve" or "apply" must **propose a git change**, not patch Supabase canon directly.

## How sync works today
- **Truth:** `JarvisMain/yggdrasil/jd/entries/*.md` + `lal/*.json` (git).
- **Mirror:** on every push to `main`, `yggdrasil-validate.yml` runs `validate.py` then
  `sync_supabase.py --push` — a PostgREST **upsert** (`on_conflict=jnl`, merge-duplicates) of
  `jnl_registry` + `jd_entries` from git → Supabase. So for any object **git has**, git overwrites
  Supabase each merge (git wins). Good — as far as it goes.

## The cracks (canon written to Supabase outside git)
| path | where | writes | problem |
|---|---|---|---|
| `jd_approve` | jarvis-dex 245–293 | upsert `jnl_registry` + `jd_entries` | **new object lands in Supabase, never git.** Mirror only *pushes* git's rows, so it's never reconciled back → Supabase holds canon git lacks (true divergence). |
| `jarvis_jip_apply` | jarvis-mcp 1631–32 | patch `jd_entries` + `jnl_registry` | field change is Supabase-only → **overwritten by git on the next mirror** (silent loss). |
| `jarvis_jip_revert` | jarvis-mcp 1650 | patch `jd_entries` | same — ephemeral. |
| `sync_supabase.py` | mirror | upsert, **no delete** | a git-deleted object **lingers** in Supabase (stale ghost). Low risk (JMS rarely deletes). |

## Severity
- **Git can't be permanently perverted** for objects it *has* — the upsert re-asserts git every merge.
- **But git is not the *whole* truth**: `jd_approve`'d objects exist only in Supabase, and
  `jip_apply` edits silently revert. A change can *look* landed in the connector and not be real.
  That is exactly the failure "the connector is home" must not have.

## Remediation (the build that makes Git-First Canon real)
1. **`jd_approve` → git-first.** On approval, write the JD entry `.md` to git (commit/PR via the
   github-write path), let the mirror sync. Supabase upsert becomes a *preview*, not the origin.
2. **`jip_apply` / `jip_revert` → git-first.** Apply the delta to the git JD entry (PR); Supabase
   patch is the immediate runtime preview, reconciled by the merge mirror — never the source.
3. **Mirror authoritative (optional).** Make `sync_supabase.py` delete Supabase rows absent from
   git, so deletions propagate and no ghost survives.
4. **Guard rail.** Until 1–2 land, the connector descriptions must say so: these tools *preview*
   in Supabase; the canonical change is a git PR. Never present an ungit'd patch as "applied."

## How JARVIS guides by this
Git-First Canon is now in `CLAUDE.md` (Governed Workflow) — always-loaded, so every stream routes
canonical writes through git. The grimoire/verbs surface points "propose a change" at
`jarvis_github_write` (git), not at a Supabase patch. The streams guide Raven to git-first by default.
