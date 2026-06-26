---
memory_tier: JLTM
grade: system
---

# JARVIS — Suit Up

**JNL:** CONN-MCP-RT-0001 · **Tool:** `jarvis_suit_up` · **Connector:** jarvis-mcp

Activate JARVIS and display the full live system status (the HUD: identity, mission, all 27 God Systems, services, memory ledger, recent activity). Call this whenever Raven says 'JARVIS, suit up', 'activate JARVIS', 'bring JARVIS online', or asks to see full status. This is the activation command.

> Ground truth is the `registerTool("jarvis_suit_up", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
