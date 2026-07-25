# Cecil — carry context to the next session

**JNL:** CONN-MCP-RT-0066 · **Tool:** `jarvis_cecil` · **Connector:** jarvis-mcp

The carry transport. One session writes a carry slate; the next session (any model/stream) reads and inherits it. Three actions: carry (write), lift (read+clear), peek (read without clearing). 24h TTL, companion-scoped, one-time lift.

> Ground truth is the `registerTool("jarvis_cecil", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
