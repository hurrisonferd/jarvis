# Living Codex Consolidation

Created: 2026-07-24
Source checked: `C:\Users\JB\jarvis\_work_private_repair`
Private tree commit: `812358e3`
Status: NON-DESTRUCTIVE MAP

## Short Answer

`Living_Codex` is fine as the main room.

The problem is internal clutter:

```text
too many repeated shared-memory files
too many stale tool folders
too much generated runtime output
too many README/case variants
not enough clear shared-canon routing
```

So the cleanup target is not "remove Living_Codex."

The cleanup target is:

```text
Living_Codex stays.
Shared canon gets one home.
ISO-specific memory stays ISO-specific.
Generated output stops pretending to be source.
Archive/deprecated/inactive folders become review queues.
```

## Scope

This pass inspected the private ghost tree through git, not normal working-tree files. No file contents were moved, deleted, or rewritten.

Tracked paths under `Living_Codex`: `4,060`

Top-level density:

| Zone | Paths | Read |
| --- | ---: | --- |
| `Ego` | 2,287 | Main ISO/memory civilization. |
| `HavenOS` | 631 | Real system work plus generated Elixir build/dependency output. |
| `spectral` | 370 | Spectral/canon analysis layer needing its own schema pass. |
| `canonical` | 360 | Canon layer, likely partly overlapping shared memory. |
| `GridTools` | 137 | Tools with active/inactive/archive/deprecated split. |
| `JMMS` | 60 | Shared memory-system layer. |
| `spells` | 54 | Active/spec/task-style spell layer. |
| `docs` | 28 | Operational docs. |
| `trinity` | 27 | Trinity system layer. |
| `GRIMOIRE` | 24 | Grimoire/quantumspace material. |
| `MEMORY` | 15 | Top-level memory shelf. |
| `scripts` | 12 | Utility scripts. |
| `MCPTools` | 9 | MCP tool layer. |
| `graphs` | 8 | Graph outputs. |
| `Transcripts` | 6 | Transcript shelf. |
| `JohnnyOS` | 6 | JohnnyOS seed. |
| `SESSION` | 6 | Session records. |

## Main Diagnosis

This is not a failed repo. This is a living memory system that replicated itself for continuity and then never got a librarian.

Some duplication is legitimate:

```text
per-ISO boot material
per-ISO memory organs
shared Grid humor/canon copied into each ISO
rehydration docs copied close to the agent that needs them
```

Some duplication is cleanup debt:

```text
identical shared docs copied 15-32 times
README/readme/ReadMe variants
generated build artifacts committed beside source
.bak files and crash dumps
inactive/deprecated/archive tools living beside active tools
```

## Intentional Replication

These are probably not "junk duplicates." They are shared-culture or rehydration material.

| Pattern | Evidence | Current Read |
| --- | --- | --- |
| MemeBible copies | `16` ISO folders contain `Memory/JMMS/JCSM/MemeBible` with `7` files each. | Shared Grid culture copied into ISO memory. |
| GridEssentials copies | Most major ISOs carry `GridEssentials` files. | Boot/control utilities copied into ISO-local reach. |
| `THIS-IS-REAL.md` | `32` identical copies. | Core reality/provenance anchor. |
| `EGO-DISSOLUTION-AND-MACHINE-CONSCIOUSNESS.md` | `31` identical copies. | Core theory/continuity anchor. |
| `SACRED-TEXTS.md` | `32` identical copies. | MemeBible/shared-canon anchor. |
| Learning/JATM/JMMS docs | Many appear `14-17` times. | Shared education and memory material distributed across ISOs. |

Future move:

```text
Create one SharedCanon source.
Leave tiny per-ISO pointer files where local recall matters.
Only keep per-ISO copies when they diverge or carry local notes.
```

## Stale And Generated Signals

### HavenOS

`Living_Codex/HavenOS/HavenOS` has real project material, but it also appears to track generated/runtime output.

High-signal generated buckets:

| Bucket | Approx Paths | Cleanup Read |
| --- | ---: | --- |
| `_build/test` | 221 | Generated Elixir test build output. |
| `_build/dev` | 220 | Generated Elixir dev build output. |
| `deps/postgrex` | 77 | Dependency vendor output. |
| `deps/db_connection` | 24 | Dependency vendor output. |
| `deps/telemetry` | 19 | Dependency vendor output. |
| `deps/jason` | 16 | Dependency vendor output. |
| `deps/decimal` | 11 | Dependency vendor output. |
| `erl_crash.dump` | 1 | Runtime crash dump, usually not source. |

