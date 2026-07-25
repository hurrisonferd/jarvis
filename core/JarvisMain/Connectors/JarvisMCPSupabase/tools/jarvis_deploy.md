---
memory_tier: JLTM
grade: system
---

# Deploy — redeploy an edge function

**JNL:** CONN-MCP-RT-0037 · **Tool:** `jarvis_deploy` · **Connector:** jarvis-mcp

Redeploy a Supabase edge function (dispatch the deploy workflow) so it picks up new secrets or code.

> Ground truth is the `registerTool("jarvis_deploy", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
