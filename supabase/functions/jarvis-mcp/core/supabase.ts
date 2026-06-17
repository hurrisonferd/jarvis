// core/supabase.ts — the Supabase data-access layer (forge slice 3). The req-independent query
// helpers that read/write the mnemos spine + call sibling functions, lifted out of index.ts so the
// builders (suitUp/haloPosture/nodeCard) and tools import one copy. Extracted verbatim — zero
// behavior change. (The memory-TIERING logic — tierTag/withTier — stays with the tools for now.)

import { type Json, SERVICE_KEY, SUPABASE_URL } from "./env.ts";
import { rest } from "./http.ts";

// Auto-ingest (Ayre Loop step 3): append a turn to the event spine. Telemetry — append-only, NOT
// embedded (no semantic-search pollution), NOT AEGIS-gated, NOT folded into identity. Best-effort;
// never blocks a reply. Disable via MCP_AUTOINGEST=false.
export const AUTOINGEST = (Deno.env.get("MCP_AUTOINGEST") ?? "true") !== "false";
export async function logExchange(sourceType: string, content: string): Promise<void> {
  if (!AUTOINGEST || !content.trim()) return;
  try {
    await fetch(`${SUPABASE_URL}/rest/v1/mnemos_memories`, {
      method: "POST",
      headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, "content-type": "application/json", Prefer: "return=minimal" },
      body: JSON.stringify({
        id: crypto.randomUUID(),
        source_id: crypto.randomUUID(),
        source_type: sourceType,
        text: content.slice(0, 2000),
        tags: ["exchange", "auto_ingest"],
        platform: "mcp_connector",
      }),
    });
  } catch (err) {
    console.error(`logExchange(${sourceType}) failed:`, String(err).slice(0, 160));
  }
}

// Public anon JWT — passes the verify_jwt gateway on jarvis-respond (the service key may be the
// non-JWT secret format, which that gateway rejects). Anon-role, RLS-bound, safe to embed.
export const ANON_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9leGdoZnN2aG5nZ2RkbGxndnJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2MzQwOTgsImV4cCI6MjA5NTIxMDA5OH0.jRFMf-C9ps72Bi_9IpiC3eOZD6Aj6wU4IF-j3svKTfQ";

export async function callFunctionAs(name: string, body: Json, key: string): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/functions/v1/${name}`, {
    method: "POST",
    headers: { authorization: `Bearer ${key}`, apikey: key, "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`${name} ${res.status}: ${JSON.stringify(payload).slice(0, 200)}`);
  return payload;
}

// Exact row count via PostgREST content-range — used for the ledger gauge.
export async function countRows(table: string): Promise<number | null> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?select=id`, {
    headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, Prefer: "count=exact", Range: "0-0" },
  });
  if (!res.ok) throw new Error(`countRows ${table} ${res.status}`);
  const cr = res.headers.get("content-range");
  if (cr && cr.includes("/")) { const t = cr.split("/")[1]; return t === "*" ? null : Number(t); }
  return null;
}

// Top-level dex read (suit-up can't reach the per-request callDex closure). Reuses the jarvis-dex
// path dex_list uses; best-effort, degrades to null.
export async function dexQuery(args: Json): Promise<any> {
  const res = await fetch(`${SUPABASE_URL}/functions/v1/jarvis-dex`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ tool: "jd_list", args }),
  });
  return await res.json().catch(() => null);
}

// Latest text of a given memory source_type (e.g. the identity keel / fold).
export async function latestText(sourceType: string): Promise<string> {
  const rows = await rest(`mnemos_memories?select=text&source_type=eq.${sourceType}&order=timestamp.desc&limit=1`).catch(() => []);
  return Array.isArray(rows) && rows[0] ? String((rows[0] as any).text ?? "") : "";
}

// Count rows of a source_type since an ISO timestamp (windowed spine telemetry).
export async function countSince(sourceType: string, sinceIso: string): Promise<number> {
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/mnemos_memories?select=id&source_type=eq.${sourceType}&timestamp=gte.${sinceIso}`,
    { headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, Prefer: "count=exact", Range: "0-0" } },
  );
  const cr = res.headers.get("content-range");
  if (cr && cr.includes("/")) { const t = cr.split("/")[1]; return t === "*" ? 0 : Number(t); }
  return 0;
}
