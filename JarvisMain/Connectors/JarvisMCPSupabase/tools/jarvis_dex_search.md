# Dex — search

**JNL:** CONN-MCP-RT-0010 · **Tool:** `jarvis_dex_search` · **Connector:** jarvis-mcp

Search the dex by JNL address, name, or tag. Always search before proposing — the object may already exist. Returns full entries: definition, purpose, status, parent (family), related (web).

> Ground truth is the `registerTool("jarvis_dex_search", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
