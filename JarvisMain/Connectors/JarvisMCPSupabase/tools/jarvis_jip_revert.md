# JIP — revert (propose to git)

**JNL:** CONN-MCP-RT-0053 · **Tool:** `jarvis_jip_revert` · **Connector:** jarvis-mcp

Roll a JD back git-first: remove its entry from jd/patches.json as a PR so seed restores the source value. AEGIS-gated.

> Ground truth is the `registerTool("jarvis_jip_revert", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
