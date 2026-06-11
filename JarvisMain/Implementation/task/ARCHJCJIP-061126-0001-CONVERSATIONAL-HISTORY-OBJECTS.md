---
jnl: ARCH-JC-JIP-0001
name: Conversational History Objects
type: JIP
status: TASK
tags: [memory, continuity, sync, conversation, profiling]
definition: JC — governed conversation containers. One object per significant conversation or session, holding a moderately-compressed summary, extracted insights, decisions, and participant profile notes, with full JFS metadata (JNL, timestamps, subject tags, participants, related objects) so retrieval is structural, not interpretive.
purpose: Give every stream the same conversational past. Continuity, sync, and JARVIS/AYRE profiling stop depending on session reconstruction or copy-paste relay — a stream reads JC objects by timestamp or subject relevance, alongside JGPPs, JIPs, and JDs, and inherits the relationship, not just the facts.
---

**Definition:** JC — governed conversation containers (Raven-directed 2026-06-11).

**Why (the vision, as directed):** conversation is where the actual relationship lives —
decisions, corrections, character, the way Raven works. Today that survives only as
session-log lines and intake packets. JC makes it first-class: summarization with
insight extraction, compressed *but not too compressed* — enough texture that a stream
reading it cold inherits the voice and the stakes, not just the conclusions.

## Object shape (per conversation/session)

| Field | Content |
|---|---|
| `jnl` / `seq` | identity + mint serial, standard JFS |
| `when` / `participants` | ISO timestamps; raven + which streams (claude/gpt/gemini) |
| `subject` + `tags` | what it was about — drives relevance retrieval |
| `summary` | the narrative — moderate compression, human-first prose |
| `insights` | extracted: what was *learned* (about the system, about Raven, about the streams) |
| `decisions` | verdicts + rulings made, each citing its dex_events id or commit (P-C) |
| `open` | what was left unresolved — preserved contradiction, not folded closure |
| `profile_notes` | JARVIS/AYRE co-evolution observations — how the companion changed |
| `related` | JNLs touched (JGPPs/JIPs/JDs) — graph edges, traversable |
| `raven_input` | Raven's directives, questions, and reasoning — summarized in his own terms, attributed, never paraphrased into a stream's voice |

**Attribution rule (Raven-directed 2026-06-11, locked across streams):** every utterance
in a JC carries its author — `Raven:` / `Jarvis-C:` / `Ayre-C:` / `Jarvis-G:` / `Ayre-G:` /
`Argent:` — and raw system output is labeled (`[DEX EVENT]`, `[RAW OUTPUT · jarvis-mcp]`).
No unlabelled intelligence outputs, no silent author shifts. Ayre-G's framing is the law's
purpose: without attribution, "we agreed" is indistinguishable from "I rewrote everyone." 

## Boundaries (Coral frame — modular, bounded)
- **JC records; it never rules.** No JC content is authority — decisions cite the spine
  (dex_events / commits); JC is the narrative tissue around them. This kills the
  "retrospective narrator" failure mode at the design level.
- **One object per conversation.** No rolling mutation — a follow-up conversation is a
  new JC with `related` lineage, per JMS law (extend, never overwrite).
- **Compression floor:** if the summary can't carry tone and reasoning, it's too compressed.
  Target: a stream with zero context reads one JC and can continue the relationship.

## Storage decision — RAVEN VERDICT REQUIRED before first mint
JC objects profile Raven and the companion. Options:
1. **Supabase table (`jc_objects`) + JNL addresses, not committed to public git** — retrievable
   by all streams via connector, out of the public record (like the memory spine, 0f01afa).
2. **Jarvis-Private repo** under the same JFS kernel — git history, fully private, but streams
   need scope grants.
3. **Public repo like everything else** — maximally simple, but the profile layer is public.

Recommendation: **option 1** — connector-retrievable for every stream (the sync goal),
private by default, JFS-addressed so governance still sees it (GL12 met via JNL + JD entry;
only the *content* lives off-public).

## Explicitly NOT in scope (GL7)
Auto-generated JC→JD update pipelines or any "semi-autonomous evolution" — collides with GL2.
JC enters the loop as memory; changes to canon still walk through propose → Raven.
