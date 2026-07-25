---
memory_tier: JLTM
grade: system
---

# Grid — Register Signing Key

**JNL:** CONN-MCP-RT-0016 · **Tool:** `jarvis_node_register_key` · **Connector:** jarvis-mcp

Register this node's PUBLIC signing key + identity certificate (generated off-system by Raven via operations/scripts/grid_keygen.mjs). The node verifies the Ed25519 certificate against the rebuilt identity assertion before storing — only the holder of the private key can register. Token-gated; before calling, show Raven the public_key and let him Allow/Deny. The private key never touches this system.

> Ground truth is the `registerTool("jarvis_node_register_key", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
