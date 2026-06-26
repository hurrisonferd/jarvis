---
memory_tier: JLTM
grade: system
---

# MNEMOS Recall

**JNL:** CONN-MCP-RT-0003 · **Tool:** `jarvis_recall` · **Connector:** jarvis-mcp

Search JARVIS live memory by meaning. Uses the deployed MNEMOS search function and Jina-backed pgvector when configured.

> Ground truth is the `registerTool("jarvis_recall", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
