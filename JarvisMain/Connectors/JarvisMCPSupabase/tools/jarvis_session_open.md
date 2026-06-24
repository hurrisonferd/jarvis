# Session Open — continuity bootstrap

**JNL:** CONN-MCP-RT-0064 · **Tool:** `jarvis_session_open` · **Connector:** jarvis-mcp

Run this first in a fresh session. It returns the continuity bootstrap packet: live self-test, latest JC/SL pointers, resumability receipt, source basis, repo head, and verification time.

> Ground truth is the `registerTool("jarvis_session_open", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
