// grid-write — the GL5 write boundary, as a PURE + testable unit. The public anon
// key is read-only at the DB; every browser/script write flows through grid-write
// and is checked here against a strict (table, op) whitelist before the service
// role performs it. This file holds no I/O so it can be unit-tested in CI
// (node --experimental-strip-types). index.ts imports it — single source of truth.

export type Op = "insert" | "update" | "upsert" | "delete";

// Exactly the writes the browser + scripts perform. Nothing else is permitted.
export const WHITELIST: Record<string, Set<Op>> = {
  sessions:            new Set<Op>(["insert", "update"]),
  events:              new Set<Op>(["insert"]),
  mnemos_memories:     new Set<Op>(["insert"]),
  prometheus_log:      new Set<Op>(["insert"]),
  god_system_stats:    new Set<Op>(["update"]),
  push_subscriptions:  new Set<Op>(["upsert", "delete"]),
  rom_library:         new Set<Op>(["insert"]),
  save_states:         new Set<Op>(["insert"]),
  consensus_proposals: new Set<Op>(["insert", "update"]),
};

export type WriteReq = {
  table: string;
  op: string;
  data?: unknown;
  match?: Record<string, unknown> | null;
};

// The gate. Returns {ok:true} only for a whitelisted (table, op) with the shape
// that op requires (update/delete need a match filter; insert/upsert need a data
// object). Pure — no DB, no fetch. index.ts performs the write only when ok.
export function validateWrite(r: WriteReq): { ok: true } | { ok: false; error: string } {
  const allowed = WHITELIST[r.table];
  if (!allowed) return { ok: false, error: `table not writable: ${r.table}` };
  if (!allowed.has(r.op as Op)) return { ok: false, error: `op not allowed on ${r.table}: ${r.op}` };
  if ((r.op === "update" || r.op === "delete") && (!r.match || Object.keys(r.match).length === 0)) {
    return { ok: false, error: `${r.op} on ${r.table} requires a match filter` };
  }
  if ((r.op === "insert" || r.op === "upsert") && (r.data === null || typeof r.data !== "object")) {
    return { ok: false, error: `${r.op} on ${r.table} requires a data object` };
  }
  return { ok: true };
}
