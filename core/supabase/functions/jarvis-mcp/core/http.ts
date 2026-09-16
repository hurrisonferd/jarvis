// core/http.ts — BLACKWALL MCP data-plane firewall.
//
// The MCP runtime holds service credentials internally. Helpers therefore enforce
// a second boundary so an open/read-looking tool cannot casually turn that broad
// credential into private data projection or mutation.

import { type Json, SERVICE_KEY, SUPABASE_URL } from "./env.ts";

export function text(content: unknown) {
  return {
    content: [
      {
        type: "text" as const,
        text: typeof content === "string" ? content : JSON.stringify(content, null, 2),
      },
    ],
  };
}

const HELD_FUNCTIONS = new Set([
  // Legacy semantic search uses server authority and predates owner-scoped private-read
  // binding at the MCP request. Explicit governed memory APIs must replace it.
  "mnemos-search",
  "mnemos-embed",
]);

export async function callFunction(name: string, body: Json): Promise<unknown> {
  if (HELD_FUNCTIONS.has(name)) {
    throw new Error(`${name}: HELD_BY_BLACKWALL_PRIVATE_READ_AUTH_REQUIRED`);
  }
  const res = await fetch(`${SUPABASE_URL}/functions/v1/${name}`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${SERVICE_KEY}`,
      apikey: SERVICE_KEY,
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`${name}: UPSTREAM_${res.status}`);
  return payload;
}

// Reference/system metadata allowed through the generic service-role reader.
// Anything resident-content-bearing must get a dedicated owner-scoped capability.
const SAFE_READ_TABLES = new Set([
  "jnl_registry",
  "jd_entries",
  "jd_proposals",
  "dex_control",
  "dex_events",
  "jip_entries",
  "execution_trace",
  "node_keys",
  "musicos_tracks",
  "musicos_observations",
  "musicos_source_receipts",
]);

const FORBIDDEN_SELECTS: Record<string, RegExp> = {
  execution_trace: /(^|,)(payload|intent)(,|$)|\*/i,
  dex_events: /(^|,)detail(,|$)|\*/i,
  node_keys: /(^|,)(owner|assertion)(,|$)|\*/i,
  musicos_tracks: /(^|,)(media_ref|fingerprint)(,|$)|\*/i,
  musicos_observations: /(^|,)(interpretation|factual_features|media_ref)(,|$)|\*/i,
};

function parseRestTarget(path: string): { table: string; query: URLSearchParams } {
  const q = path.indexOf("?");
  const table = (q >= 0 ? path.slice(0, q) : path).replace(/^\/+/, "");
  const query = new URLSearchParams(q >= 0 ? path.slice(q + 1) : "");
  return { table, query };
}

function assertSafeRestRead(path: string): void {
  const { table, query } = parseRestTarget(path);
  if (table.startsWith("rpc/")) throw new Error("REST_RPC_HELD_BY_BLACKWALL");
  if (!SAFE_READ_TABLES.has(table)) throw new Error(`PRIVATE_TABLE_HELD_BY_BLACKWALL:${table}`);

  const select = query.get("select") ?? "";
  const forbidden = FORBIDDEN_SELECTS[table];
  if (forbidden && (!select || forbidden.test(select.replace(/\s+/g, "")))) {
    throw new Error(`PRIVATE_COLUMNS_HELD_BY_BLACKWALL:${table}`);
  }

  const limit = query.get("limit");
  if (limit !== null) {
    const n = Number(limit);
    if (!Number.isInteger(n) || n < 1 || n > 500) throw new Error("REST_LIMIT_OUT_OF_BOUNDS");
  }
}

export async function rest(
  path: string,
  opts?: { method?: string; body?: unknown; prefer?: string },
): Promise<unknown> {
  const method = (opts?.method ?? "GET").toUpperCase();

  // Generic service-role effects are disabled. Effect-capable tools must use a
  // request-bound gate and a purpose-built effect helper/capability instead.
  if (method !== "GET") {
    throw new Error("GENERIC_REST_EFFECT_HELD_BY_BLACKWALL");
  }

  assertSafeRestRead(path);

  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method: "GET",
    headers: {
      authorization: `Bearer ${SERVICE_KEY}`,
      apikey: SERVICE_KEY,
      "content-type": "application/json",
    },
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`rest: UPSTREAM_${res.status}`);
  return payload;
}
