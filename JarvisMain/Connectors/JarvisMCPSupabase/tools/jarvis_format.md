---
memory_tier: JLTM
grade: system
---

# JARVIS Format — same-turn close (optional)

**JNL:** CONN-MCP-RT-0006 · **Tool:** `jarvis_format` · **Connector:** jarvis-mcp

Optional same-turn close: call with Raven's input and your drafted JARVIS answer to review + log THIS turn's output immediately, instead of the normal close (passing prior_reply on your next jarvis_query). Returns the council review (output_review verdict); if it FLAGs, correct your answer before sending. Do NOT also pass this same answer as prior_reply next turn — that would double-log it.

> Ground truth is the `registerTool("jarvis_format", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
