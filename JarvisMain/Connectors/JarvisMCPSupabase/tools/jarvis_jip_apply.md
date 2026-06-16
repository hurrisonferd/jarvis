# JIP — apply (propose to git)

**JNL:** CONN-MCP-RT-0052 · **Tool:** `jarvis_jip_apply` · **Connector:** jarvis-mcp

Apply an approved JIP's delta git-first: write the field override into jd/patches.json as a PR. AEGIS-gated.

> Ground truth is the `registerTool("jarvis_jip_apply", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
