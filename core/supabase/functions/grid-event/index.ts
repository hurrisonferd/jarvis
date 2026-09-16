import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SUPABASE_SERVICE_KEY =
  Deno.env.get("SUPABASE_SERVICE_KEY") ??
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ??
  "";
const NODE_ID = Deno.env.get("JARVIS_NODE_ID") ?? "node-001-raven";
const ALLOWED_ORIGIN = (Deno.env.get("GRID_EVENT_ALLOWED_ORIGIN") ?? "").trim();
const MAX_BODY_BYTES = 16_384;
const MAX_INTENT_CHARS = 240;
const MAX_PATCH_ID_CHARS = 160;
const MAX_PAYLOAD_JSON_CHARS = 8_000;

// BLACKWALL law:
// - reachability != authority
// - claimed source != caller identity
// - telemetry != permission to harvest arbitrary payloads
// - UNKNOWN / persistence failure must fail closed
const ALLOWED_TYPES = new Set([
  "speak", "store", "propose", "execute", "observe",
  "query", "heartbeat", "recall", "commit", "deploy",
  "promote_node",
]);

const ALLOWED_SOURCE_LABELS = new Set([
  "jarvis", "raven", "codex", "gpt", "gemini",
]);

const SENSITIVE_KEY = /(token|secret|password|credential|authorization|cookie|api[_-]?key|private[_-]?key|session[_-]?key)/i;
const PRIVATE_CONTENT_KEY = /(message|body|text|prompt|content|transcript|memory|biograph|location|email|phone)/i;

const WORLD_MAX_DEPTH = 5;
const WORLD_MAX_CHILD = 8;

function json(status: number, body: Record<string, unknown>, extra: HeadersInit = {}): Response {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
  };
  if (ALLOWED_ORIGIN) headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN;
  Object.assign(headers, extra);
  return new Response(JSON.stringify(body), { status, headers });
}

function safeEqual(a: string, b: string): boolean {
  if (!a || !b || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function bearer(req: Request): string {
  const raw = req.headers.get("authorization") ?? "";
  if (!raw.toLowerCase().startsWith("bearer ")) return "";
  return raw.slice(7).trim();
}

function internalAuthorized(req: Request): boolean {
  if (!SUPABASE_SERVICE_KEY) return false;
  return safeEqual(bearer(req), SUPABASE_SERVICE_KEY);
}

function aegisValidateWorld(payload: unknown): string | null {
  const p = (payload ?? {}) as Record<string, unknown>;
  const ws = p.world_schema as Record<string, unknown> | undefined;
  if (!ws) return "P30:missing_world_schema";
  const bounds = ws.bounds as Record<string, number> | undefined;
  if (!bounds) return "P30:missing_bounds";
  const depth = Number(bounds.max_depth ?? 0);
  if (!Number.isFinite(depth) || depth < 1) return "P30:depth_must_be_positive";
  if (depth > WORLD_MAX_DEPTH) return `P30:depth_exceeds_${WORLD_MAX_DEPTH}`;
  const child = Number(bounds.max_child_worlds ?? 0);
  if (!Number.isFinite(child) || child < 0) return "P30:child_worlds_invalid";
  if (child > WORLD_MAX_CHILD) return `P30:child_worlds_exceeds_${WORLD_MAX_CHILD}`;
  const signOff = (ws.raven_sign_off ?? p.raven_sign_off) === true;
  if (!signOff) return "P30:raven_sign_off_required";
  return null;
}

const FORBIDDEN_EDGES = new Set([
  "skadi:aegis", "dante:skadi", "janus:skadi", "loki:hades",
]);

function validateEvent(type: string, source: string, payload: unknown): string | null {
  const t = type.toLowerCase();
  const s = source.toLowerCase();
  if (!ALLOWED_TYPES.has(t)) return "UNKNOWN_EVENT_TYPE";
  if (!ALLOWED_SOURCE_LABELS.has(s)) return "UNKNOWN_SOURCE_LABEL";
  if (FORBIDDEN_EDGES.has(`${s}:${t}`)) return "FORBIDDEN_EDGE";
  if (t === "promote_node") return aegisValidateWorld(payload);
  return null;
}

function minimizeValue(value: unknown, key = "", depth = 0): unknown {
  if (depth > 4) return "[DEPTH_LIMIT]";
  if (SENSITIVE_KEY.test(key)) return "[REDACTED_SECRET]";
  if (PRIVATE_CONTENT_KEY.test(key)) {
    if (typeof value === "string") return { redacted: true, chars: value.length };
    return "[REDACTED_PRIVATE_CONTENT]";
  }
  if (value === null || typeof value === "boolean" || typeof value === "number") return value;
  if (typeof value === "string") return value.slice(0, 240);
  if (Array.isArray(value)) return value.slice(0, 20).map((v) => minimizeValue(v, key, depth + 1));
  if (typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>).slice(0, 40)) {
      out[k.slice(0, 80)] = minimizeValue(v, k, depth + 1);
    }
    return out;
  }
  return String(value).slice(0, 120);
}

