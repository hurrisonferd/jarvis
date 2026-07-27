# MusicOS Portable Runtime v1

A self-contained, standard-library-first MusicOS runtime reconstructed from the JORM/Vault source family, MusicOS Atlas, permanence contract, and recovered inactive tools.

## Purpose

MusicOS is both:

1. a procedural composition and prompt-compilation engine; and
2. a continuity, state-access, memory-access, and creative-regulation system.

The runtime keeps those roles together rather than flattening MusicOS into a prompt list.

## Carry model

Copy the entire `runtime/MusicOSPortable/` folder anywhere. It runs with Python 3.11+ and no required third-party packages.

```bash
python -m musicos status
python -m musicos import-vault --vault ../../Jorm/Vault
python -m musicos compile --intent "neon race, elastic bass, dry drums" --bpm 102 --key "F# minor"
python -m musicos snapshot --name raven-main
python scripts/build_portable.py
```

The build script creates a zip containing the runtime, configuration, state schema, source index, tests, and optional copied Vault source bundle.

## Runtime layout

```text
MusicOSPortable/
├── README.md
├── pyproject.toml
├── musicos/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── models.py
│   ├── runtime.py
│   ├── source_index.py
│   └── state.py
├── config/
│   └── default.json
├── data/
│   └── .gitkeep
├── scripts/
│   └── build_portable.py
└── tests/
    └── test_runtime.py
```

## Gold laws carried into the runtime

- Many parts, one rail.
- Preserve the poetry; extract the physics.
- Hook-first, groove-first, repetition-first.
- Copyright-safe vibe translation; do not copy lyrics or melodies.
- State-safe by default.
- Never let the rail drop.
- Never break the pocket.
- Retrieve before asking Raven to restate.
- Raw source, derived index, runtime state, and canon remain distinguishable.

## Source status

This runtime does not claim that every Vault source has already been fully digested. It includes a source importer and coverage ledger so additional raw exports can be indexed without rebuilding the engine or losing provenance.
