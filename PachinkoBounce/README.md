# PachinkoBounce

**JNL:** PROJ-PACH-BIO-0001
**Status:** ACTIVE
**JARVIS repo:** `JarvisSide/Projects/PachinkoBounce/` (canonical spec, governed)
**This repo:** Godot 4.x development workspace, game assets, monster designs
**Engine:** Godot 4.x

## What
Physics-based Pachinko pinball RPG where monster companions bounce through procedurally
generated boards. RGB encoding: R=Power (force/punch), G=Rhythm (timing/combo), B=Range (spread/area).
Ethics-first monetization: no loot boxes, no energy systems, no pay-to-win.

## Current state
- GDD v0.4 in `specs/`
- Monster designs via MonsterOS (26 species catalogued)
- Canon assets: `JarvisSide/Media/images/` + `JarvisSide/Media/audio/`
- Godot 4.x project setup pending

## Directory map
- `src/` — Godot project (*.gd, scenes, resources)
- `specs/` — GDD, design docs, RGB encoding spec
- `assets/` — canonical images/audio linked from JARVIS repo
- `specs/systems/` — board generation, scoring, monster ability rules
- `specs/gameplay/` — turn structure, combat, progression
