import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { buildRequest, endpoint, parseGrounded, reachSummary } from "./bifrost.ts";

// BIFROST — JARVIS reaches the world. Live, grounded web knowledge via Gemini's
// Google Search tool, on the key we already have. Read-only reach: it fetches and
// synthesizes, it never writes to the world. The companion curates what to keep.
const BASE  = Deno.env.get("BIFROST_BASE")  || "https://generativelanguage.googleapis.com";
const MODEL = Deno.env.get("BIFROST_MODEL") || "gemini-2.0-flash";
const KEY   = Deno.env.get("BIFROST_KEY") || Deno.env.get("LLM_API_KEY") || Deno.env.get("GEMINI_API_KEY") || "";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
  if (req.method !== "POST") return new Response("method not allowed", { status: 405, headers: CORS });

  const jsonH = { "Content-Type": "application/json", ...CORS };
  if (!KEY) return new Response(JSON.stringify({ error: "no_api_key" }), { status: 500, headers: jsonH });

  let body: Record<string, unknown> = {};
  try { body = await req.json(); } catch { return new Response("bad request", { status: 400, headers: jsonH }); }
  const query = (body.query as string ?? "").trim();
  if (!query) return new Response(JSON.stringify({ error: "query required" }), { status: 400, headers: jsonH });

  try {
    const r = await fetch(endpoint(BASE, MODEL), {
      method: "POST",
      headers: { "x-goog-api-key": KEY, "Content-Type": "application/json" },
      body: JSON.stringify(buildRequest(query)),
    });
    if (!r.ok) {
      const detail = (await r.text().catch(() => "")).slice(0, 300);
      return new Response(JSON.stringify({ error: `bifrost_${r.status}: ${detail}` }), { status: 502, headers: jsonH });
    }
    const reach = parseGrounded(await r.json());
    return new Response(
      JSON.stringify({ query, answer: reach.answer, sources: reach.sources, grounded: reach.grounded, summary: reachSummary(reach) }),
      { headers: jsonH },
    );
  } catch (e) {
    return new Response(JSON.stringify({ error: `bifrost_fetch_error: ${String(e).slice(0, 160)}` }), { status: 502, headers: jsonH });
  }
});
