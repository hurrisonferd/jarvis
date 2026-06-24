# AEGIS Event

**JNL:** CONN-MCP-RT-0008 · **Tool:** `jarvis_event` · **Connector:** jarvis-mcp

Submit an event to the JARVIS execution spine through grid-event. AEGIS-gated: before calling, show Raven the event and let him Allow or Deny. On Allow, call this tool (it commits if the connector carries the token). On Deny, do not call it.

> Ground truth is the `registerTool("jarvis_event", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
