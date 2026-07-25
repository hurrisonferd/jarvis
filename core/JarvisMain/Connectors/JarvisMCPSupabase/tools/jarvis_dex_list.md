---
memory_tier: JLTM
grade: system
---

# Dex — list governed objects

**JNL:** CONN-MCP-RT-0009 · **Tool:** `jarvis_dex_list` · **Connector:** jarvis-mcp

List the dex (JD/JNL registry — the shared truth across all agents and sessions). Open every session with status:'ACTIVE' to load true architecture state instead of reconstructing it from chat memory. Filter by status/class/tier/type/tag.

> Ground truth is the `registerTool("jarvis_dex_list", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
