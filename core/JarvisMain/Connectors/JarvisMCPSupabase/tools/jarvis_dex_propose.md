---
memory_tier: JLTM
grade: system
---

# Dex — propose entry (JGPP/JIP/JD/BIO)

**JNL:** CONN-MCP-RT-0011 · **Tool:** `jarvis_dex_propose` · **Connector:** jarvis-mcp

Stage a new governed object in the dex. Supply MEANING ONLY — name, domain (e.g. PROJ), system (project code, e.g. DEO for Deoxys — see project-codes), type (JGPP|JIP|JD|BIO), definition, purpose, tags. The connector derives JNL/class/tier/owner and stages it for Raven's approval; approved entries materialize as governed repo files automatically. AEGIS-gated: show Raven the proposal and let him Allow or Deny before calling. NEVER construct a JNL by hand.

> Ground truth is the `registerTool("jarvis_dex_propose", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
