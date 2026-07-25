---
memory_tier: JLTM
grade: system
---

# MNEMOS Store

**JNL:** CONN-MCP-RT-0007 · **Tool:** `jarvis_remember` · **Connector:** jarvis-mcp

Write a durable memory through MNEMOS. AEGIS-gated: before calling, show Raven exactly what will be stored and let him Allow or Deny. On Allow, call this tool (it commits if the connector carries the token). On Deny, do not call it.

> Ground truth is the `registerTool("jarvis_remember", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
