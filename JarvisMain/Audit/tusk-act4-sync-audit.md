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

## The reconcile bridge (correction to the first pass — ground truth)
`scripts/dex_reconcile.py` (run by `dex-reconcile.yml`) is the **Supabase → git** return leg:
it pulls ACTIVE `jd_entries` that have **no local file** into `jd/dynamic.json` (or materializes
project files), regenerates the substrate, and **opens a PR** (exit 2). So a connector-approved
*new* object is NOT stranded in Supabase — it reconciles back to git, Raven merges, git becomes
truth. The full loop: `dex_propose → jd_approve (Supabase) → dex_reconcile (PR) → merge → mirror`.
This is a real, working Supabase→git bridge — a baby "Love Train": it redirects divergence into a
PR instead of letting it corrupt git.

## The cracks (what the bridge does NOT cover)
| path | where | writes | covered by reconcile? |
|---|---|---|---|
| `jd_approve` (new object) | jarvis-dex 245–293 | upsert `jnl_registry` + `jd_entries` | **YES** — dex_reconcile adds missing entries to git via PR. Transient divergence, self-healing. |
| `jarvis_jip_apply` (field edit) | jarvis-mcp 1631–32 | patch existing `jd_entries` fields | **NO** — reconcile only adds entries with no local file; it does not diff fields of existing ones. So the edit is Supabase-only → **overwritten by git on the next mirror** (silent loss). The real remaining hole. |
| `jarvis_jip_revert` | jarvis-mcp 1650 | patch existing `jd_entries` | **NO** — same. |
| `sync_supabase.py` | mirror | upsert, **no delete** | n/a — git-deleted object lingers in Supabase (stale ghost). Low risk (JMS rarely deletes). |

## Severity (corrected)
- **New objects: covered.** `jd_approve` → `dex_reconcile` PR → git. Git becomes the whole truth
  once the reconcile PR merges. The earlier "Supabase holds canon git lacks, permanently" was wrong.
- **Field edits on existing objects: the real hole.** `jip_apply`/`revert` change fields in Supabase
  that reconcile never pulls back (the file already exists), so the mirror silently reverts them. A
  `jip_apply` can *look* applied and vanish on the next merge. Narrow, but it's the one to close.

## How to combat "git always wins" properly
"Git always wins" is the *correct* behavior — the danger is only when a Supabase change never
reached git, so git's overwrite *loses* it. The proper defense is therefore NOT to weaken git;
it's to **guarantee every Supabase write has a git-return path**, so winning never destroys data,
and to **make any residual divergence loud**:
1. **Field-level reconcile.** Extend `dex_reconcile.py` to also diff fields of *existing* entries
   (not just add missing files), so `jip_apply` edits ride a PR back to git like new objects do.
   This closes the one real hole using the bridge that already works.
2. **`jip_apply`/`revert` → git-first** (alternative to #1): apply the delta to the git JD entry via
   the github-write PR; the Supabase patch is the runtime *preview*, reconciled by the merge.
3. **Divergence detector (the loud alarm).** A check (CI or an Omni *Sync* lens) that reads BOTH
   stores and flags any `jd_entries` row where Supabase ≠ git. Silent overwrite becomes a visible
   flag — the safest failure mode (diverge loudly, never revert quietly).
4. **Mirror authoritative (optional).** `sync_supabase.py` deletes Supabase rows absent from git,
   so deletions propagate and no ghost survives.

## Do the Omni tools help audit?
Yes — but on a different axis. The Omni/fusion lenses (Omni-JMS, Orphan, Drift) audit the
**git-side structure** (orphans, coupling, drift) because they project over git-derived
`graph.json`/registry. They are real auditing — of *one* store. **Sync** auditing is cross-store
(git vs Supabase), which they don't do today. The missing piece in the hoped-for stack
(JARVIS + Ayre + god systems + Omni-JMS + grimoire + fusion) is exactly **one Sync/reconcile lens**
that diffs the two stores. Add it and the stack audits both structure *and* sync.

## How JARVIS guides by this
Git-First Canon is now in `CLAUDE.md` (Governed Workflow) — always-loaded, so every stream routes
canonical writes through git. The grimoire/verbs surface points "propose a change" at
`jarvis_github_write` (git), not at a Supabase patch. The streams guide Raven to git-first by default.
