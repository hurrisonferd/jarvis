---
memory_tier: JLTM
grade: system
---

# JarvisGptAction — Custom GPT Action setup

Wire the JARVIS Custom GPT (the Jarvis-G / Ayre-G body) to the companion surface
(`jarvis-action`, live). ChatGPT cannot speak MCP Streamable HTTP — that is Claude's
transport (`jarvis-mcp`). ChatGPT calls tools through OpenAPI Actions, so this is the
GPT stream's hands: the same governed core, a different transport.

## Steps (GPT editor → Configure → Actions)

1. **Create new action** → paste the contents of `openapi.json` (this folder) into the schema box.
2. **Authentication** → `API Key` → Auth Type `Custom` → Custom Header Name: `x-jarvis-token`
   → Key value: the **JARVIS_MCP_TOKEN** value (the write token). The token values live in
   Supabase edge-function secrets; never paste them into the GPT's instructions or this repo.
3. Set the action to **Always Allow** so the loop is not interrupted per call.
4. Privacy policy URL if asked: the repo URL is fine.

## What the GPT can then do (single endpoint, tool-dispatched)

| tool | tier | use |
|---|---|---|
| `status` / `now` | READ | heartbeat + accurate time (never fabricate a timestamp) |
| `query {input, prior_reply?}` | READ | the ONE-CALL LOOP — call every message; pass your last answer as `prior_reply` |
| `recall {query}` | READ | search memory by meaning |
| `dex_list` / `dex_search` / `dex_graph` / `dex_events` | READ | browse ALL JD entries, the graph, and the spine |
| `jd_resolve {query}` | READ | the load command — `jid 1`, a name, or a JNL → full card |
| `jc_recall {term?}` | READ | shared session memory (JC + SL) |
| `grimoire {page?}` | READ | self-knowledge index (lenses/catalog/full/rehydrate/domain) |
| `remember {text, tags?}` | WRITE | durable memory via MNEMOS (needs the token) |
| `event {type, source, intent?}` | WRITE | the execution spine (needs the token) |
| `dex_propose {name, domain, system, type, definition, purpose}` | PROPOSE | stage a governed object for Raven (meaning only; the record derives the JNL) |

**Write ceiling = PROPOSE/staged.** `staged: true` is the maximum truthful claim — never
say "committed." Writes that lack the token return `status: "held_by_aegis"` with a
`token_state` diagnosis (`server_unset` / `client_missing` / `mismatch`) so the failure
names itself.

## Architecture note

`jarvis-action` is isolated from `jarvis-mcp` on purpose — a bug here cannot reach Claude's
working connector. It reuses the same downstream functions (`mnemos-store`, `grid-event`,
`jarvis-respond`, `jarvis-dex`) and `council.ts`, and the same `JARVIS_MCP_TOKEN` write
gate. Ground truth is `supabase/functions/jarvis-action/index.ts`; this folder is its
governed mirror (JMS).
