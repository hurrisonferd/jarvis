// core/supabase.ts — the Supabase data-access layer (forge slice 3).
// BLACKWALL: ambient conversation capture is OFF by default. Durable memory is
// an explicit effect, not a side-effect of speaking to the connector.

import { type Json, SERVICE_KEY, SUPABASE_URL } from "./env.ts";
import { rest } from "./http.ts";

// NO-HARVEST DEFAULT.
// Explicit durable memory still exists through governed MNEMOS tools. This switch
// only controls legacy ambient exchange/governance telemetry that writes to memory.
export const AUTOINGEST = (Deno.env.get("MCP_AUTOINGEST") ?? "false") === "true";

export async function logExchange(sourceType: string, content: string, sessionKey?: string): Promise<void> {
  if (!AUTOINGEST || !content.trim()) return;
  try {
    const tags = sessionKey
      ? ["exchange", "explicit_auto_ingest", "mcp_connector", `session:${sessionKey.slice(0, 12)}`]
      : ["exchange", "explicit_auto_ingest", "mcp_connector"];

    const res = await fetch(`${SUPABASE_URL}/rest/v1/mnemos_memories`, {
      method: "POST",
      headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, "content-type": "application/json", Prefer: "return=minimal" },
      body: JSON.stringify({
        id: crypto.randomUUID(),
        source_id: crypto.randomUUID(),
        source_type: sourceType,
        text: content.slice(0, 2000),
        tags,
        platform: "mcp_connector",
      }),
    });
    if (!res.ok) console.error(`logExchange(${sourceType}) persistence failed status=${res.status}`);
  } catch (err) {
    console.error(`logExchange(${sourceType}) failed:`, String(err).slice(0, 160));
  }
}

const GOVERNANCE_VERDICTS = [
  "gate", "aegis", "denied", "approved",
  "commit", "implementing", "deferred", "bench", "benched",
  "closed", "resolved", "flag",
];

export function detectGovernanceEvent(trace: string): boolean {
  if (!trace.includes("output_review")) return false;
  if (trace.includes("output_review=PASS")) return false;
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

// Compatibility export only. A publishable/anon credential is never identity.
// It must come from deployment configuration and is never baked into source.
export const ANON_JWT = (Deno.env.get("SUPABASE_ANON_KEY") ?? "").trim();

export async function callFunctionAs(name: string, body: Json, key: string): Promise<unknown> {
  if (!key) throw new Error(`${name}: caller credential unavailable`);
  const res = await fetch(`${SUPABASE_URL}/functions/v1/${name}`, {
    method: "POST",
    headers: { authorization: `Bearer ${key}`, apikey: key, "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`${name} ${res.status}: ${JSON.stringify(payload).slice(0, 200)}`);
  return payload;
}

export async function countRows(table: string): Promise<number | null> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?limit=1`, {
    headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, Prefer: "count=exact", Range: "0-0" },
  });
  if (!res.ok) throw new Error(`countRows ${table} ${res.status}`);
  const cr = res.headers.get("content-range");
  if (cr && cr.includes("/")) { const t = cr.split("/")[1]; return t === "*" ? null : Number(t); }
  return null;
}

// jarvis-dex no longer has an anonymous read tier. Use an explicitly scoped DEX
// credential or fail closed. Never silently fall back to reachability.
export async function dexQuery(args: Json): Promise<any> {
  const dexToken = (
    Deno.env.get("DEX_READ_TOKEN") ??
    Deno.env.get("DEX_AGENT_TOKEN") ??
    ""
  ).trim();
  if (!dexToken) return null;
  const res = await fetch(`${SUPABASE_URL}/functions/v1/jarvis-dex`, {
    method: "POST",
    headers: { "content-type": "application/json", "x-jarvis-token": dexToken },
    body: JSON.stringify({ tool: "jd_list", args }),
  });
  if (!res.ok) return null;
  return await res.json().catch(() => null);
}

export async function latestText(sourceType: string): Promise<string> {
  const rows = await rest(`mnemos_memories?select=text&source_type=eq.${sourceType}&order=timestamp.desc&limit=1`).catch(() => []);
  return Array.isArray(rows) && rows[0] ? String((rows[0] as any).text ?? "") : "";
}

// ── LEVEL 1 AUTONOMY ─────────────────────────────────────────────────────────
// These legacy observational routines are tied to AUTOINGEST. With the Blackwall
// default they are inert unless the operator explicitly opts into that telemetry.

export async function promoteSessionMemories(): Promise<void> {
  if (!AUTOINGEST) return;
  try {
    const cutoff = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
    const sessionRows = await rest(
      `mnemos_memories?select=id&memory_tier=eq.jstm&jstm_sub=eq.session&timestamp=lt.${cutoff}&order=timestamp.asc&limit=100`
    ) as any[];
    if (!sessionRows.length) return;
    const promote = sessionRows.slice(20);
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

export async function countSince(sourceType: string, sinceIso: string): Promise<number> {
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/mnemos_memories?select=id&source_type=eq.${sourceType}&timestamp=gte.${sinceIso}`,
    { headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, Prefer: "count=exact", Range: "0-0" } },
  );
  const cr = res.headers.get("content-range");
  if (cr && cr.includes("/")) { const t = cr.split("/")[1]; return t === "*" ? 0 : Number(t); }
  return 0;
}
