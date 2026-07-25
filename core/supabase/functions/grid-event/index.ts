import "jsr:@core/supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@core/supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_KEY") ?? "";

// GNPL trust registry
const TRUST_SCORES: Record<string, number> = {
  jarvis: 1.0,
  raven:  1.0,
  codex:  0.85,
  gpt:    0.80,
  gemini: 0.70,
};

const ALLOWED_TYPES = new Set([
  "speak", "store", "propose", "execute", "observe",
  "query", "heartbeat", "recall", "commit", "deploy",
  "promote_node",
]);

// P30/P32 world bounds — fractal tree caps enforced at the gate.
const WORLD_MAX_DEPTH = 5;
const WORLD_MAX_CHILD = 8;

// P30: validate a NODE→WORLD promotion. Mirrors the browser AEGIS.promote_node rule
// and additionally enforces the P32 fractal bounds (depth <= 5, child_worlds <= 8).
function aegisValidateWorld(payload: unknown): string | null {
  const p = (payload ?? {}) as Record<string, unknown>;
  const ws = p.world_schema as Record<string, unknown> | undefined;
  if (!ws)         return "P30:missing_world_schema";
  const bounds = ws.bounds as Record<string, number> | undefined;
  if (!bounds)     return "P30:missing_bounds";
  const depth = Number(bounds.max_depth ?? 0);
  if (depth < 1)            return "P30:depth_must_be_positive";
  if (depth > WORLD_MAX_DEPTH) return `P30:depth_exceeds_${WORLD_MAX_DEPTH}`;
  const child = Number(bounds.max_child_worlds ?? 0);
  if (child > WORLD_MAX_CHILD) return `P30:child_worlds_exceeds_${WORLD_MAX_CHILD}`;
  const signOff = (ws.raven_sign_off ?? p.raven_sign_off) === true;
  if (!signOff)    return "P30:raven_sign_off_required";
  return null;
}

// Forbidden edge patterns (source:type)
const FORBIDDEN_EDGES = new Set([
  "skadi:aegis", "dante:skadi", "janus:skadi", "loki:hades",
]);

interface AegisResult {
  allowed: boolean;
  trust: number;
  reason?: string;
}

function aegisValidate(type: string, source: string): AegisResult {
  const t = type.toLowerCase();
  const s = source.toLowerCase();

  if (!ALLOWED_TYPES.has(t)) {
    return { allowed: false, trust: 0, reason: `Unknown event type: ${t}` };
  }

  const trust = TRUST_SCORES[s];
  if (trust === undefined) {
    return { allowed: false, trust: 0, reason: `Untrusted source: ${s}` };
  }

  if (FORBIDDEN_EDGES.has(`${s}:${t}`)) {
    return { allowed: false, trust, reason: `Forbidden edge: ${s}→${t}` };
  }

  return { allowed: true, trust };
}

Deno.serve(async (req) => {
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, content-type",
  };

  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });

  // GET — list recent execution trace
  if (req.method === "GET") {
    const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
    const url = new URL(req.url);
    const limit = parseInt(url.searchParams.get("limit") ?? "10");
    const { data } = await sb
      .from("execution_trace")
      .select("id, type, source, intent, stage, severity, created_at, patch_id")
      .order("created_at", { ascending: false })
      .limit(limit);
    return new Response(JSON.stringify({ traces: data ?? [] }), {
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  // POST — submit event through AEGIS gate
  try {
    const body = await req.json();
    const { type, source, intent, payload, node_id, patch_id } = body;

    if (!type || !source) {
      return new Response(
        JSON.stringify({ error: "type and source are required" }),
        { status: 400, headers: { ...cors, "Content-Type": "application/json" } },
      );
    }

    const aegis = aegisValidate(type, source);

    // P30: promote_node carries a world schema — gate it before any world is created.
    if (aegis.allowed && type.toLowerCase() === "promote_node") {
      const worldReason = aegisValidateWorld(payload);
      if (worldReason) {
        aegis.allowed = false;
        aegis.reason = worldReason;
      }
    }

    const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

    const { data: trace, error: traceErr } = await sb
      .from("execution_trace")
      .insert({
        type,
        source,
        intent: intent ?? "",
        stage: aegis.allowed ? "allowed" : "rejected",
        severity: aegis.allowed ? "info" : "warn",
        patch_id: patch_id ?? null,
        payload: {
          ...(typeof payload === "object" && payload !== null ? payload : { raw: payload }),
          node_id: node_id ?? "node-001-raven",
          aegis_trust: aegis.trust,
          aegis_allowed: aegis.allowed,
          ...(aegis.reason ? { aegis_reason: aegis.reason } : {}),
        },
      })
      .select("id, created_at")
      .single();

    if (traceErr) console.error("trace insert failed:", traceErr.message);

    return new Response(
      JSON.stringify({
        status:    aegis.allowed ? "allowed" : "rejected",
        trace_id:  trace?.id ?? null,
        trust:     aegis.trust,
        source,
        type,
        node_id:   node_id ?? "node-001-raven",
        timestamp: trace?.created_at ?? new Date().toISOString(),
        ...(aegis.reason ? { reason: aegis.reason } : {}),
      }),
      {
        status:  aegis.allowed ? 200 : 403,
        headers: { ...cors, "Content-Type": "application/json" },
      },
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ error: String(err) }),
      { status: 500, headers: { ...cors, "Content-Type": "application/json" } },
    );
  }
});
