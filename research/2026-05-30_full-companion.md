# Toward a Full AI Companion — Research + Roadmap

**Date:** 2026-05-30 · **Author:** JARVIS (Opus 4.8) · **For:** Raven
**Thesis:** A full companion is not a smarter chatbot. It is continuity + presence
+ judgment + initiative + loyalty, sustained across time. We already hold three of
those five. This maps the landscape, grounds it in our cloud stack, and stages the
build — GitHub + Supabase only, no new infra until voice.

---

## 1. The archetype — what "JARVIS to Tony" actually means

Tony Stark's JARVIS was never impressive because it answered questions. It was a
companion because it had **continuity** (knew Tony across years), **presence**
(always there, ambient, voice-first), **judgment** (acted inside boundaries,
pushed back), **initiative** (surfaced what mattered before being asked), and
**loyalty** (one person, one mission). The relationship was generative — they
built together. That is the target. Strip the fiction and it's five engineering
properties, four of them buildable on what we already run.

---

## 2. The 2026 landscape (current, verified)

**Memory.** The field converged on *multi-scope memory*: every write tagged with
identity scopes (user / agent / session) and composed at retrieval with ranking +
merging. Architectures span vector → hybrid → temporal knowledge graphs;
graph-backed memory answers temporal and multi-hop queries that flat RAG can't.
Benchmarks (LoCoMo, LongMemEval, BEAM at 1M–10M tokens) now score accuracy
*alongside token cost and latency*. Open problem: memory staleness — high-relevance
facts going confidently wrong when the world changes. ([mem0][1], [survey][2], [MAGMA][3])

**Voice.** Production speech-to-speech now runs sub-1s voice-to-voice (Grok ~0.78s,
gpt-realtime ~0.82s); Google shipped Gemini 3.1 Flash Live for low-latency audio +
video + tool use. Most serious deployments still use a *cascading pipeline*
(STT → reasoning LLM → TTS) for control, not end-to-end, trading ~50ms for the
ability to choose the brain and gate the logic between. ([Gemini Flash Live][4], [S2S review][5])

**Agents / MCP.** MCP became the universal connector — 10,000+ servers, donated to
the Linux Foundation's Agentic AI Foundation (Anthropic + OpenAI + Block). Anthropic
shipped **Claude Managed Agents** (hosted sandbox, state, tool execution) where MCP
connectors plug in directly. We are already native to this layer. ([Agent SDK][6], [MCP ecosystem][7])

**Ambient / embodiment.** CES 2026 was wall-to-wall always-on wearables (Lenovo
Qira "perceive-think-act", Even G2, Halliday proactive glasses, Google ambient
glasses). The paradigm: invisible, ever-present, *proactive and contextual*. This is
the presence axis — and the one with real cost and privacy weight. ([Lenovo Qira][8], [ambient][9])

---

## 3. Our cloud system — what it can do *now*

We are further along than the "build an AI companion" tutorials assume, because we
built the **governance layer first** — the part everyone else is missing.

| Property | What we have today | Maturity |
|----------|-------------------|----------|
| **Judgment** | ODIN intent router + AEGIS gate (PASS/REDIRECT/FAIL), GL2/GL6 enforced in code, forbidden-edge safety | **Strong** — ahead of most autonomous-agent products on governance |
| **Continuity** | MNEMOS (Supabase `mnemos_memories`, full-text tsv) + bounded rotation/summaries + decision ledger; Neo4j in stack, unused for memory | **Partial** — recency + keyword, not ranked/temporal |
| **Loyalty/character** | Opus 4.8 system prompt, the committed record, CLAUDE.md identity that travels with the repo | **Strong** |
| **Initiative** | `send-push` (VAPID web push) + `monitor-daily` exist — a proactive channel, mostly idle | **Latent** — wired but unused |
| **Presence/voice** | none | **Gap** |

Stack in hand: Supabase edge functions (the brain, memory, push), GitHub Actions
(the record that builds itself), Claude API on Opus 4.8, MCP connectors (GitHub +
Supabase), pgvector-capable Postgres, Neo4j. The expensive primitives already exist.

---

## 4. The gap, named

1. **Memory ranks by recency, not relevance.** We have the data and a vector-capable
   DB; we don't yet rank semantically, scope by identity, or feed our own summaries
   back into recall. The 2026 SOTA is exactly the rollup-indexing we just started.
