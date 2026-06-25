# MonsterOS

**JNL:** PROJ-MONS-BIO-0001
**Status:** ACTIVE
**JARVIS repo:** `JarvisSide/Projects/MonsterOS/` (canonical spec, governed)
**This repo:** development workspace, game assets, monster designs

## What
RGB monster encoding system for Pachinko Bounce: R=Power, G=Rhythm, B=Range.
26 unique monster species catalogued with concept art, stats, abilities.

## Current state
- **26 monsters** catalogued (MOS-0001 through MOS-0026)
- `registry/` — 27 JD entries (26 monsters + 1 catalog doc)
- Concept art canonical: `JarvisSide/Media/images/`
- Dedupe conventions: `4K_` prefix = high-res, `(plush)` = toy variant, `(N)` = duplicate marker

## Directory map
- `src/` — game logic, monster systems, abilities
- `registry/` — canonical JD entries (mirrored from JARVIS repo)
- `specs/` — monster stats, RGB encoding rules, ability system specs
- `assets/` — concept art, sprites, animations