function minimizedPayload(payload: unknown): unknown {
  const minimized = minimizeValue(payload);
  const encoded = JSON.stringify(minimized);
  if (encoded.length <= MAX_PAYLOAD_JSON_CHARS) return minimized;
  return {
    redacted: true,
    reason: "PAYLOAD_SUMMARY_TOO_LARGE",
    original_type: Array.isArray(payload) ? "array" : typeof payload,
  };
}

Deno.serve(async (req) => {
  const cors: Record<string, string> = {
    "Access-Control-Allow-Headers": "authorization, content-type",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  };
  if (ALLOWED_ORIGIN) cors["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN;

  if (req.method === "OPTIONS") {
    if (!ALLOWED_ORIGIN) return new Response(null, { status: 204 });
    return new Response(null, { status: 204, headers: cors });
  }

  if (!internalAuthorized(req)) {
    return json(401, { ok: false, error: "UNAUTHORIZED" }, cors);
  }

  if (req.method === "GET") {
    const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
    const url = new URL(req.url);
    const requested = Number(url.searchParams.get("limit") ?? "10");
    const limit = Number.isFinite(requested) ? Math.max(1, Math.min(50, Math.trunc(requested))) : 10;
    const { data, error } = await sb
      .from("execution_trace")
      .select("id, type, source, intent, stage, severity, created_at, patch_id")
      .order("created_at", { ascending: false })
      .limit(limit);
    if (error) return json(502, { ok: false, error: "TRACE_READ_FAILED" }, cors);
    return json(200, { ok: true, traces: data ?? [] }, cors);
  }

  if (req.method !== "POST") {
    return json(405, { ok: false, error: "METHOD_NOT_ALLOWED" }, cors);
  }

  const contentLength = Number(req.headers.get("content-length") ?? "0");
  if (Number.isFinite(contentLength) && contentLength > MAX_BODY_BYTES) {
    return json(413, { ok: false, error: "BODY_TOO_LARGE" }, cors);
  }

  try {
    const body = await req.json();
    const type = typeof body?.type === "string" ? body.type.trim().toLowerCase() : "";
    const source = typeof body?.source === "string" ? body.source.trim().toLowerCase() : "";
    const intent = typeof body?.intent === "string" ? body.intent.trim().slice(0, MAX_INTENT_CHARS) : "";
    const patchId = typeof body?.patch_id === "string" ? body.patch_id.trim().slice(0, MAX_PATCH_ID_CHARS) : null;
    const payload = body?.payload ?? {};

    if (!type || !source) {
      return json(400, { ok: false, error: "TYPE_AND_SOURCE_REQUIRED" }, cors);
    }

    const reason = validateEvent(type, source, payload);
    const allowed = reason === null;
    const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
    const tracePayload = {
      node_id: NODE_ID,
      claimed_source: source,
      source_is_attribution_only: true,
      caller_authority: "internal_service_credential",
      event_payload: minimizedPayload(payload),
      aegis_allowed: allowed,
      ...(reason ? { aegis_reason: reason } : {}),
    };

    const { data: trace, error: traceErr } = await sb
      .from("execution_trace")
      .insert({
        type,
        source,
        intent,
        stage: allowed ? "allowed" : "rejected",
        severity: allowed ? "info" : "warn",
        patch_id: patchId,
        payload: tracePayload,
      })
      .select("id, created_at")
      .single();

    if (traceErr || !trace?.id) {
      console.error("grid-event trace persistence failed");
      return json(502, { ok: false, error: "TRACE_PERSISTENCE_FAILED" }, cors);
    }

    return json(
      allowed ? 200 : 403,
      {
        ok: allowed,
        status: allowed ? "allowed" : "rejected",
        trace_id: trace.id,
        source,
        source_authority: "attribution_only",
        caller_authority: "internal_service_credential",
        type,
        node_id: NODE_ID,
        timestamp: trace.created_at,
        ...(reason ? { reason } : {}),
      },
      cors,
    );
  } catch {
    return json(400, { ok: false, error: "INVALID_REQUEST" }, cors);
  }
});
