# Jarvis-Private Root Condense Plan

Date: 2026-07-24
Target repo: `hurrisonferd/Jarvis-Private`
Target ref checked: `origin/main`
Commit checked: `cbce951b`

## Evidence State

RETRIEVED + PLAN ONLY.

The local mirror was fetched from `origin main`. This file does not move, delete, or rewrite Jarvis-Private. It is a safe cave map for later consolidation.

Important working-tree note: the local `rooms/repos/private-repair` checkout currently reports many deleted paths, so it should not be used for direct edits until repaired or freshly cloned.

## Root Count

```text
root_dirs_total = 24
root_dirs_nondot = 23
```

Non-dot root folders:

```text
Canon
CodeOS
Evidence
GridTools
Jam Sesh
Living_Codex
MARCO-POLO
PachinkoBounce
Research
VISION
VoiceOS
docs
gameboy
identity
logs
rebuild
scripts
supabase
systemd
tests
trace_log
workers
workspaces
```

Root noise also visible:

```text
I
THE
We
cat
Grid
johnny
conversation_*.zip
test-write.md
test_delete.txt
boot_*.sh
*_daemon.py
*_watcher.py
{YOUR_ISO}_*.py
encoded checkmark folder
```

## Diagnosis

The root problem is not only folder count. The bigger problem is category mixing:

```text
canon
apps
voice runtime
tools
daemons
identity
logs
tests
evidence
old generated files
symbol scraps
```

All of these sit as peer doors. That makes important items hard to fish from the folder sea.

## Proposed Root Rooms

Keep root narrow and memorable:

```text
Canon/
Evidence/
Living_Codex/
VoiceOS/
GridTools/
apps/
runtime/
tools/
archive/
docs/
supabase/
tests/
README.md
AGENTS.md
ROOT-SIGNS.md
```

Optional stronger John-spice names:

```text
JFS/          # file-system/kernel layer, if promoted later
Yggdrasil/    # map/tree architecture, if extracted from Canon/Living_Codex
JNL/          # naming/address ledger, if promoted later
Dictionary/   # JD/Jarvis Dictionary, if made user-facing
rooms/        # old worlds and parked civilizations
```

Use these only when they become actual retrieval wins. Names are spells, but root names must earn rent.

## Move Buckets

### Keep At Root

```text
Canon
Evidence
Living_Codex
VoiceOS
GridTools
docs
supabase
tests
README.md
AGENTS.md
LICENSE
```

Reason: these are primary entryways, current substrate, or expected repo conventions.

### Move Under `apps/`

```text
PachinkoBounce -> apps/PachinkoBounce
gameboy -> apps/gameboy
```

Optional later:

```text
CodeOS -> apps/CodeOS
```

Only move CodeOS if references and docs are updated. It may be closer to a system than an app.

### Move Under `runtime/`

```text
logs -> runtime/logs
trace_log -> runtime/trace_log
workers -> runtime/workers
systemd -> runtime/systemd
rebuild -> runtime/rebuild
```

Reason: these are operational/runtime surfaces, not concept roots.

### Move Under `tools/`

```text
scripts -> tools/scripts
boot -> tools/boot
boot_*.sh -> tools/boot/
fleet_cleanup.py -> tools/maintenance/
scaffold_projects.py -> tools/scaffold/
*_daemon.py -> tools/daemons/
*_watcher.py -> tools/watchers/
gameboy_fleet_*.js/html -> tools/gameboy-fleet/ or apps/gameboy/
```

Reason: loose executables are useful, but root-level executable confetti makes the cave noisy.

### Move Under `archive/`

```text
Jam Sesh -> archive/jam-sesh
MARCO-POLO -> archive/marco-polo
Research -> archive/research
VISION -> archive/vision
conversation_*.zip -> archive/exports/
test-write.md -> archive/test-scraps/
test_delete.txt -> archive/test-scraps/
TEST-*.txt -> archive/test-scraps/
I -> archive/symbol-scraps/I
THE -> archive/symbol-scraps/THE
We -> archive/symbol-scraps/We
cat -> archive/symbol-scraps/cat
encoded checkmark folder -> archive/symbol-scraps/checkmark
```

Reason: these may matter historically, but they should not compete with active rooms.

### Review Before Moving

```text
identity
CodeOS
workspaces
Grid
johnny
LILITH.md
PATENT-OFFICE.md
KNOWLEDGE-INDEX.md
GRID-MAP.json
ARCHITECTURE-SPEC.md
JARVIS_STRUCTURE.md
```

Reason: likely high-value or heavily referenced. Make signs first, moves second.

## Safe Move Order

1. Fresh clone Jarvis-Private or repair the local worktree.
2. Create `ROOT-SIGNS.md` at repo root.
3. Add README signs to `apps/`, `runtime/`, `tools/`, `archive/`, and `rooms/`.
4. Move only obvious scraps and runtime folders first.
5. Run reference search for each proposed move:

```text
rg "old/path|FolderName"
```

6. Update README/root signs/indexes in the same commit as each move group.
7. Keep one commit per bucket: `runtime`, `tools`, `apps`, `archive`.
8. Do not move `Living_Codex`, `VoiceOS`, `Canon`, `Evidence`, `GridTools`, or `supabase` until the first pass has settled.

## Cave Law

```text
Many folders not evil.
Many equal doors with no map: evil.
Root is for portals, not storage.
Archive is not deletion.
Move with receipts.
```

