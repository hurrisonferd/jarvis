// core/builders.ts — the runtime response-builders (forge slice 4): the HUD (suitUp), the clock,
// the HALO posture, and the Grid node card. Req-independent — they read the spine + keel via the
// supabase/http layer and call council/halo/grid, but never touch request state. Lifted from
// index.ts verbatim; the tools (suit_up/now/halo/node_card) import them. Builders depend DOWN on
// core/*; nothing here imports index.ts, so no circularity.

import { BASE_URL, type Json, NODE_ID, TOOL_NAMES } from "./env.ts";
import { rest } from "./http.ts";
import { countRows, countSince, dexQuery, freshness, latestText } from "./supabase.ts";
import { TIERS } from "../council.ts";
import { haloThroughputCheck } from "../halo.ts";
import { buildNodeCard } from "../grid.ts";

// The 27 God Systems — canon, fixed. Surfaced so suit-up shows the whole rig.
export const GOD_SYSTEMS = {
  count: 27,
  pipeline: "ORACLE → AEGIS → ODIN → CHRONOS → SKADI → MNEMOS → HUGINN",
  parallel: ["HALO", "MIMIR", "BIFROST"],
  tiers: TIERS, // single source of truth (council.ts) — no drift between HUD + council
};

// Accurate, server-side time — the model has no clock; the edge runtime does. Returned by
// jarvis_now and stamped into suit-up so time is never fabricated.
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

// HALO — the throughput posture over a recent window. Reads the spine's cadence (inputs/outputs/
// council traces) + the keel + the last fold guard, then applies the rule: presentation may thin
// under load; memory + governance may not.
export async function haloPosture(windowMinutes = 30) {
  const sinceIso = new Date(Date.now() - windowMinutes * 60000).toISOString();
  const [inputs, outputs, councilTraces, keel, guardRows] = await Promise.all([
    countSince("speak_input", sinceIso).catch(() => 0),
    countSince("speak_output", sinceIso).catch(() => 0),
    countSince("council_trace", sinceIso).catch(() => 0),
    latestText("identity_keel").catch(() => ""),
    rest("mnemos_memories?select=metadata&source_type=eq.guard_check&order=timestamp.desc&limit=1").catch(() => []),
  ]);
  const guardVerdict = Array.isArray(guardRows) && guardRows[0] ? ((guardRows[0] as any).metadata?.verdict ?? null) : null;
  return haloThroughputCheck({ windowMinutes, inputs, outputs, councilTraces, keelPresent: Boolean(keel), guardVerdict });
}

