# Memory Lane — JC/SL relationship memory

**JNL:** CONN-MCP-RT-0023 · **Tool:** `jarvis_jc_recall` · **Connector:** jarvis-mcp

Read conversation containers (JC) and star-log digests (SL) — the relationship memory every stream shares.
Use day/week/month pointers when you need a structured slice; timestamps are retrieval pointers, not decoration. The connector can return day/week/month windows and group them by day so summaries stay readable after pruning.

> Ground truth is the `registerTool("jarvis_jc_recall", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
