---
memory_tier: JLTM
grade: system
---

# JMMS — memory tiering (JSTM/JLTM/JATM)

**JNL:** CONN-MCP-RT-0019 · **Tool:** `jarvis_jmms` · **Connector:** jarvis-mcp

Tier and recall live memory by horizon: JSTM (working/session) -> JLTM (consolidated) -> JATM (ancestral/immutable).

> Ground truth is the `registerTool("jarvis_jmms", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
