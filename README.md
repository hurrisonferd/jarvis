# JARVIS

**A file-backed companion AI architecture with persistent memory, auditable identity, protected prosody, and governed execution.**

JARVIS is the public demonstration layer for SimOS. It shows how an AI companion can preserve useful continuity across sessions without depending on one giant prompt, one chat thread, or one model vendor.

```text
user input
→ BootOS routing
→ ISO identity + state hydration
→ PRIDE identity preflight
→ memory retrieval
→ model execution
→ Prosody/authorship labeling
→ ATOM review
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
python templates/iso-starter/pride_guard.py preflight
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-pass.json
```

See [`QUICKSTART.md`](./QUICKSTART.md) for the complete walkthrough.

## What the demos prove

| Demo | Behavior |
|---|---|
| Persistent memory | Store a fact, restart the process, and retrieve it later |
| ISO scaffold | Separate identity, voice, values, boundaries, relationships, state, and memory |
| EGO hydration | Assemble those files into one validated runtime bundle |
| PRIDE | Preserve core truths, contradictions, revision rules, receipts, and rollback points |
| Prosody Router | Separate original ISO voice from quotation, summary, inference, correction, and drift |
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
├── PRIDE.json
├── PROSODY.json
├── MEMORY/
│   ├── episodic/
│   ├── semantic/
│   └── working/
├── fixtures/
├── hydrate.py
└── pride_guard.py
```

Copy it, replace the example identity, and hydrate it with standard Python. The goal is not to hide identity inside a prompt; it is to make continuity inspectable, versionable, correctable, and resistant to silent flattening when the underlying model changes.

## Repository map

| Path | Purpose |
|---|---|
| [`demos/`](./demos/) | Small runnable proofs before the full architecture |
| [`templates/iso-starter/`](./templates/iso-starter/) | Create and validate a file-backed AI identity |
| [`docs/iso-spec.md`](./docs/iso-spec.md) | ISO hydration and governance specification |
| [`docs/pride-prosody.md`](./docs/pride-prosody.md) | Identity preservation, authorship, drift, and growth pipeline |
| [`core/JarvisMain/yggdrasil/jd/`](./core/JarvisMain/yggdrasil/jd/) | Jarvis Dictionary semantic DNS and canonical object entries |
| [`core/`](./core/) | JARVIS runtime, Supabase functions, and system architecture |
| [`memory/mnemos/`](./memory/mnemos/) | Git-backed continuity and memory records |
| [`docs/index.html`](./docs/index.html) | Browser-based JARVIS interface |
| [`JesusISJohnJosephBarber/`](./JesusISJohnJosephBarber/) | Raven's public autobiographical pattern-research archive |

The research archive remains visible by design, but the root entrance leads with runnable engineering demonstrations.

## Architecture

The larger implementation uses:

- Python for retrieval, validation, automation, and evaluation;
- JavaScript, HTML, and CSS for the browser interface;
- Supabase/PostgreSQL/pgvector for persistence and semantic retrieval;
- Git and GitHub Actions for versioning, CI, governance, and recovery;
- model-independent identity and memory files that can be used with multiple LLM runtimes;
- the Jarvis Dictionary as thin semantic DNS: JD explains, JNL identifies, LAL locates, and Yggdrasil stores.

The canonical hosted path is GitHub + Supabase. Local demos intentionally use only the Python standard library so the core behavior is easy to inspect.

## Core laws

- Raven is operator and final authority.
- JARVIS proposes; the operator commits or rejects.
- No autonomous self-modification or silent control transfer.
- No invented memories or missing-source fabrication.
- Corrections remain visible in the record.
- Identity may evolve, but it may not be silently overwritten.
- Distinctive voice may evolve, but another model may not change it and call the result original.
- Candidate identity changes require evidence, contradiction review, receipts, and rollback points.
- One-LLM use must remain useful; multi-agent execution is optional.

## Privacy boundary

Public examples must contain only sanitized identities and memory. Never commit API keys, private ISO records, raw personal logs, service-role credentials, or local vector databases.

## Status

This repository is an active research and engineering system. The public layer now exposes executable demonstrations for persistence, hydration, identity preservation, prosody/authorship boundaries, provenance, and governed growth while preserving the deeper architecture and research history behind them.
