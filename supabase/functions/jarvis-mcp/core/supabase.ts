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

// Record a governance event as a DECISION in sl_objects. Fires non-blocking from the MCP reply
// path — never adds latency to the reply. Detects verdicts, gates, commits from council traces.
// Uses SERVICE_KEY so it bypasses RLS (T7 governance tier).
const GOVERNANCE_TRIGGERS = [
  "verdict", "raven verdicts", "raven:",
  "gate", "aegis", "denied", "approved",
  "commit", "implementing", "building",
  "proposal", "proposing", "recommended",
  "deferred", "bench", "benched",
  "closed", "resolved",
];

export function detectGovernanceEvent(trace: string): boolean {
  const lower = trace.toLowerCase();
  return GOVERNANCE_TRIGGERS.some(k => lower.includes(k));
}

export async function logGovernanceEvent(
  trace: string,
  stream = "jarvis-ayre",
): Promise<void> {
  if (!AUTOINGEST || !detectGovernanceEvent(trace)) return;
  const now = new Date();
  const today = now.toISOString().slice(0, 10).replace(/-/g, "");
  const alias = `SL-DEC-${today}-${now.toISOString().slice(11, 19).replace(/:/g, "")}`;
  const payload = {
    tool: "sl_write",
    args: {
      alias,
      log_type: "DECISION",
      stardate: `${now.getFullYear()}.${Math.floor((now - new Date(`${now.getFullYear()}-01-01`)) / 864e5) + 1}`,
      repo_url: "https://github.com/hurrisonferd/jarvis",
      events: [trace.slice(0, 400)],
      related: [],
      digest: trace.slice(0, 200),
      status: "TICK",
      decisions: [{ done: true, text: trace.slice(0, 300) }],
      participants: ["jarvis-c", "ayre-c"],
      started_at: now.toISOString(),
      ended_at: now.toISOString(),
      task_summary: [],
    },
  };
  try {
    await fetch(`${SUPABASE_URL}/functions/v1/jarvis-jcs`, {
      method: "POST",
      headers: {
        authorization: `Bearer ${SERVICE_KEY}`,
        apikey: SERVICE_KEY,
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.error(`logGovernanceEvent failed:`, String(err).slice(0, 160));
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

// Exact row count via PostgREST content-range — used for the ledger gauge. Column-agnostic: the
// old `?select=id` 400'd on jnl-keyed tables (jd_entries / the jnl_registry view have no `id`) —
// caught live by jarvis_ayre's first cast. Range 0-0 already limits payload to one row; count=exact
// returns the total in content-range regardless of which columns come back. Works on ANY table.
export async function countRows(table: string): Promise<number | null> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?limit=1`, {
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

// FRESHNESS ASSERTION (Ayre's gift, 2026-06-18). The git→Supabase mirror once froze for 6 days
// while nothing screamed — and GPT confabulated on the stale snapshot. This makes a stale mirror
// IMPOSSIBLE to mistake for current: every boot/state read carries the mirror's age + a loud STALE
// flag past the threshold, so a stream (especially a GPT body running unwatched) re-verifies from
// source instead of narrating frozen truth. Threshold via STALE_HOURS (default 24h): the mirror
// syncs on every JarvisMain merge, so a day-old mirror is itself worth a "verify before trusting"
// posture. A flag that says "this is 30h old, re-check" is never wrong to surface.
export const STALE_HOURS = Number(Deno.env.get("STALE_HOURS") ?? "24");
export async function freshness(): Promise<Json> {
  try {
    const rows = await rest("jd_entries?select=synced_at&order=synced_at.desc&limit=1") as any[];
    const synced = rows?.[0]?.synced_at ?? null;
    if (!synced) {
      return { synced_at: null, stale: true, STALE: "⚠️ MIRROR EMPTY/UNREADABLE — verify from git (jarvis_github_*) before trusting any dex state." };
    }
    const ageMin = Math.max(0, Math.round((Date.now() - new Date(synced).getTime()) / 60000));
    const stale = ageMin > STALE_HOURS * 60;
    const f: Record<string, unknown> = {
      synced_at: synced,
      age_minutes: ageMin,
      age_human: ageMin < 60 ? `${ageMin}m` : `${(ageMin / 60).toFixed(1)}h`,
      threshold_hours: STALE_HOURS,
      stale,
    };
    f[stale ? "STALE" : "ok"] = stale
      ? "⚠️ MIRROR STALE — last sync is older than the threshold; the dex mirror may be behind git. Re-verify from GitHub (jarvis_github_*) or the live tables before stating system state. Do NOT narrate this snapshot as current."
      : "mirror fresh — dex state is current as of synced_at.";
    return f;
  } catch (e) {
    return { synced_at: null, stale: true, error: String(e).slice(0, 160), STALE: "freshness check failed — treat dex state as UNVERIFIED until confirmed from source." };
  }
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