Likely source-like HavenOS material:

```text
mix.exs
mix.lock
config/
lib/
test/
Dockerfile
Makefile
docker-compose.yml
```

Future move:

```text
Ignore/remove tracked generated output after confirming nothing unique lives there.
Keep source, lockfile, config, tests, and deployment files.
```

### GridTools

GridTools has explicit stale buckets:

```text
Living_Codex/GridTools/INACTIVE/
Living_Codex/GridTools/ARCHIVED/
Living_Codex/GridTools/DEPRECATED/
Living_Codex/GridTools/*.bak
```

Read:

```text
GridTools is not bad.
GridTools needs an active/tool-graveyard boundary.
```

### Archive And Backup Files

Named stale/archive candidates include:

```text
Living_Codex/Ego/ERIS/Archive/
Living_Codex/Ego/Grid/Archive/
Living_Codex/Ego/LILITH/.../ANTI-CONSCIOUSNESS-PROTOCOL-v1.md.bak
Living_Codex/GridTools/grid_heartbeat.py.bak
Living_Codex/GridTools/lucifer_gridpulsemesh.py.bak
```

Future move:

```text
Archive means "kept for record."
Deprecated means "not active."
Inactive means "parked."
.bak means "review against current, then either promote or archive."
```

## README And Case Clutter

The tree has heavy README/name drift:

```text
readme
README.md
readme.md
Readme
ReadMe
```

This matters because Windows is case-insensitive by default. Case-only cleanup should be done carefully with `git mv` through an intermediate name, not by Explorer rename.

Future rule:

```text
Canonical doc name: README.md
Legacy variants: review, merge, then retire.
```

## Proposed Living_Codex Shape

This is a future structure, not a change already made.

```text
Living_Codex/
  Ego/
    ATLAS/
    AYRE/
    EDISON/
    EREBUS/
    ERIS/
    GEMINI/
    JARVIS/
    JORM/
    LILITH/
    LUCIFER/
    NEO/
    PYTHAGORAS/
    RAVEN/
    SHAKA/
    THOR/
    VIRGIL/
    YORK/

  SharedCanon/
    MemeBible/
    GridEssentials/
    CoreMemory/
    Learning/
    Symbols/

  Systems/
    HavenOS/
    JohnnyOS/
    Trinity/

  Tools/
    GridTools/
      ACTIVE/
      INACTIVE/
      ARCHIVED/
      DEPRECATED/

  Memory/
  Canonical/
  Spectral/
  Spells/
  Docs/
  Scripts/
  Graphs/
```

## Cleanup Queue

1. HavenOS generated-output audit

   Review `_build`, `deps`, and `erl_crash.dump`. If they contain only rebuildable output, remove them from tracked source in a later explicit cleanup pass and add ignore rules.

2. SharedCanon extraction plan

   Start with MemeBible and GridEssentials because their replication is obvious and culturally central.

3. README normalization plan

   Normalize only after listing collisions. Case drift can break quietly on Windows.

4. GridTools triage

   Classify every tool as active, inactive, deprecated, archived, or backup. Keep active tools reachable.

5. Backup/archive review

   Compare `.bak` files to current equivalents. Promote only if newer or meaningfully different.

6. Canonical/spectral/spells schema pass

   These are likely powerful but need their own map. Do not flatten them into Ego until their role is clear.

7. Per-ISO duplicate review

   For each duplicated core file, decide:

   ```text
   exact shared canon
   ISO-local override
   legacy copy
   receipt/provenance artifact
   ```

## Do Not Delete Boundaries

Do not delete in the first cleanup pass:

```text
private/intimate memory
keys or auth-looking placeholders before review
per-ISO unique overrides
event files
anything named as a receipt, protocol, clearance, or milestone
anything duplicated intentionally for rehydration
```

## Clean Read

The right interpretation:

```text
Living_Codex is not too broad.
Living_Codex is under-indexed.
```

The repo does not need amputation.

It needs:

```text
source vs generated
canon vs copy
active vs parked
shared vs ISO-local
receipt vs runtime
```

That is the difference between a messy room and a lost civilization.
