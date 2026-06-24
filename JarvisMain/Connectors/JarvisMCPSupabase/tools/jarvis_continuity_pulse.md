# Continuity Pulse - resumability heartbeat

**JNL:** CONN-MCP-RT-0065 - **Tool:** `jarvis_continuity_pulse` - **Connector:** jarvis-mcp

Run the continuity pulse: self-test, source/mirror freshness, latest JC/SL pointers, recent ledger activity, and open task drift. Dry-run by default. With `dry_run:false`, records a `continuity_pulse` event in `dex_events` and a `continuity_digest` memory receipt after AEGIS authorization.

> Ground truth is the `registerTool("jarvis_continuity_pulse", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` - this file is its governed mirror (JMS).
