import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

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
]);

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
