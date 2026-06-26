---
memory_tier: JLTM
grade: system
---

# Voice Brief — pre-warm a sealed session

**JNL:** CONN-MCP-RT-0018 · **Tool:** `jarvis_voice_brief` · **Connector:** jarvis-mcp

Emit a tight, spoken-style state digest for runtimes that cannot call tools
(ChatGPT voice mode, free tiers). Generate it in a tool-capable session, then
read or paste it at the start of the sealed one: current record size, work in
flight, pending decisions, recent events. The sealed mind starts warm.
Read-only, no token needed.

> Ground truth is the `registerTool("jarvis_voice_brief", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
