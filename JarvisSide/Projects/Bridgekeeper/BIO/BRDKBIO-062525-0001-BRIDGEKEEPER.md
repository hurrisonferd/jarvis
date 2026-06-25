---
memory_tier: JLTM
name: Bridgekeeper
type: BIO
jnl: PROJ-BRDK-BIO-0001
status: ACTIVE
created: 2026-06-25
tags: [project, security, governance, github]
definition: GitHub PR challenge gate for external contributors — Bridgekeeper asks questions before PRs can merge.
purpose: >
  Firewall for JARVIS repo. Any PR from a non-collaborator must pass Bridgekeeper's
  gauntlet before it can merge. Questions are context-aware and non-trivial — the goal
  is to slow down drive-by noise and signal real intent.
related: [PROJ-ALL-LOG-0001, ARCH-SYS-SPEC-0001]
---

# PROJ-BRDK-BIO-0001 — Bridgekeeper

## What it is

A GitHub Action or App that intercepts PRs from outside collaborators and challenges them.
Inspired by the Bridgekeeper from Monty Python and the Holy Grail — three questions before
crossing.

## Core concept

"Stop! Who would cross the Bridge of Death must answer me these questions three,
ere the other side they see."

- Questions are non-trivial and context-aware (not just "what is your name")
- PR is blocked until answered satisfactorily or admin approves
- Creates friction for noise, signals intent for real contributors
- Scales with JARVIS's ability to generate interesting questions

## Questions (Phase 1)

1. "What is your name?" — identity
2. "What is your quest?" — intent
3. "What is the airspeed velocity of an unladen swallow?" — the curveball

## Implementation path

1. GitHub Action triggered on `pull_request` events from outside collaborators
2. Posts a comment with questions
3. Fails the PR status check
4. Admin (Raven) can approve → merges through
5. Phase 2: context-aware questions based on PR content
