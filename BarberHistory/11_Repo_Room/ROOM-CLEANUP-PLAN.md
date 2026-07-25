# Room Cleanup Plan

Created: 2026-07-24
Status: ACTIVE

## Guiding Principle

```text
Make it findable.
Then make it shippable.
Then make it pretty.
```

## Phase 1 - Contain The Mirrors

Done:

```text
_work_public_main/
_work_private_repair/
Jarvis-Private/
Jarvis-Private-work/
```

These are now ignored by the current public repo so they stop appearing as accidental untracked source.

## Phase 2 - Keep BarberHistory As The Index

Active:

```text
BarberHistory/
```

This is the shelf for:

```text
project maps
evidence maps
repo room maps
mythos maps
AI/Grid maps
medical/legal context maps
```

## Phase 3 - Private Repo Recovery

Do not mutate `_work_private_repair` yet.

Next safe move:

```text
build indexes from git tree
recover targeted files by `git show`
decide later whether to fresh-clone private repo outside public repo folder
```

Why:

```text
4,982 files exist in HEAD.
4,982 files are currently marked deleted in the working tree.
That is recoverable but not a normal cleanup surface.
```

## Phase 4 - Public Mirror Commit Split

For `_work_public_main`, split dirty work into review groups:

1. Audit files.
2. JORM/Lucifer records.
3. Bridgekeeper active/inactive script promotion.
4. Supabase MCP/RLS changes.
5. Script README updates.

No blanket commit.

## Phase 5 - Root Public Repo

Current public root is small: 136 tracked files.

Treat it as:

```text
workbench
```

Not:

```text
storage locker
```

Keep only:

```text
active source
BarberHistory
small docs
config needed for current runnable app
```

Visible local decision item:

```text
.claude/
```

It contains Claude command/settings material and no secret-looking values were found in the inspected settings file. Leave visible until Raven decides whether it is project config to keep or local tool state to ignore.

## Phase 6 - Future Real Cleanup

After the maps are stable:

```text
create SharedCanon/MemeBible source of truth
create one ProjectCard per major project
reconcile Supabase live vs public/private/local source
decide whether BarberHistory belongs in public repo, private repo, or its own repo
fresh-clone private repo outside the public workspace
```

## Do Not Do Yet

```text
delete mirrors
bulk restore private repair
publish private repair contents
move secret-bearing files
merge BarberHistory into public docs without review
commit Supabase auth changes without security review
```
