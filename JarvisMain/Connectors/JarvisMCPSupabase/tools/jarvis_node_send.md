# Grid — Send to Node

**JNL:** CONN-MCP-RT-0015 · **Tool:** `jarvis_node_send` · **Connector:** jarvis-mcp

Relay a message from this node to another node's inbox (BIFROST). Outbound action — before calling, show Raven the target + message and let him Allow or Deny. Commits only if the connector carries the token.

> Ground truth is the `registerTool("jarvis_node_send", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
