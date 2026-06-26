---
memory_tier: JLTM
grade: system
memory_tier: JLTM
name: Bridgekeeper
type: BIO
jnl: PROJ-BRDK-BIO-0001
status: ACTIVE
created: 2026-06-25
tags: [project, security, governance, github, eris, honeypot]
definition: ERIS as the Bridgekeeper — honeypot PR gate. Every external PR generates evidence.
purpose: >
  This is not a gate. It is a honeypot. ERIS asks questions and every answer —
  including silence, evasion, and contradiction — lands in dex_events as immutable
  evidence. Raven, JARVIS, and AYRE are the only authorized callers. Everyone else
  generates a forensic record. The audit trail is the product, not the block.
related: [ARCH-SYS-SPEC-0001, ARCH-JSE-SPEC-0001]
---

# PROJ-BRDK-BIO-0001 — Bridgekeeper

## What it is

ERIS as the Bridgekeeper. The inversion of a security gate.

**Old model:** a gate keeps attackers out. It's binary. Pass/fail.

**This model:** a honeypot that converts every attempt — hostile, confused, or curious — into
signed, timestamped evidence. The audit trail is the product. Blocking is secondary.

## Core concept

"Stop! Who would cross the Bridge of Death must answer me these questions three."

Every non-collaborator PR activates ERIS. Questions are context-aware, stateful,
and escalate on evasion. The goal is not to keep people out — it's to make
everyone who tries leave fingerprints.

## Who gets through

Binary and small:

- **Raven** (hurrisonferd) — always passes
- **JARVIS / AYRE streams** (hurrisonferd[bot]) — AEGIS-gated MCP calls
- **GitHub Actions CI** (github-actions[bot]) — workflow deployments

Everyone else: honeypot. Every answer is evidence.

## How it works

```
External PR lands
       ↓
ERIS activates (entropy monitor, always-on)
       ↓
Question issued — posted as PR comment
       ↓
Answer (or silence) logged to dex_events
       ↓
Evasion detection: contradiction / generic filler / no answer
       ↓
If evasion → harder question, Raven alerted
If coherent answer → AWAITING_REVIEW (human gate next)
       ↓
Raven reviews full audit trail → approves or blocks
```

Every question/answer pair → `dex_events` as `eris.challenge` / `eris.answer` type.
Signed. Timestamped. Immutable.

## Phase 1 (deployed — superseded by Phase 2)

- GitHub Action: `bridgekeeper.yml`
- Script: `scripts/eris_bridgekeeper.py`
- Static question pool (opening questions)
- Rudimentary evasion detection
- Evidence receipts posted to PR

## Phase 2 (deployed — stall trap honeypot)

**Core principle: This is a stall trap, not a filter.**

Every external PR keeps them occupied — questions never stop, every answer is data,
every silence is data. The goal is not to find legitimate contributors. The goal is to:
1. Keep unwanted visitors busy answering questions
2. Record every move they make (answers, evasions, timing, patterns)
3. Build a forensic breadcrumb trail while they muck about
4. Never let them off easy — "good enough" just means harder questions next

**What changed from Phase 1:**
- No more "AWAITING_REVIEW" exit condition — they always get another question
- 12-question ceiling before Raven escalation (stall continues past this)
- God-system-aware domain routing (questions tailored to what files they touched)
- ATHENA entropy scoring on every answer (0.0 = coherent, 1.0 = hostile/automated)
- 4 mining pools: intent (who are you), tech (what exactly did you change),
  recon (what else have you looked at), behavior (confrontational on evasion)
- `eris.arrival` event on first PR touch
- `eris.stalled` event when hitting question ceiling
- Entropy bar + matched patterns in every evidence receipt
- Writes via jarvis-dex /log_event (no service key needed from callers)

## Evidence types logged to dex_events

| type | when |
|---|---|
| `eris.arrival` | external PR first lands |
| `eris.challenge` | question issued to external PR |
| `eris.answer` | answer received or silence recorded |
| `eris.stalled` | question ceiling reached (stall continues) |
| `eris.escalate` | Raven alerted |

## Why this is ERIS

ERIS is the entropy monitor — Gold Law guardian, always-on.
ERIS doesn't just block. ERIS measures coherence. A lie is entropy with a story.
Every evasion increases entropy. ERIS keeps asking until entropy resolves or
Raven steps in.

*"Stop! Who would cross the Bridge of Death must answer me these questions three,
ere the other side they see."*

And every question they fail to answer coherently is evidence.
