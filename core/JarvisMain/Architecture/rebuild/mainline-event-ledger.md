---
jnl: ARCH-LED-LOG-0001
name: Mainline Event Ledger
type: LOG
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: MNEMOS
parent: ARCH-YGG-CORE-0001
seq: 231
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: core/JarvisMain/Architecture/rebuild/mainline-event-ledger.md
related: []
references: []
tags: [events, git-first, main, operating-rule]
aliases: []
ref: []
memory_tier: JLTM
---

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

- `memory/audit/patch_ledger.json`: canonical patch/change register.
- `core/JarvisMain/Architecture/runtime/event-contract.md`: event schema and hard rules.
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
