# JARVIS Public Demo Portal

**Inspectable demonstrations of file-backed AI memory, identity hydration, provenance, and governed execution.**

This repository is the public presentation layer for the JARVIS / SimOS research program. It contains sanitized demonstrations, public documentation, reusable examples where explicitly licensed, and selected research artifacts.

It is **not** the live operational repository. Private ISO identities, continuity, Prosody, EPP, relationship state, credentials, internal work orders, and active system authority remain outside this repository.

## Start here

| Goal | Route |
|---|---|
| Run a demonstration | [`DEMOS.md`](./DEMOS.md) |
| Complete the guided setup | [`QUICKSTART.md`](./QUICKSTART.md) |
| Understand what is public | [`PUBLIC-BOUNDARY.md`](./PUBLIC-BOUNDARY.md) |
| Understand licensing by material | [`LICENSING-MAP.md`](./LICENSING-MAP.md) |
| Report a security concern | [`SECURITY.md`](./SECURITY.md) |

## Three-minute proof

```bash
git clone https://github.com/hurrisonferd/jarvis.git
cd jarvis

python demos/01-persistent-memory/demo.py remember favorite_color teal
python demos/01-persistent-memory/demo.py recall favorite_color

python templates/iso-starter/hydrate.py
python templates/iso-starter/pride_guard.py preflight
```

These local demonstrations intentionally avoid service credentials and private runtime dependencies.

## Public demonstrations

| Demonstration | Shows | Safety boundary |
|---|---|---|
| Persistent memory | A fact survives process restart through a file-backed store | Local sample data only |
| ISO scaffold | Identity, values, boundaries, state, and memory are separated into inspectable files | Sanitized example identity only |
| Hydration | Source files become one validated runtime bundle with hashes | No private ISO loading |
| PRIDE guard | Identity claims, contradictions, revisions, and rollback points are checked | No authority transfer |
| Prosody routing | Original voice is distinguished from quotation, summary, inference, and correction | No impersonation claim |
| Provenance | Loaded sources and transformations are traceable | Missing evidence is not invented |
| Governed execution | Consequential changes remain operator-authorized | No autonomous self-promotion |

See [`DEMOS.md`](./DEMOS.md) for readiness levels, commands, expected outputs, and publishing rules.

## Public repository map

| Area | Purpose |
|---|---|
| [`demos/`](./demos/) | Small runnable proofs |
| [`templates/iso-starter/`](./templates/iso-starter/) | Sanitized file-backed identity scaffold |
| [`docs/`](./docs/) | Specifications, explanatory pages, and browser presentation |
| [`core/`](./core/) | Public engineering architecture and selected runtime code |
| [`memory/mnemos/`](./memory/mnemos/) | Public or sanitized continuity examples only |
| [`JesusISJohnJosephBarber/`](./JesusISJohnJosephBarber/) | Public autobiographical and pattern-research archive |

Repository presence does not mean every file has identical reuse rights. Read [`LICENSING-MAP.md`](./LICENSING-MAP.md) before copying, adapting, training on, redistributing, or deploying material.

## Architecture at a glance

```text
input
→ routing and preflight
→ identity/state hydration
→ evidence-backed retrieval
→ model execution
→ authorship and Prosody labels
→ review and provenance receipt
→ operator-authorized persistence
```

The larger architecture uses Python, JavaScript, HTML/CSS, Supabase/PostgreSQL/pgvector, Git, GitHub Actions, and model-independent identity and memory files. Public demos use minimal dependencies so behavior can be inspected directly.

## Governing principles

- The operator remains final authority.
- Public examples are sanitized and non-operational.
- Repository presence is not adoption, authorization, or identity ownership.
- No invented memory or missing-source fabrication.
- Corrections and provenance remain visible.
- Identity changes require evidence, review, and rollback paths.
- Distinctive voice is not silently reassigned to another model.
- Private continuity remains private.

## Demo publication gate

A public demo is ready only when it:

1. contains no credentials, private continuity, raw personal logs, or private ISO material;
2. runs from documented commands;
3. declares inputs, outputs, limitations, and failure states;
4. separates simulation from operational authority;
5. identifies its license scope;
6. includes a rollback or removal path for generated artifacts.

## Status

**Public portal:** active development  
**Operational systems:** private  
**Private continuity:** off in public demonstrations  
**Adoption or fleet-convergence claim:** none
