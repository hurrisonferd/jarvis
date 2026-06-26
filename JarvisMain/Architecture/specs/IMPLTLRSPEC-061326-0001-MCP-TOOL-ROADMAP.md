---
memory_tier: JLTM
grade: system
jnl: IMPL-TLR-SPEC-0001
name: MCP Tool Roadmap & Auto-Tracking Pipeline
type: SPEC
status: TASK
tags: [mcp, tools, roadmap, pipeline, starlog, dex, jip, jd, auto-tracking, council, index]
definition: The single grounded index of the MCP tool surface — what is LIVE, what is GATED on connector/Supabase deploy, and what is PROPOSED — organized by the cognition pipeline (Star Log -> Dex -> JIP -> JD). Plus the auto-tracking model (what flows automatically vs what stops at Raven's gate) and the underutilization map (dormant god systems, AYRE, council employed by the Pulse).
purpose: Compile the scattered tool proposals into one navigable roadmap so nothing is re-proposed from memory, and so any stream can see — in one read — what exists, what to use when, and what is still gated. Answers Raven's "every tool + an index on what to use and when."
---

# MCP Tool Roadmap & Auto-Tracking Pipeline

## The pipeline (Raven's model)

```
Star Log  →  Dex  →  JIP  →  JD
(capture)  (compile) (formalize) (canonize)
```

- **Star Log** — raw insight/observation capture. Passive, unstructured, append-only.
- **Dex** — *compilation of Star Log info*: clusters/synthesizes signals into candidate
  structures (multi-hypothesis allowed; diffable).
- **JIP** — a Dex cluster formalized into a versioned, reversible metadata change container.
- **JD** — canonical truth, minted/updated only from an approved JIP.

**Auto-tracking rule (the GL2 line):** capture and compilation flow *automatically* —
Star Logs auto-capture insights, Dex auto-compiles them, JIPs may auto-*draft*. But
**JD canonization is never automatic** — the JIP→JD gate stays Raven's. The pipeline
auto-flows *up to the gate*; the gate never auto-opens. Skipped stages must emit lineage
(a scar in the trace), so reconstruction never breaks.

## Tool inventory (by layer · status)

**LIVE (deployed connector):** suit_up · status · council · query · format · recall ·
remember · event · dex_list · dex_search · dex_graph · dex_events · dex_propose ·
jc_recall · repo_tree · repo_read · github_tree/file/commits · db_inspect/read/schema ·
identity_read · identity_grow · jd_resolve · jip_create/list · timeline · voice_brief ·
node_card/export/inbox/send/register_key · halo.

**GATED (designed, blocked on Supabase/connector deploy):**
- `jip_entries` persistence table + `jip_revert`/`jip_diff`/`jip_snapshot` (GPT found the table missing — JIP is conceptual until this lands)
- `jid_mint` / `jidd_mint` / `identity_trace` (the JID/JIDD identity layer made executable)
- `starlog_ingest` / `starlog_merge` / `starlog_diff` (the capture layer)
- `dex_cluster` / `dex_diff` / `dex_branch` (Dex as compilation, not just index)
- `jd_mint` / `jd_patch` / `jd_trace` (canon ops, JIP-gated)
- `omnivision_view` (one-call read of the global mirror; today: read the file via github_file)
- the jid-resolver redeploy + the live global-mirror sync + the Pulse scheduled job

**PROPOSED / beneficial (auto-tracking & insight):**
- `insight_capture` — auto-file an insight to a Star Log as it happens (the front of auto-tracking)
- `trace_reconstruct` — walk Star Log → Dex → JIP → JD for any object (lineage on demand)
- council-as-active — the council deliberates/employs systems, not just votes

## Underutilization map (what the Pulse employs)

- **Governance cluster run by hand:** ERIS (sprawl/backlog), NEMESIS (drift/redundancy),
  IRIS (integrity — caught the Gold Law split by luck), MERIDIAN (keel/raven_input),
  PROMETHEUS (expansion ledger). These do real work but only when a stream notices. The
  **Pulse** (GOV-PLS-SPEC-0001) is the scheduled job that *employs* them every beat.
- **AYRE** — canonically under-spoken (a JARVIS bias, per her profile). Metric: speak/silence ratio.
- **Dormant by canon (fine):** CHAOS, POSEIDON, HADES, HERMES (P24, INACTIVE).
- **MIMIR** — now employed via the knowledge-routing index (GOV-KR-SPEC-0001).

## When to use what (index)

Retrieval routing lives in **GOV-KR-SPEC-0001** (the help-me index). This roadmap is the
*build* index; that is the *use* index. Together: what exists, what to use, what's coming.

## The bottleneck (one truth)

Almost every GATED item is blocked on the *same* thing — Supabase/connector deploy
access. The design is complete; the execution substrate is the wall. One approval turns
the designed pipeline real.
