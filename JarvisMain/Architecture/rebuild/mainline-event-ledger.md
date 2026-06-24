# Mainline Event Ledger

**Status:** operating rule  
**Last updated:** 2026-06-24  
**Authority:** Raven final authority; GitHub main is canon; Supabase is runtime.

## Rule

`main` is the canonical branch. Work may happen on feature branches, but those branches are staging lanes only. A change is system truth when it lands on `main` and has a traceable ledger/event pointer.

## Mainline Path

1. Start from current `origin/main`.
2. Make the smallest coherent change on a branch.
3. Verify locally and, when relevant, against the cloud MCP endpoint.
4. Open/merge through the protected main path.
5. Record the event in the ledger.

No force-push over `main`. If local `main` diverges from `origin/main`, rebase/cherry-pick onto fresh `origin/main` in a clean worktree before publishing.

## Ledger Surfaces

- `audit/patch_ledger.json`: canonical patch/change register.
- `JarvisMain/Architecture/runtime/event-contract.md`: event schema and hard rules.
- Supabase `execution_trace` / `dex_events`: runtime event spine.
- Git commit hash: durable proof of what changed.

## Minimum Event Fields

Every meaningful change should be recoverable by:

- intent
- decision/authority
- execution commit
- verification result
- runtime event id when emitted
- follow-up debt, if any

## Rebuild Implication

If a behavior matters enough to rebuild, Git must contain its source, schema, or instruction packet. Supabase may prove it ran; Git must explain how to recreate it.