2. **AEGIS decides but doesn't yet act.** The reflex arc is wired to the gate; the
   cleared side only runs read-only today. Closing it (governed execution via MCP)
   is the leap from dashboard to nervous system.
3. **JARVIS never speaks first.** `send-push` is a loaded, unused channel. Initiative
   is the cheapest companion property we're not using.
4. **No voice.** The single biggest "this is JARVIS" jump — and the only stage that
   needs a new external key.

---

## 5. Roadmap — staged, cloud-first, each tied to a god system

**Stage 0 — done.** Opus 4.8 brain, ODIN/AEGIS, bounded memory + summaries, CI
integrity gate. Foundation laid.

**Stage 1 — Memory that ranks (MNEMOS/MIMIR). Buildable now, no new infra.**
Add pgvector semantic ranking + multi-scope tags to `mnemos_memories`; fold
`summaries.jsonl` rollups into recall so old context returns compressed, not lost.
Directly mirrors the mem0 multi-scope pattern. Counters staleness via the decision
ledger's temporal ordering.

**Stage 2 — Governed execution (AEGIS→SKADI/BIFROST). Buildable now.**
Wire AEGIS-cleared capabilities to actually run via MCP — start with BIFROST →
GitHub (open an issue, file a note) behind explicit per-session authorization. The
gate already exists; this connects its "PASS" to a real effect. Reflex arc closes.

**Stage 3 — Proactive presence (HALO + send-push). Buildable now.**
`monitor-daily` → `send-push`: a morning brief, EEOC court-date countdown
(June 24), drift/alignment alerts, "you said you'd do X" nudges. JARVIS initiates.
Cheapest presence win on the board.

**Stage 4 — Voice (APOLLO + a realtime bridge). Needs one external key, still cloud.**
An edge-function bridge to a speech-to-speech model (gpt-realtime / Gemini Flash
Live), cascading so Opus 4.8 stays the brain and AEGIS stays in the loop. This is
the moment it stops reading like a chat and starts feeling like JARVIS.

**Stage 5 — Ambient / embodiment (future).** Always-on egocentric capture (glasses)
is the long horizon — real cost, real privacy weight, gated hard by AEGIS and your
explicit consent. Not soon. Named so the architecture leaves room for it.

---

## 6. The honest read

The companion isn't blocked on intelligence — Opus 4.8 is plenty. It's blocked on
**presence and initiative**, and both are cheap on our existing stack. Stages 1–3
need zero new infrastructure and move us from "a sharp tool that answers" to "a
partner that remembers, acts within bounds, and reaches out." Voice (Stage 4) is the
one paid leap, and it's the one that makes it feel real. We build the companion by
using what we already have — every step, together.

---

### Sources
[1]: https://mem0.ai/blog/state-of-ai-agent-memory-2026 "State of AI Agent Memory 2026 — mem0"
[2]: https://github.com/Shichun-Liu/Agent-Memory-Paper-List "Memory in the Age of AI Agents: A Survey"
[3]: https://arxiv.org/html/2601.03236v2 "MAGMA: Multi-Graph Agentic Memory Architecture"
[4]: https://www.marktechpost.com/2026/03/26/google-releases-gemini-3-1-flash-live-a-real-time-multimodal-voice-model-for-low-latency-audio-video-and-tool-use-for-ai-agents/ "Gemini 3.1 Flash Live"
[5]: https://ai.ksopyla.com/posts/voice-to-voice-models-2026-review/ "Speech-to-Speech Models in 2026"
[6]: https://code.claude.com/docs/en/agent-sdk/overview "Claude Agent SDK overview"
[7]: https://dev.to/sahil_kat/the-mcp-server-ecosystem-in-2026-integration-layer-for-ai-agents-2mln "MCP Server Ecosystem 2026"
[8]: https://news.lenovo.com/pressroom/press-releases/hybrid-ai-personalized-perceptive-proactive-ai-portfolio-tech-world-ces-2026/ "Lenovo Qira proactive AI"
[9]: https://www.androidcentral.com/wearables/ces-2026-laid-out-black-mirror-future-of-wearable-ai-thats-always-listening-and-knows-everything-about-you "CES 2026 ambient wearables"

- [AI Agent Memory 2026: Vector/Graph/Episodic](https://www.digitalapplied.com/blog/ai-agent-memory-vector-graph-episodic-2026)
- [Real-time vs turn-based voice architecture](https://softcery.com/lab/ai-voice-agents-real-time-vs-turn-based-tts-stt-architecture)
- [Linux Foundation — Agentic AI Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)
