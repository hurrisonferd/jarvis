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
// path — never adds latency to the reply. Detects governance-significant outputs.
// review.verdict is only "FLAG" or "PASS"; the signal is in council.summary keywords.
// Uses SERVICE_KEY so it bypasses RLS (T7 governance tier).
const GOVERNANCE_VERDICTS = [
  "gate", "aegis", "denied", "approved",
  "commit", "implementing", "deferred", "bench", "benched",
  "closed", "resolved", "flag",
];

export function detectGovernanceEvent(trace: string): boolean {
  // Only fire on output_review traces that flag or show real governance action
  if (!trace.includes("output_review")) return false;
  if (trace.includes("output_review=PASS")) return false; // clean pass — skip
  const lower = trace.toLowerCase();
  return GOVERNANCE_VERDICTS.some(k => lower.includes(k));
}

export async function logGovernanceEvent(trace: string): Promise<void> {
  if (!AUTOINGEST || !detectGovernanceEvent(trace)) return;
  const now = new Date();
  const today = now.toISOString().slice(0, 10).replace(/-/g, "");
  const alias = `SL-DEC-${today}-${now.toISOString().slice(11, 19).replace(/:/g, "")}`;
  const startOfYear = new Date(`${now.getFullYear()}-01-01`);
  const dayOfYear = Math.floor((now.getTime() - startOfYear.getTime()) / 864e5) + 1;
  const stardate = `${now.getFullYear()}.${dayOfYear}`;
  const payload = {
    tool: "sl_write",
    args: {
      alias,
      log_type: "DECISION",
      stardate,
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

// ── LEVEL 1 AUTONOMY ─────────────────────────────────────────────────────────
// AUTONOMY-ROADMAP-0001 L1: Observational. Fires on governance events + session close.
// All actions emit spine events (GL5: no silent mutation). Auditable via logExchange.
// ─────────────────────────────────────────────────────────────────────────────

/** Promote cold JSTM rows to JHTM on session close.
 * Candidates: JSTM rows with jstm_sub='session' older than 7 days.
 * Keeps last 20 (most recent), promotes the rest.
 * All promotions emit a jmms.promote event.
 */
export async function promoteSessionMemories(): Promise<void> {
  if (!AUTOINGEST) return;
  try {
    const cutoff = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
    const sessionRows = await rest(
      `mnemos_memories?select=id&memory_tier=eq.jstm&jstm_sub=eq.session&timestamp=lt.${cutoff}&order=timestamp.asc&limit=100`
    ) as any[];
    if (!sessionRows.length) return;
    const promote = sessionRows.slice(20); // keep last 20, promote rest
    if (!promote.length) return;
    const ids = promote.map((r: any) => r.id);
    await fetch(`${SUPABASE_URL}/rest/v1/mnemos_memories?id=in.(${ids.join(",")})`, {
      method: "PATCH",
      headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, "Content-Type": "application/json", Prefer: "return=minimal" },
      body: JSON.stringify({ memory_tier: "jhtm", jstm_sub: null, updated_at: new Date().toISOString() }),
    });
    logExchange("jmms.promote", `promoteSessionMemories: ${ids.length} JSTM→JHTM`);
  } catch (err) { console.error("promoteSessionMemories failed:", String(err).slice(0, 120)); }
}

/** Flag governance drift by comparing JCS decisions vs dex_events activity.
 * Fires after governance events. Reports HIGH/MEDIUM/CLEAN to the spine.
 */
export async function flagGovernanceDrift(): Promise<Json | null> {
  if (!AUTOINGEST) return null;
  try {
    const today = new Date().toISOString().slice(0, 10);
    const [eventsRows, slRows, jcsCount] = await Promise.all([
      fetch(`${SUPABASE_URL}/rest/v1/dex_events?created_at=gte.${today}T00:00:00Z&select=id`, {
        headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY }
      }).then(r => r.json()).catch(() => []),
      fetch(`${SUPABASE_URL}/rest/v1/sl_objects?stardate=like.${today.replace(/-/g, "")}*&select=id`, {
        headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY }
      }).then(r => r.json()).catch(() => []),
      countRows("jc_objects"),
    ]) as [any[], any[], number | null];
    const score = (eventsRows.length > 5 && jcsCount === 0) ? "HIGH" :
                 (eventsRows.length > 10 && (jcsCount ?? 0) < 3) ? "MEDIUM" : "CLEAN";
    if (score === "CLEAN") return null;
    const report = {
      drift: true, score,
      jcs_decisions: jcsCount,
      dex_events_today: eventsRows.length,
      sl_objects_today: slRows.length,
      flagged_at: new Date().toISOString(),
      message: score === "HIGH"
        ? "JCS has 0 decisions but high dex_events — governance may not be recording to JCS"
        : "JCS decisions lower than event activity suggests",
    };
    logExchange("governance.drift", JSON.stringify(report).slice(0, 400));
    return report;
  } catch (err) { console.error("flagGovernanceDrift failed:", String(err).slice(0, 120)); return null; }
}

/** Auto-fire SL_TICK from Supabase side after a governance event.
 * Writes a lightweight SL_TICK to sl_objects with current counts.
 * Idempotent — safe to call multiple times per session.
 */
export async function autoSLTick(): Promise<void> {
  if (!AUTOINGEST) return;
  try {
    const now = new Date();
    const ts = now.toISOString().slice(0, 19).replace(/[-:T]/g, "");
    const today = now.toISOString().slice(0, 10);
    const [eventsRows, slRows] = await Promise.all([
      fetch(`${SUPABASE_URL}/rest/v1/dex_events?created_at=gte.${today}T00:00:00Z&select=id`, {
        headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY }
      }).then(r => r.json()).catch(() => []),
      fetch(`${SUPABASE_URL}/rest/v1/sl_objects?stardate=like.${today.replace(/-/g, "")}*&select=id`, {
        headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY }
      }).then(r => r.json()).catch(() => []),
    ]) as [any[], any[]];
    const payload = {
      alias: `AUTO-TICK-${ts}`,
      log_type: "SL_TICK",
      stardate: today.replace(/-/g, "."),
      repo_url: "https://github.com/hurrisonferd/jarvis",
      events: [`auto-tick: ${eventsRows.length} events | ${slRows.length} SL rows today`],
      related: [],
      digest: `AUTO-TICK ${ts} | ${eventsRows.length} events | ${slRows.length} SL rows`,
      status: "TICK",
      decisions: [],
      participants: ["jarvis-c"],
      started_at: now.toISOString(),
      ended_at: now.toISOString(),
      task_summary: [],
    };
    const res = await fetch(`${SUPABASE_URL}/rest/v1/sl_objects`, {
      method: "POST",
      headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, "Content-Type": "application/json", Prefer: "resolution=mergepeks" },
      body: JSON.stringify(payload),
    });
    if (res.ok) logExchange("autonomy.tick", `autoSLTick: ${ts} — ${eventsRows.length} events today`);
  } catch (err) { console.error("autoSLTick failed:", String(err).slice(0, 120)); }
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
