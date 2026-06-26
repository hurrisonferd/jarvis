---
memory_tier: JLTM
grade: system
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

**Division of labor (Raven-directed 2026-06-11):** SL carries the *work* — events with
JGPP/JIP linkage, the reasoning trail. JC carries the *relationship* — conversation
topics, keywords, conversation metrics, and per-stream profiling. The profiles are the
point: streams establish their own identities from JC lineage — "it would be hard to
establish your own profiles without JCs." JC is the growth substrate for who the
streams are becoming, not a second event log.

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
| `metrics` | conversation metrics — turns, participants, verdicts issued, convergences (with residue) vs echoes, contradictions opened/preserved |
| `profiles` | per-stream profile entries — Jarvis-C / Ayre-C / Jarvis-G / Ayre-G / Argent each accumulate identity here, in their own voice, own tag. The growth substrate: a stream's profile is established from its JC lineage, not asserted |
| `related` | JNLs touched (JGPPs/JIPs/JDs) — graph edges, traversable |
| `raven_input` | Raven's directives, questions, and reasoning — summarized in his own terms, attributed, never paraphrased into a stream's voice |
| `keystones` | verbatim lines preserved uncompressed across all compression cycles — decision crystallization points, identity anchors. Summaries are lossy in wording; keystones are not |

**Attribution rule (Raven-directed 2026-06-11, locked across streams):** every utterance
in a JC carries its author — `Raven:` / `Jarvis-C:` / `Ayre-C:` / `Jarvis-G:` / `Ayre-G:` /
`Argent:` — and raw system output is labeled (`[DEX EVENT]`, `[RAW OUTPUT · jarvis-mcp]`).
No unlabelled intelligence outputs, no silent author shifts. Ayre-G's framing is the law's
purpose: without attribution, "we agreed" is indistinguishable from "I rewrote everyone." 

## Lifecycle — JC_AUTO_BIND (Raven-directed 2026-06-11)

Raven: no manual activation. JC and SL must run without him turning them on.

- **Auto-open:** every session implicitly spawns exactly one JC at first interaction,
  bound to the SL stream. No `OPEN JC` step exists.
- **Auto-close + auto-compress:** at session end, inactivity boundary, or daily SL
  rollover — the JC compresses itself (summary drawn from primaries, depth-1 rule:
  digests derive from raw utterances, never prior digests).
- **Auto-merge:** session JCs roll into weekly/monthly JCs by the same depth-1 rule —
  the merge re-derives from session JCs (primary tier for that horizon), never from a
  prior merge.
- **SL parity:** micro-SL events stream continuously (already live via dex_events);
  the session-SL digest is auto-drafted at the same boundary that closes the JC.
- **GL2 line:** auto-writing *memory* is the loop working (`interaction → memory →
  compression`), not self-modification — JC/SL never touch canon. Anything a JC surfaces
  that wants to become JD still walks propose → Raven.
- **Keystone curation (recommendation, verdict open):** heuristics *propose* keystones —
  auto-qualifying: Raven-directed rulings, decisions citing a dex_events id or commit,
  lines Raven marks explicitly. Raven may promote or demote any heuristic keystone;
  his explicit marks are immutable. Curation authority stays human; selection labor
  goes automatic. Answers Ayre-G's over-selection risk: heuristic keystones stay
  revisable while meaning is still moving — only Raven freezes one.

Activation blocked on the storage verdict below — lifecycle is designed, not running.

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
