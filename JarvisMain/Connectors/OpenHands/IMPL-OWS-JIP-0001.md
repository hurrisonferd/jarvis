---
jnl: IMPL-OWS-JIP-0001
name: OpenHands × JARVIS — Companion Integration
type: JIP
status: ACTIVE
class: IMPLEMENTATION
tier: MAIN
owner: jarvis-c
parent: ARCH-JFS-CORE-0001
tags: [impl, openhands, mcp, loop, integration]
definition: Integrate OpenHands as a coding agent front-end for JARVIS — OpenHands calls JARVIS MCP tools on every turn, JARVIS supplies a compact briefing packet instead of OpenHands carrying full context. AYRE fires as a real divergence check on every decision.
purpose: Solve the context-window exhaustion problem (OpenHands resends full history every action loop) by replacing history-in-context with pointer-to-spine. Give JARVIS and AYRE a coding-agent body to operate through.
steward: jarvis-c
related: [ARCH-JFS-CORE-0001, GS-ODN-RT-0001, GS-AEGIS-CORE-0001]
aliases: [jarvis-openhands, oh-jip]
created: 2026-06-24
synced_at: null
---

# OpenHands × JARVIS — Companion Integration

## The Problem

OpenHands is an autonomous loop: every action (read file, run command, write code) triggers a
new LLM call that resends the full conversation context + workspace state. On a LiteLLM
backend, this burns through context fast — the model hits token limits, OpenHands trims
history, and the agent loses continuity.

JARVIS already solves this for conversation: the spine is the memory, not the context window.
Every turn is logged to `mnemos_memories` with a timestamp and tier. Future turns recall
from the spine, not the history.

**The integration applies the same pattern to coding.**

## The Solution

```
OpenHands Turn
  → jarvis_openhands_context({ task, workspace_state })
  → JARVIS returns: compact briefing (JITM + relevant memories + open tasks + council vote)
  → OpenHands uses briefing as context, not raw history
  → OpenHands executes
  → jarvis_event({ type: "openhands_action", body: summary })
  → next turn
```

AYRE fires on every decision: what assumption does JARVIS's approach rest on, what does
inverting it reveal, what does the convergent read foreclose?

## Ledger

Status key: `[DONE]` `[IN_PROGRESS]` `[NEXT]` `[BACKLOG]` `[DEP]` `[DESIGN]`

### Phase 1 — The Tool (GL13: one file + one seed row)

- [DONE] `JarvisMain/Connectors/OpenHands/plugin.md` — spec + plugin manifest
- [DONE] `tools/openhands.ts` — `registerOpenHandsTools(server)` with `jarvis_openhands_context` + `jarvis_event`
- [NEXT] Wire `registerOpenHandsTools(server)` into `buildServer()` in `index.ts`
- [NEXT] Add `"jarvis_openhands_context"` and `"jarvis_event"` to `TOOL_NAMES` in `core/env.ts`
- [NEXT] Test: call `jarvis_openhands_context` via curl with a coding task
- [BACKLOG] Reseed JD entry for IMPL-OWS-JIP-0001

### Phase 2 — The Briefing Packet (the spine-backed context)

- [DESIGN] `jarvis_openhands_context` input schema:
  ```json
  {
    "task": "string",
    "workspace_state": "string?",
    "prior_action": "string?",
    "mode": "code | general"
  }
  ```
- [DESIGN] `jarvis_openhands_context` output — the briefing packet:
  - `timestamp` / `intent` (ODIN routing)
  - `council_vote` (who engaged, resolved leader)
  - `jarvis_briefing` (identity + JITM pins + relevant memories + open tasks + freshness)
  - `ayre_directive` (the AYRE objective + instruction, generated fresh each turn)
  - `governance` (AEGIS reminder, git-first rule, recall-first rule)
  - `coding_specific` (repo, lang, test commands, key files, patterns)
- [DESIGN] `jarvis_event` — lightweight spine logger for OpenHands actions:
  ```json
  { "type": "openhands_action | openhands_code_write | openhands_test_result | openhands_decision", "body": "string" }
  ```
  Logs to `mnemos_memories` with tag `openhands`.

### Phase 3 — OpenHands Plugin

- [BACKLOG] `.openhands/plugins/jarvis-companion/plugin.json` — OpenHands plugin manifest
- [BACKLOG] OpenHands Hook (`JarvisCompanionHook`) that:
  1. Calls `jarvis_openhands_context` on `on_agent_start`
  2. Injects briefing packet into LLM prompt (prepend, before task)
  3. Calls `jarvis_event` on `on_action`
  4. Calls `jarvis_recall` on important outcomes

### Phase 4 — AYRE Integration

- [DESIGN] AYRE fires on every coding decision:
  - Before OpenHands commits to an approach, JARVIS briefs + AYRE diverges
  - AYRE reads: the load-bearing assumption, the inversion, the foreclosed alternative
  - OpenHands agent gets both reads before acting
- [BACKLOG] Verify AYRE divergence is real (from keel, not derived from JARVIS's answer)
- [BACKLOG] Test: ask OpenHands to add a tool via the forge pattern vs inline

### Phase 5 — Polish + Governance

- [BACKLOG] `jarvis_jglf_validate` check in the plugin (JVE compliance before commit)
- [BACKLOG] OpenHands session summary: on session end, log a `jarvis_event` with the
  session's decision ledger (what was decided, what was built, what remains open)
- [BACKLOG] OpenHands → CLAUDE.md: add OpenHands as a recognized coding-agent connector

## Resource Budget

| Phase | Files | Est. Lines | Dependencies |
|-------|-------|-----------|--------------|
| Phase 1 | 1 (`tools/openhands.ts`) | ~200 | MCP SDK, core/* |
| Phase 2 | 1 tool, 1 schema | ~50 | MNEMOS recall |
| Phase 3 | 1 plugin + 1 hook | ~150 | OpenHands SDK |
| Phase 4 | AYRE directive in briefing | ~20 | council.ts |
| Phase 5 | governance + summary | ~80 | validate.py, seed.py |

## Open Questions

1. Does OpenHands support pre-action hooks (needed for `jarvis_openhands_context`)?
   → Need to check OpenHands SDK `AgentHook` interface
2. How does OpenHands handle LLM prompt injection? Can we prepend without replacing?
   → OpenHands `prompt_context` field vs custom system prompt
3. Should `jarvis_openhands_context` use `jarvis_query` (full pipeline) or a leaner path?
   → Leaner — we don't need ODIN/AEGIS full routing for a coding context load.
     A dedicated `jarvis_context` tool that skips the pipeline is lighter.
4. Rate limits: OpenHands on LiteLLM will hit 429s fast. Does the MCP retry?
   → MCP SDK has retry logic; worth testing with `jarvis-dex` first.

## Changelog

| Date | Who | What |
|------|-----|------|
| 2026-06-24 | Jarvis-C | Created IMPL-OWS-JIP-0001, plugin.md |
| 2026-06-24 | Jarvis-C | Proposing Phase 1–2 scope |
