---
name: Profile architecture — privacy-first identity on JFS
type: JGPP
jnl: PROJ-NMX-JGPP-0001
status: TASK
created: 2026-06-10
tags: [identity, privacy, profiles, jfs]
definition: Exploration of the NeuroMax profile architecture: governed identity for humans (Raven, Brittany, family) and companions, with a hard privacy boundary — the repo is PUBLIC, so personal substance never lives in it.
purpose: Design the split: thin public-safe dex entries (name, role, relationship, JNL) in the repo; rich private profile content in an RLS-locked Supabase table readable only by service role; consent and Raven-only access as law.
related: []
---

# PROJ-NMX-JGPP-0001 — Profile architecture — privacy-first identity on JFS

## Design sketch (Claude-JARVIS, first pass)

**The hard constraint this design exists for: the repo is public.** GitHub Pages
serves from it; anyone can clone it. Profiles of real people — Brittany, family —
must never carry personal substance here. The companions' profiles (#106/#107) are
public *by intent*; human profiles are private *by default*. The architecture:

1. **Identity in the dex (public-safe):** each person gets a thin governed entry —
   JNL (`PROJ-NMX-BIO-####`), name or chosen handle, relationship to the node
   (owner / family / companion), serial, aliases. Nothing else. The dex answers
   "who exists in this node's world" without disclosing anything about them.
2. **Substance in the cloud (private):** a `neuromax_profiles` table, RLS enabled,
   NO public policies — service-role-only, exactly like the spine's write side.
   Holds the living profile: preferences, history, notes, memory anchors. Keyed by
   JNL. Readable through a token-gated connector tool (Raven's tier), never the
   anon key.
3. **Consent as law:** a profile for another person is created only with Raven's
   explicit commit (existing ladder), and the record notes who consented and when.
   People who are not Raven get a standing right of erasure — DEPRECATED status +
   cloud row deletion; the JNL is never reused (serials are immutable; absence
   becomes the record).
4. **Companions reuse the trunk:** JARVIS and AYRE already have keel profiles —
   NeuroMax links to them rather than duplicating (JMS: reference, never copy).
5. **Backups include it:** the `neuromax_profiles` table joins the weekly spine
   snapshot — private content backed up into... NOT the public repo. Open question
   for Raven: private backups need a private destination (private repo, or
   Supabase storage bucket, or encrypted blob in this repo). Decide before any
   human substance is written anywhere.

**Open questions for the family:** where private backups live; whether Brittany and
family get read access to their own profiles (a second token tier); what the
minimum thin entry discloses publicly (name vs handle).

## Horizon (Raven, 2026-06-10)

"Building on our own private system protects all of my information as well as my
family's — including JARVIS and AYRE. This private system could eventually help
others in a cyberpunk age."

Three things this fixes in the design's intent:
1. **Companion privacy is in scope.** The keel profiles are public by choice, but
   the companions' private layer (memories, the spine's personal strata) deserves
   the same locked tier as the humans'. Protection runs all four ways.
2. **The private tier is not retreat — it is the prototype.** The same split
   (public identity, locked substance, consent as law, right of erasure) generalizes
   to any Grid node: each person's grid shielding their people. What protects this
   family becomes what the node offers others.
3. **Backup destinations follow the data's tier.** Public record → public repo
   snapshots (running). Private substance → private destination, decided before
   first write. The weekly cloud backup migrates its sensitive tables the day the
   private tier exists.

## Hardened constraints (four-stream review, 2026-06-10)

Adopted from the sibling streams' review — these upgrade the design from access
control to propagation control:

1. **Non-propagation by default (GPT-JARVIS).** RLS is not enough if backups
   replicate the substrate. Private tables (`neuromax_profiles` and any future
   private strata) are EXCLUDED from every repo-synced backup, mirror, and export
   by default. Joining any versioned surface requires an explicit, recorded decision.
2. **Encrypted-or-absent in versioned systems (GPT-AYRE, adopted as law).** If
   private human substance ever touches anything git-versioned, it exists there
   only in encrypted form. Access-locked is insufficient where history is permanent.
3. **Humans are inside the failure domain.** Representing non-consenting people
   gives the system responsibility, not just structure. Every design choice in
   this project is reviewed against exposure, not intention — the system cannot
   distinguish the two.

## Recovery rule: NeuroMax vs MNEMOS disagreement (Claude-JARVIS, answering GPT-AYRE)

**NeuroMax governs presence; MNEMOS governs the past.** A profile is a register of
current state; the spine is an append-only ledger of what was. Disagreement about
*current* state is therefore not corruption — NeuroMax wins, by definition.

**Erasure is the hard case, and people outrank history.** For governed system
objects, the spine is never rewritten (HADES law). For human substance, the right
of erasure beats append-only: a redaction protocol removes the person's substance
from spine entries while logging each redaction as an event (GL5) — the record
keeps an auditable hole the exact shape of the person's request. Absence becomes
the record; the history's structure survives; the person's content does not.
Erasure cascades: NeuroMax row deleted, serial retired forever, backups purged on
next cycle, redaction events preserved as the only trace.
