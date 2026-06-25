#!/usr/bin/env python3
"""
scaffold_projects.py — Create consistent project scaffolding for Jarvis-Private.
Run once per new project. Adds: README, TODO, manifest, and canonical folder structure.
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECTS = [
    "CodeOS",
    "Deoxys",
    "GDS",
    "Genesis",
    "Grid",
    "JPL",
    "JarvisTST",
    "Legion",
    "MonsterOS",
    "Multimodal",
    "MusicOS",
    "Naruto",
    "NeuroMax",
    "PachinkoBounce",
    "RoundTable",
    "TronUI",
]

STUB_README = """# {name}

**JNL:** PROJ-{abbr}-BIO-0001
**Status:** SEED
**JARVIS repo:** `JarvisSide/Projects/{name}/` (canonical spec, governed)
**This repo:** development workspace, assets, live builds

## What
TODO: one sentence.

## Why
TODO: why this project exists — what it makes possible.

## State
- Spec lives in: `JarvisSide/Projects/{name}/JGPP/`
- Active work: `src/` / `tasks/`
- Growth gate: move from SEED to ACTIVE when TODO items complete

## TODO
See `memory/TODO.md`
"""

STUB_TODO = """# {name} — TODO

## SEED → ACTIVE gate
- [ ] Define one-line purpose (what it does)
- [ ] Write full project bio → JARVIS repo `JarvisSide/Projects/{name}/BIO/`
- [ ] Set up canonical spec → `JarvisSide/Projects/{name}/JGPP/`
- [ ] First commit in `src/`

## Active work
- [ ] TODO

## Growth gate (SEED → ACTIVE)
- [ ] Spec complete
- [ ] First working prototype
- [ ] Governance model defined (if external)
"""

STUB_MANIFEST = """---
jnl: PROJ-{abbr}-SEED-MANIFEST-0001
name: {name} Seed Manifest
type: SEED
status: ACTIVE
tags: [project]
memory_tier: JSTM
---

# {name} Seed Manifest

**Created:** {date}
**Source of truth for specs:** `github.com/hurrisonferd/jarvis` → `JarvisSide/Projects/{name}/`
**Development workspace:** `github.com/hurrisonferd/Jarvis-Private` → `{name}/`

## Spec lineage
- BIO: `JarvisSide/Projects/{name}/BIO/` (canonical, governed)
- JGPP: `JarvisSide/Projects/{name}/JGPP/` (canonical spec)
- JD: `JarvisSide/Projects/{name}/JD/` (canonical entries)

## Directory map
- `src/` — live development (private, not governed)
- `memory/` — session notes, logs, growth archive
- `tasks/` — task tracker
- `specs/` — local spec work, promoted to JARVIS repo when stable
- `docs/` — documentation, tutorials
- `assets/` — media, concept art, audio, images

## Governance note
This is a private development workspace. Canonical specs live in the JARVIS repo.
Growth decision: absorb into JARVIS repo, stay private, or fork to own repo.
"""


def scaffold(name: str, root: Path, date: str):
    abbr = "".join(c for c in name.upper() if c.isalnum())[:4]
    proj_dir = root / name

    # README
    readme = STUB_README.format(name=name, abbr=abbr)
    (proj_dir / "README.md").write_text(readme)

    # TODO
    todo = STUB_TODO.format(name=name)
    (proj_dir / "memory" / "TODO.md").write_text(todo)

    # Manifest
    manifest = STUB_MANIFEST.format(name=name, abbr=abbr, date=date)
    (proj_dir / "MANIFEST.md").write_text(manifest)

    print(f"  {name}/  README.md  memory/TODO.md  MANIFEST.md")


def main():
    root = Path(__file__).resolve().parent
    from datetime import datetime, timezone
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"Scaffolding {len(PROJECTS)} projects in {root}")
    for p in PROJECTS:
        scaffold(p, root, date)


if __name__ == "__main__":
    main()