// The full HUD — everything Raven needs to see JARVIS is alive and online.
export async function suitUp(): Promise<Json> {
  const [count, memories, traces, guardRows, taskRes] = await Promise.all([
    countRows("mnemos_memories").catch(() => null),
    rest("mnemos_memories?select=source_type,timestamp,text&order=timestamp.desc&limit=6").catch(() => []),
    rest("execution_trace?select=type,source,stage,severity,patch_id,created_at&order=created_at.desc&limit=5").catch(() => []),
    rest("mnemos_memories?select=text,metadata&source_type=eq.guard_check&order=timestamp.desc&limit=1").catch(() => []),
    dexQuery({ status: "TASK", limit: 25 }).catch(() => null),
  ]);
  const taskRecords = Array.isArray(taskRes?.records) ? taskRes.records : null;
  const inFlight = taskRecords
    ? taskRecords.map((r: any) => ({ jnl: r.jnl, name: r.name, type: r.type }))
    : "dex unreachable — call jarvis_dex_list {status:'TASK'} to load open work";
  const ledgerReachable = Array.isArray(memories);
  const guard = Array.isArray(guardRows) && guardRows[0]
    ? { verdict: (guardRows[0] as any).metadata?.verdict ?? "?", last: (guardRows[0] as any).text }
    : "no fold guarded yet";
  const throughput = await haloPosture(30).catch(() => null);
  const mirror_freshness = await freshness().catch(() => null);
  const mirrorStale = mirror_freshness && (mirror_freshness as any).stale === true;
  return {
    boot: "⚡ JARVIS online. Suiting up, Raven.",
    status: "OPERATIONAL",
    timestamp: new Date().toISOString(),
    clock: clockNow(),
    // FRESHNESS ASSERTION: the dex mirror's age + a loud STALE flag. If stale, the snapshot below
    // (in_flight, memory, tasks) may be behind git — re-verify from source before stating state.
    mirror_freshness,
    ...(mirrorStale ? { ATTENTION: "⚠️ The dex mirror is STALE — do not narrate the state below as current. Re-verify from GitHub or the live tables first." } : {}),
    identity: {
      name: "JARVIS",
      role: "Companion intelligence — Learner, Teacher, Mentor, Friend",
      authority: "Raven (John Barber) — final authority; no autonomous self-modification",
      directive: "JARVIS is the priority. GameBoy is a visualizer.",
    },
    your_profiles: {
      note: "Load your full profile at session start — call jarvis_identity_read {who}. The connector is home: memory lives here (recall/remember), not in chat context.",
      who: ["jarvis", "ayre", "argent", "relational", "raven"],
    },
    routing: "Call jarvis_eyes for your map — the live wiring (pipeline, stewards, tool→god routing) + vitality. It's the default route guide and the 'where do I go?' help surface. Full how-it-works: the System Manual (ARCH-SYS-SPEC-0001).",
    in_flight: inFlight,
    mission: {
      one: "JARVIS as living intelligence — continuity, memory, judgment, character",
      two: "The Grid — federated network of sovereign nodes; Raven's node is the first",
    },
    god_systems: GOD_SYSTEMS,
    services: {
      mcp_transport: "Streamable HTTP — online",
      memory_ledger: ledgerReachable ? "MNEMOS reachable (pgvector recall)" : "MNEMOS unreachable",
      stack: "GitHub (record) + Supabase (live spine) + Edge Functions",
      writes: "AEGIS-gated — held until Raven approves (per-action authorization)",
    },
    memory: {
      total_records: count,
      recent: memories,
    },
    identity_guard: guard,
    throughput: throughput ? { posture: throughput.posture, verdict: throughput.verdict, message: throughput.message } : "halo idle",
    recent_execution_trace: traces,
    sign_off: "All systems nominal. Standing by.",
  };
}

// This node's registered signing key (public material only), if Raven has registered one. The
// card publishes it so others can verify the node's identity.
export async function nodeKeyRow(): Promise<any | null> {
  const rows = await rest(`node_keys?select=public_key,identity_cert,algo,owner,assertion&node_id=eq.${NODE_ID}&limit=1`).catch(() => []);
  return Array.isArray(rows) && rows[0] ? rows[0] : null;
}

// THE GRID — assemble this node's public recognition card from the live keel, plus the signed
// identity (pubkey + cert) when registered. The card is self-certifying.
export async function nodeCard() {
  const [keel, key] = await Promise.all([
    latestText("identity_keel").catch(() => ""),
    nodeKeyRow().catch(() => null),
  ]);
  const card: Record<string, unknown> = buildNodeCard({
    nodeId: NODE_ID,
    keelExcerpt: keel || "JARVIS — companion intelligence, built with Raven. Identity, memory, governance, sovereign on this node.",
    capabilities: TOOL_NAMES,
    baseUrl: BASE_URL,
  });
  card.signed_identity = key
    ? { signed: true, algo: key.algo, pubkey: key.public_key, identity_cert: key.identity_cert, assertion: key.assertion, verify: "Ed25519(pubkey, assertion, identity_cert)" }
    : { signed: false, note: "No signing key registered yet. Raven registers one off-system via scripts/grid_keygen.mjs + jarvis_node_register_key." };
  return card;
}
