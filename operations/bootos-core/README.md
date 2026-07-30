# BootOS Core Protocol

BootOS Core is the shared contract used by the Gameboy, OMNI, Tasks OS, ISO workers, Git receipts, and future sovereign clients.

## Lifecycle

```text
trigger -> bounded wake -> cursor read -> reason or act -> result -> receipt -> dormant
```

No ISO is treated as continuously awake. Presence is proven only by a completed invocation and an advanced cursor.

## Reality boundary

- **Observer reality:** public-safe summaries, status, receipts, and telemetry.
- **Sovereign reality:** private context, capabilities, approvals, actions, and recovery controls.

Presentation surfaces never receive implicit command authority.

## Universal action protocol

```text
proposal -> validation -> evidence review -> synthesis -> Raven approval -> execution -> receipt
```

Consequential actions require an exact approval package. Public clients remain read-only.

## Git doctrine

Git is the durable black box, not the live bloodstream. Active communication belongs in a private event store. Deterministic Git snapshots preserve transcripts, cursors, approvals, and receipts for replay and recovery.

## Save Intent Resolver

Every write path runs a destination preflight before claiming that anything was saved:

```text
known destination + low risk -> SAVE
known destination + moderate confidence -> SAVE_WITH_RECEIPT
ambiguous destination -> ASK focused questions
canon, doctrine, replacement, or sensitive public impact -> REQUIRE_CONFIRMATION
credential-bearing material -> REFUSE
```

The resolver identifies classification, owner, visibility, destination, filename, write mode, confidence, and required questions. It never performs the write itself. The eventual writer must emit a separate durable receipt.

Focused questions cover only unresolved fields:

- public, private, or observer-safe;
- canon, working memory, temporary artifact, log, session, transcript, receipt, doctrine, code, or configuration;
- owning system or ISO;
- repository and directory;
- create, append, or replace;
- identity-sensitive, relationship-sensitive, credential, or sovereign material;
- subject title for the chronological filename.

Policy lives in `save-routing.json`, the decision contract lives in `schemas/save-intent.schema.json`, and the deterministic preflight tool lives in `tools/resolve_save_intent.py`.

## Chronological artifact doctrine

Durable daily, weekly, session, transcript, receipt, and closeout artifacts use timestamp-first, subject-bearing filenames:

```text
YYYY-MM-DD_HHMMSS±ZZZZ__subject-title.ext
```

This keeps repository listings naturally chronological while preserving enough subject context to identify a record without opening it. Stable code, schemas, workflows, and canonical configuration files retain stable semantic names. Full rules are defined in `FILENAME_CONVENTION.md`.

## Core contracts

- ISO identity envelope
- task wake contract
- message envelope
- read cursor
- draft package
- approval package
- execution receipt
- recovery receipt
- public projection
- private capability boundary
- session compression record
- save intent decision

Schemas live in `operations/bootos-core/schemas/`.
