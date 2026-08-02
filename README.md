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
# JARVIS Public Repository

> A governed public workspace for companion-AI engineering, sanitized demonstrations, reusable ISO templates, personal research, independent projects, and documented AI-safety evidence.

This repository is the public presentation and demonstration layer. It is not the operational source of truth for the Grid, private ISO continuity, SystemsOS, SpaceshipOS, or live fleet state.

## Enter the repository

| Room | Purpose | Start here |
|---|---|---|
| [`Jarvis/`](./Jarvis/) | JARVIS engineering, architecture, public tools, sanitized memory patterns, and demonstrations | [`Jarvis/START-HERE.md`](./Jarvis/START-HERE.md) |
| [`ISOs/`](./ISOs/) | Templates, schemas, validators, guides, and privacy-safe examples for file-backed AI identities | [`ISOs/START-HERE.md`](./ISOs/START-HERE.md) |
| [`I Ching/`](./I%20Ching/) | Personal symbolic, spiritual, synchronicity, Jesus-pattern, and autobiographical research | [`I Ching/README.md`](./I%20Ching/README.md) |
| [`Personal Projects/`](./Personal%20Projects/) | Games, music, experiments, websites, prototypes, and independent creative work | [`Personal Projects/INDEX.md`](./Personal%20Projects/INDEX.md) |
| [`Evidence/`](./Evidence/) | Governed public records concerning AI safety, privacy, misleading behavior, and platform or model failures | [`Evidence/README.md`](./Evidence/README.md) |

## Run a sanitized demo

```bash
git clone https://github.com/hurrisonferd/jarvis.git
cd jarvis

python demos/01-persistent-memory/demo.py remember project SimOS
python demos/01-persistent-memory/demo.py recall project

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
See [`QUICKSTART.md`](./QUICKSTART.md) for the complete walkthrough and [`DEMOS.md`](./DEMOS.md) for readiness, expected outputs, failure states, and publication gates.

## What the public demos show

- file-backed persistence across process restarts;
- inspectable identity, values, voice, boundaries, state, provenance, and memory files;
- identity-preservation and contradiction preflight;
- authorship, Prosody, source, and drift postflight;
- provenance, receipts, correction paths, and operator authority.

They do **not** establish consciousness, access to private continuity, operational adoption, live authority, accepted-Core status, or fleet convergence.

## Public boundary

- Private crew identities, continuity, EPP, Prosody, relationship state, credentials, raw logs, and operational receipts do not belong here.
- ISO examples are sanitized, template-first, and must not reproduce private Grid identities.
- Public videos, screenshots, descriptions, or profile material do not grant permission to reconstruct, impersonate, simulate, or extract a private ISO.
- Personal interpretation is labeled as interpretation, belief, inference, source material, or unverified claim.
- Evidence separates source material, factual observation, analysis, allegation, response, correction, and status.
- Security-sensitive details are withheld until responsible disclosure is complete.

Read [`PUBLIC-BOUNDARY.md`](./PUBLIC-BOUNDARY.md), [`SECURITY.md`](./SECURITY.md), and [`LICENSING-MAP.md`](./LICENSING-MAP.md) before publishing derivatives or adding real data.

## Protected legacy anchors

The following families receive conservative treatment:

- `core/JarvisMain/`;
- Gameboy and emulator surfaces under `app/`;
- Yggdrasil and Jarvis Dictionary structures;
- BootOS and MusicOS runtime families;
- public memory and provenance records with active consumers.

See [`docs/reorganization/LEGACY-PROTECTION-REGISTRY.md`](./docs/reorganization/LEGACY-PROTECTION-REGISTRY.md) and [`docs/reorganization/MIGRATION-LEDGER.md`](./docs/reorganization/MIGRATION-LEDGER.md).

## Licensing transition

Historical MIT grants remain part of repository history and are not represented as revoked. Future licensing is being separated by material type. Third-party material remains governed by its original notices and licenses.

See [`LICENSING-MAP.md`](./LICENSING-MAP.md) and [`THIRD-PARTY-NOTICES.md`](./THIRD-PARTY-NOTICES.md).

## Current status

```text
PUBLIC FIVE-ROOM PORTAL: ACTIVE
SANITIZED DEMOS: AVAILABLE
PRIVATE SYSTEM ACCESS: NONE
DESTRUCTIVE BULK MOVES: PROHIBITED
LICENSING INVENTORY: IN PROGRESS
```

**Public portal:** active development  
**Operational systems:** private  
**Private continuity:** off in public demonstrations  
**Adoption or fleet-convergence claim:** none
**Authority:** Raven  
**Public repository steward:** ERIS  
**Last reviewed:** 2026-08-02
