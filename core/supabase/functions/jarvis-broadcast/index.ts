// JARVIS Broadcast — live system status for the TV interface.
// Returns a lightweight JSON payload: clock, god systems, god status,
// recent events, HALO posture. Refreshes every ~5 seconds from the TV side.
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SB_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? Deno.env.get("SUPABASE_SERVICE_KEY") ?? "";

const TIERS: Record<string, string> = {
  ORACLE: "T0 Foundational", AEGIS: "T0 Foundational", ODIN: "T0 Foundational",
  CHRONOS: "T0 Foundational", SKADI: "T0 Foundational", MNEMOS: "T0 Foundational",
  HUGINN: "T0 Foundational", CHAOS: "T0 Foundational", HADES: "T0 Foundational",
  POSEIDON: "T0 Foundational", ZEUS: "T0 Foundational",
  HALO: "T3 Monitoring", MIMIR: "T3 Monitoring", BIFROST: "T3 Monitoring",
  ATHENA: "T5 Strategic", MERIDIAN: "T5 Strategic", NEMESIS: "T5 Strategic",
  PROMETHEUS: "T5 Strategic", LOKI: "T5 Strategic", IRIS: "T5 Strategic",
  ARGUS: "T5 Strategic", APOLLO: "T5 Strategic", DANTE: "T5 Strategic",
  JANUS: "T5 Strategic", HERMES: "T5 Strategic",
  ATLAS: "T8 Infrastructure",
};

const LIVE_INDICATORS: Record<string, "ONLINE" | "STANDBY" | "DORMANT"> = {
  ORACLE: "ONLINE", AEGIS: "ONLINE", ODIN: "ONLINE", CHRONOS: "ONLINE",
  SKADI: "ONLINE", MNEMOS: "ONLINE", HUGINN: "ONLINE",
  HALO: "ONLINE", MIMIR: "ONLINE", BIFROST: "ONLINE",
  CHAOS: "STANDBY", HADES: "STANDBY", POSEIDON: "STANDBY", ZEUS: "STANDBY",
  ATHENA: "ONLINE", MERIDIAN: "ONLINE", PROMETHEUS: "ONLINE", NEMESIS: "ONLINE",
  ARGUS: "ONLINE", IRIS: "ONLINE", APOLLO: "ONLINE", DANTE: "ONLINE",
  ATLAS: "ONLINE", HERMES: "ONLINE", LOKI: "ONLINE", JANUS: "ONLINE",
};

async function rest(path: string) {
  const r = await fetch(`${SB_URL}/rest/v1/${path}`, {
    headers: { Authorization: `Bearer ${SB_KEY}`, apikey: SB_KEY, Prefer: "return=representation" },
  });
  if (!r.ok) return null;
  return r.json();
}

async function countRows(table: string) {
  const r = await fetch(`${SB_URL}/rest/v1/${table}?select=*`, {
    headers: { Authorization: `Bearer ${SB_KEY}`, apikey: SB_KEY, Prefer: "count=exact" },
  });
  if (!r.ok) return null;
  const cnt = r.headers.get("content-range")?.split("/").pop();
  return cnt ? parseInt(cnt) : null;
}

async function countSince(table: string, since: string) {
  const r = await fetch(
    `${SB_URL}/rest/v1/${table}?timestamp=gt.${since}&select=id`,
    {
      headers: { Authorization: `Bearer ${SB_KEY}`, apikey: SB_KEY, Prefer: "count=exact" },
    }
  );
  if (!r.ok) return null;
  const cnt = r.headers.get("content-range")?.split("/").pop();
  return cnt ? parseInt(cnt) : null;
}

async function fetchEvents(limit = 12) {
  try {
    const events = await rest(
      `mnemos_memories?select=source_type,timestamp,text&order=timestamp.desc&limit=${limit}`
    );
    if (!Array.isArray(events)) return [];
    return events.slice(0, limit).reverse().map((e: any) => ({
      type: e.source_type,
      time: new Date(e.timestamp).toISOString(),
      text: String(e.text ?? "").slice(0, 120),
    }));
  } catch {
    return [];
  }
}

async function recentTraces(limit = 8) {
  try {
    const rows = await rest(
      `execution_trace?select=type,source,stage,created_at&order=created_at.desc&limit=${limit}`
    );
    if (!Array.isArray(rows)) return [];
    return rows.slice(0, limit).reverse().map((r: any) => ({
      type: r.type,
      source: r.source,
      stage: r.stage,
      time: new Date(r.created_at).toISOString(),
    }));
  } catch {
    return [];
  }
}

async function recentKeel() {
  try {
    const rows = await rest(
      "mnemos_memories?source_type=eq.identity_keel&select=text&order=timestamp.desc&limit=1"
    );
    if (Array.isArray(rows) && rows[0]) return String(rows[0].text).slice(0, 200);
    return null;
  } catch {
    return null;
  }
}

async function haloPosture(windowMinutes = 30) {
  const since = new Date(Date.now() - windowMinutes * 60000).toISOString();
  const [inputs, outputs, traces, guardRows] = await Promise.all([
    countSince("speak_input", since),
    countSince("speak_output", since),
    countSince("council_trace", since),
    rest("mnemos_memories?source_type=eq.guard_check&select=metadata&order=timestamp.desc&limit=1"),
  ]);
  const guardVerdict =
    Array.isArray(guardRows) && guardRows[0]
      ? (guardRows[0] as any).metadata?.verdict ?? null
      : null;
  const inputsOk = (inputs ?? 0) > 0;
  const outputsOk = (outputs ?? 0) > 0;
  let posture = "NOMINAL";
  if (!inputsOk && !outputsOk) posture = "QUIET";
  else if (inputsOk !== outputsOk) posture = "SKEWED";
  return { inputs: inputs ?? 0, outputs: outputs ?? 0, councilTraces: traces ?? 0, posture, verdict: guardVerdict };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }

  const [events, traces, memCount, jdCnt, dexEvents, keel, halo] =
    await Promise.all([
      fetchEvents(12),
      recentTraces(8),
      countRows("mnemos_memories"),
      countRows("jd_entries"),
      (async () => {
        const since = new Date(Date.now() - 60 * 60000).toISOString();
        return countSince("speak_input", since);
      })(),
      recentKeel(),
      haloPosture(30).catch(() => null),
    ]);

  const godStatus = Object.entries(LIVE_INDICATORS).map(([name, status]) => ({
    name,
    status,
    tier: TIERS[name] ?? "T?",
  }));

  const now = new Date();
  const et = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York", dateStyle: "full", timeStyle: "long",
  }).format(now);

  const data = {
    clock: {
      utc: now.toISOString(),
      et,
      unix: Math.floor(now.getTime() / 1000),
    },
    system: {
      name: "JARVIS",
      version: "0.2.0",
      status: "OPERATIONAL",
      uptime: "edge-runtime",
    },
    gods: godStatus,
    halo: halo,
    counts: {
      memories: memCount ?? 0,
      jd_entries: jdCnt ?? 0,
      dex_events_1h: dexEvents ?? 0,
    },
    keel: keel,
    events,
    traces,
  };

  return new Response(JSON.stringify(data, null, 2), {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-store",
    },
  });
});
