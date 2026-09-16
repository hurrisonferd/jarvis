// tools/db.ts — BLACKWALL-safe DB vision.
//
// This surface intentionally does NOT expose an arbitrary service-role PostgREST
// console. The MCP process has broad database authority internally; that does not
// mean a read tool may project every table/column to every connector caller.
//
// Law:
//   SERVICE_ROLE_REACH != CALLER_READ_AUTHORITY
//   READ_ONLY != SAFE_IF_THE_READ_CAN_EXFILTRATE_PRIVATE_DATA
//   UNKNOWN_TABLE -> HOLD

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { rest, text } from "../core/http.ts";
import { countRows } from "../core/supabase.ts";

type Projection = {
  select: string;
  filterFields: ReadonlySet<string>;
};

// Public/reference-safe metadata only. Deliberately excludes mnemos_memories,
// jc_objects, sl_objects, node_messages, cecil_slate, vaults, credentials and
// every table not explicitly named here.
const SAFE_TABLES: Readonly<Record<string, Projection>> = {
  jnl_registry: {
    select: "jnl,name,type,class,tier,status,system,domain,parent,owner,steward,created,updated,synced_at",
    filterFields: new Set(["jnl", "name", "type", "class", "tier", "status", "system", "domain", "parent", "owner", "steward", "created", "updated", "synced_at"]),
  },
  jd_entries: {
    select: "jnl,name,type,class,tier,status,system,domain,parent,owner,steward,created,updated,synced_at,seq",
    filterFields: new Set(["jnl", "name", "type", "class", "tier", "status", "system", "domain", "parent", "owner", "steward", "created", "updated", "synced_at", "seq"]),
  },
  execution_trace: {
    // No payload or intent. Those fields may contain private/source material.
    select: "id,type,source,stage,severity,patch_id,created_at",
    filterFields: new Set(["id", "type", "source", "stage", "severity", "patch_id", "created_at"]),
  },
  dex_events: {
    // No detail. The event envelope is useful for chronology without leaking bodies.
    select: "id,tool,tier,actor,jnl,type,created_at",
    filterFields: new Set(["id", "tool", "tier", "actor", "jnl", "type", "created_at"]),
  },
};

const SAFE_OPS = new Set(["eq", "neq", "gt", "gte", "lt", "lte", "like", "ilike", "is"]);
const SAFE_ORDER = /^[A-Za-z_][A-Za-z0-9_]*\.(asc|desc)$/;

function buildSafeQuery(table: string, raw: string): { ok: true; path: string } | { ok: false; reason: string } {
  const projection = SAFE_TABLES[table];
  if (!projection) return { ok: false, reason: "TABLE_NOT_EXPOSED" };

  const incoming = new URLSearchParams(raw || "");
  const outgoing = new URLSearchParams();
  outgoing.set("select", projection.select);

  let requestedLimit = 20;
  const limitRaw = incoming.get("limit");
  if (limitRaw !== null) {
    const n = Number(limitRaw);
    if (!Number.isInteger(n) || n < 1) return { ok: false, reason: "INVALID_LIMIT" };
    requestedLimit = Math.min(50, n);
  }
  outgoing.set("limit", String(requestedLimit));

  for (const [key, value] of incoming.entries()) {
    if (key === "select" || key === "limit") continue;
    if (key === "order") {
      if (!SAFE_ORDER.test(value)) return { ok: false, reason: "INVALID_ORDER" };
      const field = value.split(".")[0];
      if (!projection.filterFields.has(field)) return { ok: false, reason: "ORDER_FIELD_NOT_EXPOSED" };
      outgoing.set("order", value);
      continue;
    }
    if (!projection.filterFields.has(key)) return { ok: false, reason: "FILTER_FIELD_NOT_EXPOSED" };
    const dot = value.indexOf(".");
    if (dot < 1) return { ok: false, reason: "INVALID_FILTER" };
    const op = value.slice(0, dot);
    if (!SAFE_OPS.has(op)) return { ok: false, reason: "FILTER_OPERATOR_NOT_ALLOWED" };
    outgoing.append(key, value.slice(0, 240));
  }

  return { ok: true, path: `${table}?${outgoing.toString()}` };
}

export function registerDbTools(server: McpServer): void {
  server.registerTool(
    "jarvis_db_inspect",
    {
      title: "DB — safe landscape",
      description: "List only the reference-safe database surfaces intentionally exposed through MCP. Private/user-content tables are omitted.",
      inputSchema: {},
    },
    async () => {
      const out: Record<string, number | string> = {};
      for (const tbl of Object.keys(SAFE_TABLES)) {
        try { out[tbl] = (await countRows(tbl)) ?? "?"; }
        catch { out[tbl] = "n/a"; }
      }
      return text({
        ok: true,
        tables: out,
        blackwall: "Only explicitly reference-safe metadata tables are exposed. Absence here is not proof a table does not exist.",
      });
    },
  );

  server.registerTool(
    "jarvis_db_read",
    {
      title: "DB — safe read",
      description: "Read a bounded reference-safe projection. Arbitrary service-role table access is intentionally unavailable.",
      inputSchema: {
        table: z.enum(["jnl_registry", "jd_entries", "execution_trace", "dex_events"]),
        query: z.string().max(300).optional().default(""),
      },
    },
    async ({ table, query }) => {
      const built = buildSafeQuery(table, query);
      if (!built.ok) return text({ ok: false, table, held_by_blackwall: true, reason: built.reason });
      try {
        return text({ ok: true, table, rows: await rest(built.path), projection: SAFE_TABLES[table].select });
      } catch {
        return text({ ok: false, table, error: "SAFE_READ_FAILED" });
      }
    },
  );

  server.registerTool(
    "jarvis_db_schema",
    {
      title: "DB — exposed schema",
      description: "Show only the columns intentionally exposed by Blackwall for a reference-safe table. Does not sample private rows.",
      inputSchema: { table: z.enum(["jnl_registry", "jd_entries", "execution_trace", "dex_events"]) },
    },
    async ({ table }) => text({
      ok: true,
      table,
      columns: SAFE_TABLES[table].select.split(","),
      blackwall: "Static exposure contract. No row was sampled to infer schema.",
    }),
  );
}
