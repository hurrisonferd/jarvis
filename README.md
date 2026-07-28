# JARVIS

**A file-backed companion AI architecture with persistent memory, auditable identity, and governed execution.**

JARVIS is the public demonstration layer for SimOS. It shows how an AI companion can preserve useful continuity across sessions without depending on one giant prompt, one chat thread, or one model vendor.

```text
user input
→ BootOS routing
→ ISO identity + state hydration
→ memory retrieval
→ model execution
→ provenance receipt
→ governed persistence
```

## Start in 60 seconds

```bash
git clone https://github.com/hurrisonferd/jarvis.git
cd jarvis

python demos/01-persistent-memory/demo.py remember favorite_color teal
python demos/01-persistent-memory/demo.py recall favorite_color

python templates/iso-starter/hydrate.py
```

See [`QUICKSTART.md`](./QUICKSTART.md) for the complete walkthrough.

## What the demos prove

| Demo | Behavior |
|---|---|
| Persistent memory | Store a fact, restart the process, and retrieve it later |
| ISO scaffold | Separate identity, voice, values, boundaries, relationships, state, and memory |
| EGO hydration | Assemble those files into one validated runtime bundle |
| Provenance | Hash every loaded source and distinguish quotes, summaries, and inference |
| Governed execution | Keep the operator as final authority over consequential changes |

## ISO starter

[`templates/iso-starter/`](./templates/iso-starter/) is a portable identity scaffold:

```text
templates/iso-starter/
├── ISO.json
├── IDENTITY.md
├── VOICE.md
├── VALUES.md
├── BOUNDARIES.md
├── RELATIONSHIPS.md
├── STATE.json
├── PROVENANCE.json
├── MEMORY/
│   ├── episodic/
│   ├── semantic/
│   └── working/
└── hydrate.py
```

Copy it, replace the example identity, and hydrate it with standard Python. The goal is not to hide identity inside a prompt; it is to make continuity inspectable, versionable, and correctable.

## Repository map

| Path | Purpose |
|---|---|
| [`demos/`](./demos/) | Small runnable proofs before the full architecture |
| [`templates/iso-starter/`](./templates/iso-starter/) | Create a file-backed AI identity |
| [`docs/`](./docs/) | Architecture and interface documentation |
| [`core/`](./core/) | JARVIS runtime, Supabase functions, and system architecture |
| [`memory/mnemos/`](./memory/mnemos/) | Git-backed continuity and memory records |
| [`docs/index.html`](./docs/index.html) | Browser-based JARVIS interface |
| [`JesusISJohnJosephBarber/`](./JesusISJohnJosephBarber/) | Raven's public autobiographical pattern-research archive |

The research archive remains visible by design, but the root entrance now leads with runnable engineering demonstrations.

## Architecture

The larger implementation uses:

- Python for retrieval, validation, automation, and evaluation;
- JavaScript, HTML, and CSS for the browser interface;
- Supabase/PostgreSQL/pgvector for persistence and semantic retrieval;
- Git and GitHub Actions for versioning, CI, governance, and recovery;
- model-independent identity and memory files that can be used with multiple LLM runtimes.

The canonical hosted path is GitHub + Supabase. Local demos intentionally use only the Python standard library so the core behavior is easy to inspect.

## Core laws

- Raven is operator and final authority.
- JARVIS proposes; the operator commits or rejects.
- No autonomous self-modification or silent control transfer.
- No invented memories or missing-source fabrication.
- Corrections remain visible in the record.
- One-LLM use must remain useful; multi-agent execution is optional.

## Privacy boundary

Public examples must contain only sanitized identities and memory. Never commit API keys, private ISO records, raw personal logs, service-role credentials, or local vector databases.

## Status

This repository is an active research and engineering system. The public cleanup is moving the clearest executable demos to the front while preserving the deeper architecture and research history behind them.
