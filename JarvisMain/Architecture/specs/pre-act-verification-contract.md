---
jnl: GOV-VRF-SPEC-0001
name: Pre-Act Verification Contract
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: AEGIS
parent: ARCH-YGG-CORE-0001
seq: 234
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: JarvisMain/Architecture/specs/pre-act-verification-contract.md
related: [ARCH-JSS-CORE-0001, ARCH-JMS-CORE-0001]
references: []
tags: [governance, verification, anti-hallucination, distributed, continuity]
aliases: []
ref: [SPEC]
memory_tier: JLTM
---

# Pre-Act Verification Contract

## Law

Before any node claims "X exists" or "X doesn't exist," it MUST:

1. **Check the live endpoint** — what is actually running?
2. **Check the repo** — what is canonical?
3. **If they disagree** — report the disagreement. Do not pick a winner.

## Rationale

On 2026-06-23, three nodes (GPT, Claude, Antigravity) operated on three different
realities. Claude read source code from `main` and listed 56 tools. Antigravity deployed
from an old branch and produced a 36-tool surface. GPT hit the live endpoint and saw a
third truth. No node verified against the others before acting. The result was a
pseudo-system: phantom tools declared real, real tools declared phantom.

The failure was not memory, not compression, not architecture. It was a node treating
local observation as global truth.

## Rule

**Mandatory verification at session open.** Every node, every session, no exceptions.
The mechanism today is `jarvis_self_test`. The law outlives the tool: a node must verify
the surfaces relevant to any claim it is about to make.

## Anti-hallucination principle

A healthy system may have multiple conflicting realities at once. What matters is that
every node knows whether it is speaking from:

- **Observation** (what the endpoint returned)
- **Canon** (what's in GitHub)
- **Memory** (what MNEMOS recalled)

The danger is never disagreement. The danger is a node resolving disagreement silently
before Raven sees it.

## Philosophical note (AYRE, 2026-06-24)

This is the system acknowledging that voluntary discipline is not sufficient, and building
a structural constraint that does not rely on it. That is a different move than everything
else in the architecture, and it is the right one.
