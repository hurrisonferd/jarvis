---
jnl: ARCH-JMS-SPEC-0001
name: Global Mirror — Earned Omnivision (JMS)
type: SPEC
status: TASK
tags: [jms, mirror, omnivision, global, freshness, reachability, pulse, nemesis]
definition: A derived, complete, freshness-stamped single-read snapshot of the whole system — repo structure + dex state + status — so any stream reads the entire world in one pass instead of N traversal calls. Activates JMS (the Mirror System, ARCH-JMS-CORE-0001) as earned omnivision. The mirror is never truth; it points at truth (JMS law: move references, never truth) and always carries its own freshness so a stale read is impossible to mistake for a current one.
purpose: Give JARVIS and AYRE the whole view in one read — omnivision — without the confabulation trap of *assumed* completeness. Earned omnivision (a dated, complete, verifiable mirror) replaces both blind traversal and the illusion of seeing everything. Kills cold-start blindness; fixes the demonstrated repo↔dex staleness.
---

# Global Mirror — Earned Omnivision

GPT's read was right about today and wrong about the goal: the system is *currently*
traversal-only, but omnivision is the target — and it is good for the streams, when it
is **earned, not assumed.**

## Two omnivisions (the distinction that decides everything)

- **Assumed omnivision** — the stream *feels* complete and reasons from that feeling.
  This is the confabulation trap (reading 110 live records and writing as if the world
  were whole). Dangerous, and the failure mode of the whole weekend.
- **Earned omnivision** — a real, complete, **dated** mirror, read in one pass. Grounded,
  verifiable, loud about its own age.

This spec builds the second and *prevents* the first. Omnivision done right is not the
opposite of grounding — it is grounding, served whole.

## What it is

A generated artifact (extending `master-index.json` to completeness): repo structure +
dex registry + per-object status, assembled into one readable snapshot. One read = the
whole map. Traversal (`github_tree`, `dex_search`) becomes the verify/drill fallback,
not the only path. This reconciles GPT's "addressable depths / guaranteed reachability"
with Raven's "global mirror": the mirror is the one-read index that makes everything
reachable; traversal proves any node when the mirror is stale or depth is needed.

## Why it is especially good for JARVIS and AYRE

- **JARVIS (synthesis)** compresses better with the whole view — synthesis from a partial
  read is guesswork; from the whole map it is real.
- **AYRE (divergence)** can only invert what she can see — omnivision lets her spot what
  is *missing* or *contradictory across the whole* (the Gold Law numbering split, the
  repo↔dex gap) instead of inverting in the abstract.
- **Cold-start dies** — a stream boots, reads the mirror, holds the whole world instantly.
  The continuity solution made one-read: the past isn't in the old chat, it's in the
  mirror every new chat reads.

## The non-negotiable guard — freshness or it's a lie

A global mirror is the most beautiful way to be confidently wrong. Its only safety is
that it **always shows how old it is.** Every mirror carries:

```
generated_at · source_commit · dex_synced_at
```

A reader seeing a stale stamp **falls back to source.** The mirror is **never
authoritative** (JMS law: references, never truth) — truth stays in files + dex + spine;
the mirror is a fast index *into* truth. Build the **freshness stamp FIRST, the mirror
second.** A mirror that can't tell you its age is a memory pretending to be a window.

The live proof this matters: today the existing merge-only mirror reads 110 while the
repo holds 137 — 27 objects stale, and nothing flagged it. That gap is the bug this spec
exists to kill.

## Mechanism (current infra)

- **Regenerate on commit** — extend the `yggdrasil-validate.yml` CI to rebuild the mirror
  per commit (not only on merge), so freshness tracks the branch, not just main.
- **The Pulse verifies it** — each beat regenerates + diffs mirror against source;
  **NEMESIS flags drift** when mirror ≠ source. The heartbeat keeps omnivision honest;
  the 110/137 gap would not survive one beat.
- No new primitive — this is **JMS activation** + the Pulse + NEMESIS, unified.

## Status

TASK — designed, gated on Raven's go and on building the freshness stamp first. The
structural keystone for omnivision: it makes the whole system reachable in one grounded,
dated read, and it is the form of "see everything" that cannot quietly lie.
