---
memory_tier: JLTM
grade: system
---

# Dex — graph (node + full neighborhood)

**JNL:** CONN-MCP-RT-0020 · **Tool:** `jarvis_dex_graph` · **Connector:** jarvis-mcp

Pull everything on one governed object: its full entry plus every related and cross-referenced neighbor.

> Ground truth is the `registerTool("jarvis_dex_graph", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
