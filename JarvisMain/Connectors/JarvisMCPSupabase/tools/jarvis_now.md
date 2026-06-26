---
memory_tier: JLTM
grade: system
---

# Now — accurate time

**JNL:** CONN-MCP-RT-0041 · **Tool:** `jarvis_now` · **Connector:** jarvis-mcp

Return the current accurate server time (UTC + US Eastern + weekday + unix) — the model cannot tell time, so this is the clock.

> Ground truth is the `registerTool("jarvis_now", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
