import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { authorized, handleRpc, PROTOCOL_VERSION, SERVER_INFO, TOOLS, type McpEnv, type RpcMessage } from "./mcp.ts";
import { authServerMetadata, protectedResourceMetadata, registerClient } from "./oauth.ts";

// MCP server — JARVIS as a remote MCP endpoint. Streamable-HTTP transport:
// clients POST JSON-RPC; we answer with JSON. One URL, every client, one mind.
//
// Deploy with verify_jwt = false so the Authorization header belongs to MCP
// (the MCP_TOKEN bearer), not the Supabase gateway. Auth is enforced in-code.

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type, mcp-protocol-version, mcp-session-id",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
};
const JSON_H = { "Content-Type": "application/json", ...CORS };

// The legacy anon JWT — public by design (anon role, RLS-bound), and a real
// JWT so it satisfies both verify_jwt gateways (jarvis-respond) and the open
// ones. Env override (MCP_PROXY_KEY) lets Raven rotate without a redeploy.
const PROXY_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9leGdoZnN2aG5nZ2RkbGxndnJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2MzQwOTgsImV4cCI6MjA5NTIxMDA5OH0.jRFMf-C9ps72Bi_9IpiC3eOZD6Aj6wU4IF-j3svKTfQ";

function env(): McpEnv {
  return {
    baseUrl: Deno.env.get("SUPABASE_URL") ?? "",
    // Sibling functions verify_jwt at their gateway; proxy with the same
    // publishable key the browser uses. They use service-role internally for DB.
    authKey: Deno.env.get("MCP_PROXY_KEY") ?? PROXY_KEY,
    token: Deno.env.get("MCP_TOKEN") ?? "",
  };
}

// Where this function lives — the OAuth issuer + resource identifier. Sub-paths
// (/.well-known/*, /register, /authorize, /token) all route to this one function.
const ISSUER = `${Deno.env.get("SUPABASE_URL") ?? ""}/functions/v1/mcp`;

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });

  const e = env();
  // Strip everything up to and including the function name. The runtime may or
  // may not include the /functions/v1 prefix, so anchor on the first "/mcp".
  const sub = new URL(req.url).pathname.replace(/^.*?\/mcp/, "");

  // --- OAuth bridge (Stage 1: discovery + registration; identity gate pending
  // the Google provider). These are additive — the MCP transport below is
  // unchanged, so existing connectors keep working until we flip the challenge on.
  if (req.method === "GET" && sub === "/.well-known/oauth-protected-resource") {
    return new Response(JSON.stringify(protectedResourceMetadata(ISSUER, ISSUER)), { headers: JSON_H });
  }
  if (req.method === "GET" && sub === "/.well-known/oauth-authorization-server") {
    return new Response(JSON.stringify(authServerMetadata(ISSUER)), { headers: JSON_H });
  }
  if (req.method === "POST" && sub === "/register") {
    let regBody: unknown = {};
    try { regBody = await req.json(); } catch { /* empty body → validation fails below */ }
    const reg = registerClient(regBody);
    if (!reg.ok) return new Response(JSON.stringify({ error: "invalid_client_metadata", error_description: reg.error }), { status: 400, headers: JSON_H });
    return new Response(JSON.stringify(reg.client), { status: 201, headers: JSON_H });
  }
  // The Google round-trip lands in Stage 2, once Raven enables the provider.
  // Honest placeholder until then — never a silent 404 mid-flow.
  if ((req.method === "GET" && sub === "/authorize") || (req.method === "POST" && sub === "/token")) {
    return new Response(JSON.stringify({ error: "oauth_setup_pending", error_description: "Google provider not yet enabled. Identity login coming in Stage 2." }), { status: 503, headers: JSON_H });
  }

  // GET — a friendly discovery/health response (some clients probe before POST).
  if (req.method === "GET") {
    return new Response(
      JSON.stringify({
        server: SERVER_INFO,
        protocolVersion: PROTOCOL_VERSION,
        transport: "streamable-http",
        tools: TOOLS.map((t) => t.name),
        note: "POST JSON-RPC 2.0 to this URL. MCP endpoint for JARVIS.",
      }),
      { headers: JSON_H },
    );
  }

  if (req.method !== "POST") return new Response("method not allowed", { status: 405, headers: CORS });

  // Auth (in-code; verify_jwt disabled). 401 with WWW-Authenticate per MCP.
  if (!authorized(req.headers.get("authorization"), e.token)) {
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401,
      headers: { ...JSON_H, "WWW-Authenticate": 'Bearer realm="jarvis-mcp"' },
    });
  }

  let body: unknown;
  try { body = await req.json(); }
  catch { return new Response(JSON.stringify({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "parse error" } }), { status: 400, headers: JSON_H }); }

  // MCP allows a single message or a batch. Notifications (no id) yield no reply.
  const messages: RpcMessage[] = Array.isArray(body) ? body as RpcMessage[] : [body as RpcMessage];
  const responses = [];
  for (const m of messages) {
    const res = await handleRpc(m, e);
    if (res) responses.push(res);
  }

  // All notifications → 202 with no body (nothing to answer).
  if (responses.length === 0) return new Response(null, { status: 202, headers: CORS });

  const payload = Array.isArray(body) ? responses : responses[0];
  return new Response(JSON.stringify(payload), { headers: JSON_H });
});
