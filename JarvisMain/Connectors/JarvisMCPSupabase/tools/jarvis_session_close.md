# Session Close — JSTM purge/promote

**JNL:** CONN-MCP-RT-0065 · **Tool:** `jarvis_session_close` · **Connector:** jarvis-mcp

Close out a session by resolving JSTM rows: preview the working set, promote selected entries to JLTM, or purge the session-only residue by tagging it closed. Use this at the boundary so session residue does not leak forward.

> Ground truth is the `registerTool("jarvis_session_close", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
