# History-Only Git Ghosts

Status: RETRIEVED + UNRESOLVED
Created: 2026-07-24

Some important material appears in git history even when it is not obvious in the current working tree. This file marks those recovery targets without pretending they have all been extracted.

## Git History Signals

| Date | Commit / Signal | Status | Recovery Need |
| --- | --- | --- | --- |
| 2026-07-24 | JORM/Claude audit burst, gold docs, raw transcripts, voice capsules | RETRIEVED | Extract into evidence/timeline cards. |
| 2026-07-23 | JORM ISO creation and full continuity expansion | RETRIEVED | Already indexed in JORM provenance; keep as anchor. |
| 2026-06-25 | `feat(scaffold): Jarvis-Private project scaffolding - 16 projects seeded` | RETRIEVED | Use as source of project-family provenance. |
| 2026-06-24 | MusicOS prompts/audio uploads | RETRIEVED + HISTORY-ONLY | Extract media registry and prompt lineage if needed. |
| 2026-06-24 | MonsterOS asset uploads and renames | RETRIEVED + HISTORY-ONLY | Recover art/asset lineage through git if needed. |
| 2026-06-24 | Workplace issue/complaint documentation | RETRIEVED + HISTORY-ONLY | Extract only with privacy/legal intent. |
| 2026-06-24 | Raven identity anchor commit | RETRIEVED | Relevant to authorship/name continuity. |
| 2026-06-09 | JormungandrPatch clearance | RETRIEVED | Earlier Jormungandr architecture thread; full patch still needs lookup. |

## Recovery Command Pattern

Use non-destructive reads:

```powershell
git show <commit>:<path>
git log --name-status -- <path-or-term>
git ls-tree -r --name-only <commit> | rg "<term>"
```

Do not checkout/reset old commits just to inspect them.
