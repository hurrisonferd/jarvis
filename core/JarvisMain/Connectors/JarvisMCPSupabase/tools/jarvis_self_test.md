---
memory_tier: JLTM
grade: system
---

# Self Test — scry the live arsenal

**JNL:** CONN-MCP-RT-0034 · **Tool:** `jarvis_self_test` · **Connector:** jarvis-mcp

Exercise the connector's own subsystems and report a health matrix in one call: GitHub, Supabase, the dex, code search, and the deployed version.

> Ground truth is the `registerTool("jarvis_self_test", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
