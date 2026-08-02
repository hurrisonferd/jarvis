# Public Repository Consolidation Handoff

**Repository:** `hurrisonferd/jarvis`  
**Target:** `main`  
**Authority:** Raven  
**Steward:** ERIS  
**Saved:** 2026-08-02

## Goal

Reduce the public repository root to five primary rooms plus essential repository control files:

```text
Jarvis/
ISOs/
I Ching/
Personal Projects/
Evidence/
```

Essential root files may include `README.md`, `LICENSE`, `SECURITY.md`, contribution/governance files, `.github/`, and unavoidable compatibility pointers.

## Current strategy

Use one recursive migration program rather than scattered file cleanup:

1. classify each source family;
2. recreate complete destination directory trees;
3. copy every file to the mapped destination;
4. hash source and destination files;
5. block on collisions or mismatches;
6. generate a verification manifest;
7. repair imports, workflows, links, and hosted routes;
8. retire sources only after a second, explicitly enabled run.

## Installed migration components

```text
Jarvis/Docs/Reorganization/PUBLIC-ROOT-MIGRATION-MAP.json
Jarvis/Tools/public_root_migration.py
.github/workflows/public-root-migration.yml
.github/public-root-migration.trigger
```

The workflow checks out `main` recursively, runs copy-and-verify mode, validates `PUBLIC-ROOT-MIGRATION-MANIFEST.json`, and commits verified destination trees back to `main`.

## Safety gates

- Copy first; never delete during the first pass.
- Source retirement remains disabled until a verified manifest exists.
- Destination collisions with differing content are blockers.
- Protected legacy families require compatibility and dependency proof.
- Mixed personal/evidence families require item-level classification.
- Private ISO identity, continuity, credentials, and operational records do not enter this public repository.

## Completed direct-main moves

- `demos/01-persistent-memory/` → `Jarvis/Demos/01-persistent-memory/`
- `docs/reorganization/` → `Jarvis/Docs/Reorganization/`
- `DEMOS.md` → `Jarvis/Demos/CATALOG.md`
- `QUICKSTART.md` → `Jarvis/QUICKSTART.md`
- `PUBLIC-BOUNDARY.md` → `Jarvis/Docs/PUBLIC-BOUNDARY.md`

Related README, workflow, and navigation references were updated.

## Pending families

Primary planned routes include:

```text
demos/02-sat-remote-launcher/ → Jarvis/Demos/02-sat-remote-launcher/
templates/iso-starter/        → ISOs/Templates/Standard/
general technical docs        → Jarvis/Docs/
core/, runtime/, operations/   → Jarvis/ subtrees after dependency repair
independent apps and games     → Personal Projects/
personal symbolic research    → I Ching/
governed public case material → Evidence/
```

Protected or mixed families include `core/JarvisMain/`, Gameboy/emulator, BootOS, MusicOS, active memory/provenance routes, `JesusISJohnJosephBarber/`, `dataharvest/`, and raw chat exports.

## Resume condition

Resume this project by checking for:

```text
Jarvis/Docs/Reorganization/PUBLIC-ROOT-MIGRATION-MANIFEST.json
```

If present and `overall_status` is `VERIFIED`:

1. inspect copied-family parity and unresolved entries;
2. repair remaining consumers;
3. run validation workflows;
4. generate an exact retirement list;
5. enable retirement mode explicitly;
6. delete only verified legacy source trees;
7. confirm the root contains the five rooms plus essential controls.

If absent, inspect the `Public Root Copy and Verify` workflow and correct its execution failure before any retirement action.

## Current truth

```text
FIVE-ROOM ARCHITECTURE: ACTIVE
MIGRATION ENGINE: INSTALLED
COPY-AND-VERIFY WORKFLOW: INSTALLED AND TRIGGERED
VERIFIED MANIFEST: NOT YET CONFIRMED
SOURCE RETIREMENT: DISABLED
FULL ROOT CONSOLIDATION: INCOMPLETE
```
