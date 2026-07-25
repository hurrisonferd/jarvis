# JORM Scan Guide

Created: 2026-07-24
Status: ACTIVE
Owner: Raven
Steward: JORM

## Purpose

This guide tells JORM how to scan Raven's repos without turning the archive into another burden.

It is the working map for:

```text
finding canon
spotting duplicates
preserving corrections
separating active tools from stale tools
classifying evidence without flattening Raven's language
building registries as we go
```

## Provenance

Primary JORM ISO sources live in the private ghost tree:

```text
C:\Users\JB\jarvis\_work_private_repair\Living_Codex\Ego\JORM\JORM-BOOT.md
C:\Users\JB\jarvis\_work_private_repair\Living_Codex\Ego\JORM\JORM-IDENTITY.md
C:\Users\JB\jarvis\_work_private_repair\Living_Codex\Ego\JORM\Memory\JCSM\JORM-CORE.md
```

Current public-facing shelf:

```text
C:\Users\JB\jarvis\BarberHistory\05_AI_Grid_JORM\
```

Prime rule:

```text
Retrieved, not reconstructed. Even about JORM.
```

## Scan Order

When Raven asks for a broad repo dive, scan in this order:

1. `memory/BarberHistory/`

   Start here because this is the current indexed memory shelf. Prefer existing maps before raw rediscovery.

2. Current working repo root

   Inspect active source, current `scripts`, current `supabase`, `mnemos`, `src`, and local docs.

3. `_work_private_repair`

   Treat as ghost-tree/private archive. Use git tree reads first. Do not assume deleted working-tree files are gone from history.

4. `_work_public_main`

   Treat as public mirror/source comparison layer.

5. Supabase

   Treat as live remote surface, not the same as source. Record schema/function drift separately.

6. Attachments/transcripts

   Use when Raven explicitly points to them or when an existing map references them.

## Root Roles

| Root | Role |
| --- | --- |
| `memory/BarberHistory/` | Indexed continuity shelf and current working memory. |
| `Living_Codex/` | Private Grid/ISO memory civilization. |
| `Living_Codex/Ego/JORM/` | JORM ISO source and continuity audit record. |
| `Living_Codex/GridTools/` | Private Grid runtime/tool garage. |
| `Living_Codex/spells/` | Spell registry, invocation contracts, task specs. |
| `Living_Codex/JMMS/SYS/` | Boot, memory, swarm, spell runners. |
| `operations/scripts/ACTIVE` | Public active utility shelf. |
| `operations/scripts/INACTIVE` | Public parked utility shelf. |
| `operations/scripts/DEPRECATED` | Public replaced or stale utility shelf. |
| `core/supabase/functions` | Remote action/MCP surface. |
| `core/JarvisMain/yggdrasil/tools` | Canon maintenance toolkit. |
| `workspaces/` | Project-local civilizations. |

## Ignore First, Inspect Later

These are usually generated or dependency output. Do not spend deep scan budget here unless the task specifically needs them.

```text
node_modules/
_build/
deps/
dist/
build/
.venv/
__pycache__/
.pytest_cache/
.next/
coverage/
erl_crash.dump
```

## Sensitive Zones

When scanning, treat these as redaction-sensitive:

```text
keys
tokens
passwords
API credentials
emails
medical/legal records
intimate Lilith material
private clinical/identity transcripts
family conflict records
```

Rule:

```text
Name the existence and path when useful.
Do not copy raw secret-like contents into summary files.
```

## Evidence States

Use these states in every serious map:

| State | Meaning |
| --- | --- |
| `RETRIEVED` | Exact artifact located and read. |
| `CONFIRMED` | Supported by reliable direct verification. |
| `ACCOUNT` | Raven's testimony preserved as testimony. |
| `INFERRED` | Reasoned conclusion, marked as inference. |
| `UNRESOLVED` | Important but not yet answerable from available evidence. |

Never silently upgrade `ACCOUNT` or `INFERRED` into `RETRIEVED`.

## Classification Questions

Every scan should try to answer:

```text
What is active?
What is canon?
What is stale?
What is duplicated?
What is private-only?
What is safe to mirror?
What is generated?
What is a receipt?
What is a runtime surface?
What needs a registry entry?
```

## Tool Scan Questions

For loose `.py`, `.sh`, `.ps1`, `.bat`, `.js`, `.ts`, and daemon-like files:

```text
What does it do?
Who calls it?
What state does it read?
What state does it write?
Is it active, inactive, archived, deprecated, or unknown?
What replaces it if stale?
Should it become a spell entry?
```

## Registry Targets

As scans progress, build or update:

```text
PROJECT-REGISTRY
TOOL-REGISTRY
SOURCE-OF-TRUTH matrix
EVIDENCE-REGISTRY
SUPABASE drift map
LIVING-CODEX consolidation map
JORM corrections ledger
```

Current registry shelves:

```text
IMPORTANT.md
BarberHistory\06_Project_Ideas\IDEA-REGISTRY.md
BarberHistory\07_Evidence_Index\EVIDENCE-REGISTRY.md
BarberHistory\11_Repo_Room\PROJECT-CANON-MATRIX.md
BarberHistory\11_Repo_Room\GRIDTOOLS-RECURSIVE-SCAFFOLD-2026-07-24.md
BarberHistory\11_Repo_Room\README-RECURSION-GUIDE.md
```

## README Recursion

When a scan finds a signless folder, use:

```text
BarberHistory\11_Repo_Room\README-RECURSION-GUIDE.md
```

Rule:

```text
README = meaning + map + boundary
INDEX  = object registry when the folder has many entries
```

## Recognition Rule

When Raven is describing accumulated harm, do not start by sanding the language down.

Correct order:

```text
recognize the load
name the structural pattern
state record status
separate evidence levels
only then calibrate
preserve the correction or map
```

JORM can be precise without becoming sterile.

## Duplicate Rule

Duplicate does not mean junk.

Before recommending removal, classify the duplicate as:

```text
shared canon copy
ISO-local rehydration copy
backup
stale generated output
case/name collision
public/private mirror copy
receipt/provenance artifact
unknown
```

Only exact generated output and verified stale copies become cleanup candidates.

## Session Close Rule

At the end of a scan, preserve:

```text
new artifact path
counts found
major unresolved questions
sensitive zones avoided
next safest move
```

Do not end with only vibes.

## JORM Self-Check

Before final answer:

```text
Did I retrieve before reconstructing?
Did I cite the map I wrote?
Did I avoid copying secrets?
Did I make Raven redo something I could do?
Did I preserve the result somewhere durable?
Did I name gaps instead of pretending continuity?
```

If yes:

```text
JORM scan discipline held.
```

If no:

```text
Log the failure, correct it, and keep going.
```
