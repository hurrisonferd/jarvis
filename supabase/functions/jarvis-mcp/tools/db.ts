// tools/db.ts — the DB vision tool group (forge slice 5: the first tool-group cut). Read-only
// Supabase table inspection. Proves the pattern: a tool module imports its helpers from core/* and
// exports registerXxx(server); buildServer just calls it. (These are reads — no req/AEGIS, so the
// signature is registerDbTools(server). Write groups will be registerXxx(server, req).)

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { rest, text } from "../core/http.ts";
import { countRows } from "../core/supabase.ts";

const KNOWN_TABLES = ["jnl_registry", "jd_entries", "jd_proposals", "dex_events", "mnemos_memories", "jc_objects", "sl_objects", "jip_entries", "node_messages", "node_keys", "execution_trace", "dex_control"];

export function registerDbTools(server: McpServer): void {
  server.registerTool(
    "jarvis_db_inspect",
    { title: "DB — inspect", description: "List known Supabase tables with row counts — the database landscape. Read-only.", inputSchema: {} },
    async () => {
      const out: Record<string, number | string> = {};
      for (const tbl of KNOWN_TABLES) {
        try { out[tbl] = (await countRows(tbl)) ?? "?"; } catch { out[tbl] = "n/a"; }
      }
      return text({ ok: true, tables: out });
    },
  );
  server.registerTool(
    "jarvis_db_read",
    { title: "DB — read", description: "Query any public table (PostgREST). e.g. table:'jnl_registry', query:'status=eq.ACTIVE&select=jnl,name&limit=20'. Read-only.", inputSchema: { table: z.string().min(1).max(60), query: z.string().max(300).optional().default("") } },
    async ({ table, query }) => {
      try { return text({ ok: true, table, rows: await rest(`${table}?${query}`) }); }
      catch (e) { return text({ ok: false, table, error: String(e).slice(0, 200) }); }
    },
  );
  server.registerTool(
    "jarvis_db_schema",
    { title: "DB — schema", description: "Show a table's columns (sampled from a row). Read-only.", inputSchema: { table: z.string().min(1).max(60) } },
    async ({ table }) => {
      try { const r = await rest(`${table}?select=*&limit=1`) as any[]; return text({ ok: true, table, columns: r[0] ? Object.keys(r[0]) : [], note: r[0] ? "from a sample row" : "table empty" }); }
      catch (e) { return text({ ok: false, table, error: String(e).slice(0, 200) }); }
    },
  );
}
