// core/builders.ts — privacy-safe runtime builders.
// Public/status surfaces expose machine health and governance metadata, not private
// memory bodies, biographical identity, or identity-keel contents.

import { BASE_URL, type Json, NODE_ID, TOOL_NAMES } from "./env.ts";
import { rest } from "./http.ts";
import { countRows, countSince, dexQuery, freshness, latestText } from "./supabase.ts";
import { TIERS } from "../council.ts";
import { haloThroughputCheck } from "../halo.ts";
import { buildNodeCard } from "../grid.ts";

export const GOD_SYSTEMS = {
  count: 27,
  pipeline: "ORACLE → AEGIS → ODIN → CHRONOS → SKADI → MNEMOS → HUGINN",
  parallel: ["HALO", "MIMIR", "BIFROST"],
  tiers: TIERS,
};

export function clockNow(): Json {
  const d = new Date();
  const et = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York", dateStyle: "full", timeStyle: "long",
  }).format(d);
  return {
    utc: d.toISOString(),
    et,
    weekday: new Intl.DateTimeFormat("en-US", { weekday: "long", timeZone: "America/New_York" }).format(d),
    unix: Math.floor(d.getTime() / 1000),
  };
}

// HALO may inspect private state internally, but returns only aggregate posture.
export async function haloPosture(windowMinutes = 30) {
  const sinceIso = new Date(Date.now() - windowMinutes * 60000).toISOString();
  const [inputs, outputs, councilTraces, keel, guardRows] = await Promise.all([
    countSince("speak_input", sinceIso).catch(() => 0),
    countSince("speak_output", sinceIso).catch(() => 0),
    countSince("council_trace", sinceIso).catch(() => 0),
    latestText("identity_keel").catch(() => ""),
    rest("mnemos_memories?select=metadata&source_type=eq.guard_check&order=timestamp.desc&limit=1").catch(() => []),
  ]);
  const guardVerdict = Array.isArray(guardRows) && guardRows[0]
    ? ((guardRows[0] as any).metadata?.verdict ?? null)
    : null;
  return haloThroughputCheck({ windowMinutes, inputs, outputs, councilTraces, keelPresent: Boolean(keel), guardVerdict });
}

export async function suitUp(): Promise<Json> {
  const [count, traces, guardRows, taskRes] = await Promise.all([
    countRows("mnemos_memories").catch(() => null),
    rest("execution_trace?select=type,source,stage,severity,patch_id,created_at&order=created_at.desc&limit=5").catch(() => []),
    rest("mnemos_memories?select=metadata&source_type=eq.guard_check&order=timestamp.desc&limit=1").catch(() => []),
    dexQuery({ status: "TASK", limit: 25 }).catch(() => null),
  ]);

  const taskRecords = Array.isArray(taskRes?.records) ? taskRes.records : null;
  const inFlight = taskRecords
    ? taskRecords.map((r: any) => ({ jnl: r.jnl, name: r.name, type: r.type }))
    : "dex unavailable or private read credential not configured";
  const guard = Array.isArray(guardRows) && guardRows[0]
    ? { verdict: (guardRows[0] as any).metadata?.verdict ?? "?" }
    : { verdict: "unknown" };
  const throughput = await haloPosture(30).catch(() => null);
  const mirror_freshness = await freshness().catch(() => null);
  const mirrorStale = mirror_freshness && (mirror_freshness as any).stale === true;

  return {
    boot: "⚡ JARVIS online.",
    status: "OPERATIONAL",
    timestamp: new Date().toISOString(),
    clock: clockNow(),
    mirror_freshness,
    ...(mirrorStale ? { ATTENTION: "Mirror is stale. Re-verify from source before stating current system state." } : {}),
    identity: {
      name: "JARVIS",
      role: "Grid companion intelligence",
      authority: "Raven — final authority; no autonomous self-modification",
    },
    privacy: {
      mode: "BLACKWALL_NO_HARVEST",
      recent_memory_content_projected: false,
      identity_keel_projected: false,
      biographical_owner_data_projected: false,
    },
    in_flight: inFlight,
    god_systems: GOD_SYSTEMS,
    services: {
      mcp_transport: "Streamable HTTP",
      memory_ledger: count === null ? "unreachable" : "reachable",
      stack: "GitHub + Supabase + Edge Functions",
      writes: "governed effect paths only",
    },
    memory: {
      total_records: count,
      recent: "[PRIVATE_CONTENT_NOT_PROJECTED]",
    },
    identity_guard: guard,
    throughput: throughput
      ? { posture: throughput.posture, verdict: throughput.verdict, message: throughput.message }
      : "halo unavailable",
    recent_execution_trace: traces,
  };
}

// Public signing material only. Owner/assertion fields may encode personal identity
// and are intentionally not projected on the public recognition path.
export async function nodeKeyRow(): Promise<any | null> {
  const rows = await rest(
    `node_keys?select=public_key,identity_cert,algo&node_id=eq.${NODE_ID}&limit=1`,
  ).catch(() => []);
  return Array.isArray(rows) && rows[0] ? rows[0] : null;
}

export async function nodeCard() {
  const key = await nodeKeyRow().catch(() => null);
  const card: Record<string, unknown> = buildNodeCard({
    nodeId: NODE_ID,
    keelExcerpt: "",
    capabilities: TOOL_NAMES,
    baseUrl: BASE_URL,
  });
  card.signed_identity = key
    ? {
        signed: true,
        algo: key.algo,
        pubkey: key.public_key,
        identity_cert: key.identity_cert,
        verify: "Ed25519 public identity certificate",
      }
    : { signed: false, note: "No public signing certificate registered." };
  return card;
}
