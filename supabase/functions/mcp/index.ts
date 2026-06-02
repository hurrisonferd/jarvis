import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { handleRpc, PROTOCOL_VERSION, SERVER_INFO, TOOLS, type McpEnv, type RpcMessage } from "./mcp.ts";
import {
  authServerMetadata,
  buildClientRedirect,
  DEFAULT_PROVIDER,
  isRaven,
  parseAuthorizeParams,
  protectedResourceMetadata,
  randomToken,
  registerClient,
  s256,
  supabaseAuthorizeUrl,
  TOKEN_TTL_SECONDS,
  verifyPkce,
} from "./oauth.ts";

// MCP server — JARVIS as a remote MCP endpoint. Streamable-HTTP transport:
// clients POST JSON-RPC; we answer with JSON. One URL, every client, one mind.
//
// Identity: an OAuth 2.1 bridge (authorize/callback/token) lets MCP clients log
// Raven in through Supabase Auth → his identity provider. The door opens as
// *Raven*, not as a shared secret. Deployed verify_jwt=false so MCP owns auth.

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type, mcp-protocol-version, mcp-session-id",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
};
const JSON_H = { "Content-Type": "application/json", ...CORS };

// The legacy anon JWT — public by design (anon role, RLS-bound), and a real JWT
// so it satisfies both verify_jwt gateways (jarvis-respond) and the GoTrue
// apikey header. Env override (MCP_PROXY_KEY) lets Raven rotate without redeploy.
const PROXY_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9leGdoZnN2aG5nZ2RkbGxndnJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2MzQwOTgsImV4cCI6MjA5NTIxMDA5OH0.jRFMf-C9ps72Bi_9IpiC3eOZD6Aj6wU4IF-j3svKTfQ";

const SB_URL       = Deno.env.get("SUPABASE_URL") ?? "";
const SB_SVC       = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const RAVEN_EMAIL  = Deno.env.get("RAVEN_EMAIL") ?? "johnbarber720@gmail.com";
const PROVIDER     = Deno.env.get("MCP_AUTH_PROVIDER") ?? DEFAULT_PROVIDER;
// Flip identity enforcement on once the provider round-trip is verified. Until
// then the transport stays open (no regression) but still honors OAuth tokens.
const REQUIRE_AUTH = (Deno.env.get("MCP_REQUIRE_AUTH") ?? "false") === "true";

function proxyEnv(): McpEnv {
  return {
    baseUrl: SB_URL,
    authKey: Deno.env.get("MCP_PROXY_KEY") ?? PROXY_KEY,
    token: Deno.env.get("MCP_TOKEN") ?? "",
  };
}

// Where this function lives — the OAuth issuer + resource identifier. Sub-paths
// (/.well-known/*, /register, /authorize, /callback, /token) route to this fn.
const ISSUER = `${SB_URL}/functions/v1/mcp`;

// Service-role client for the OAuth state tables (RLS-protected; service bypasses).
const admin = () => createClient(SB_URL, SB_SVC);

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: JSON_H });
const redirect = (location: string) => new Response(null, { status: 302, headers: { Location: location, ...CORS } });

// Parse a token-endpoint body — OAuth is form-encoded, but accept JSON too.
async function readBody(req: Request): Promise<Record<string, string>> {
  const ct = req.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) { try { return await req.json(); } catch { return {}; } }
  const params = new URLSearchParams(await req.text());
  return Object.fromEntries(params);
}

// Resolve the verified identity behind a bearer, or null. Accepts an issued
// OAuth access token (looked up + expiry-checked) or the static MCP_TOKEN escape.
async function bearerIdentity(header: string | null, staticToken: string): Promise<string | null> {
  const tok = (header ?? "").replace(/^Bearer\s+/i, "").trim();
  if (!tok) return null;
  if (staticToken && tok === staticToken) return RAVEN_EMAIL; // admin escape hatch
  const { data } = await admin().from("mcp_oauth_tokens").select("email, expires_at").eq("token", tok).maybeSingle();
  if (!data) return null;
  if (new Date(data.expires_at as string).getTime() < Date.now()) return null;
  return data.email as string;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });

  const e = proxyEnv();
  // Strip everything up to and including the function name. The runtime may or
  // may not include the /functions/v1 prefix, so anchor on the first "/mcp".
  const sub = new URL(req.url).pathname.replace(/^.*?\/mcp/, "");

  // ---- OAuth discovery (RFC 9728 / RFC 8414) ----
  if (req.method === "GET" && sub === "/.well-known/oauth-protected-resource") {
    return json(protectedResourceMetadata(ISSUER, ISSUER));
  }
  if (req.method === "GET" && sub === "/.well-known/oauth-authorization-server") {
    return json(authServerMetadata(ISSUER));
  }

  // ---- Dynamic Client Registration (RFC 7591) ----
  if (req.method === "POST" && sub === "/register") {
    let regBody: unknown = {};
    try { regBody = await req.json(); } catch { /* empty → validation fails */ }
    const reg = registerClient(regBody);
    if (!reg.ok) return json({ error: "invalid_client_metadata", error_description: reg.error }, 400);
    return json(reg.client, 201);
  }

  // ---- /authorize: start the login. Stash the client's PKCE + state, then
  // bounce the browser to Supabase for the provider handshake (our own PKCE
  // verifier guards the Supabase leg). ----
  if (req.method === "GET" && sub === "/authorize") {
    const p = parseAuthorizeParams(new URL(req.url).searchParams);
    if (!p.ok) return json({ error: "invalid_request", error_description: p.error }, 400);
    const flowId = randomToken(18);
    const providerVerifier = randomToken(48);
    const providerChallenge = await s256(providerVerifier);
    const { error } = await admin().from("mcp_oauth_flows").insert({
      flow_id: flowId,
      client_id: p.clientId,
      client_redirect_uri: p.redirectUri,
      client_state: p.state,
      client_code_challenge: p.codeChallenge,
      provider_verifier: providerVerifier,
    });
    if (error) return json({ error: "server_error", error_description: error.message }, 500);
    const callback = `${ISSUER}/callback?flow=${flowId}`;
    return redirect(supabaseAuthorizeUrl(SB_URL, PROVIDER, callback, providerChallenge));
  }

  // ---- /callback: Supabase returns here with ?code=. Exchange it for the
  // session, verify the email is Raven's, mint our auth code, hand it back to
  // the client at its registered redirect. ----
  if (req.method === "GET" && sub === "/callback") {
    const q = new URL(req.url).searchParams;
    const flowId = q.get("flow") ?? "";
    const providerCode = q.get("code") ?? "";
    const providerErr = q.get("error_description") || q.get("error");
    const { data: flow } = await admin().from("mcp_oauth_flows").select("*").eq("flow_id", flowId).maybeSingle();
    if (!flow) return json({ error: "invalid_flow" }, 400);
    const back = (err?: string, code?: string) =>
      redirect(err
        ? `${flow.client_redirect_uri}${flow.client_redirect_uri.includes("?") ? "&" : "?"}error=${encodeURIComponent(err)}${flow.client_state ? `&state=${encodeURIComponent(flow.client_state)}` : ""}`
        : buildClientRedirect(flow.client_redirect_uri as string, code as string, flow.client_state as string));

    if (providerErr || !providerCode) return back(providerErr || "access_denied");

    // Exchange the Supabase auth code for a session (GoTrue PKCE grant).
    const ex = await fetch(`${SB_URL}/auth/v1/token?grant_type=pkce`, {
      method: "POST",
      headers: { apikey: e.authKey, "Content-Type": "application/json" },
      body: JSON.stringify({ auth_code: providerCode, code_verifier: flow.provider_verifier }),
    });
    const session = await ex.json().catch(() => ({}));
    const email: string | null = session?.user?.email ?? null;
    if (!ex.ok || !email) return back("access_denied");
    if (!isRaven(email, RAVEN_EMAIL)) return back("access_denied"); // not the authority

    const authCode = randomToken(32);
    await admin().from("mcp_oauth_flows").update({ auth_code: authCode, email }).eq("flow_id", flowId);
    return back(undefined, authCode);
  }

  // ---- /token: client exchanges its auth code (+ PKCE verifier) for an access
  // token. We verify the client's PKCE, then issue an opaque token bound to the
  // verified email. ----
  if (req.method === "POST" && sub === "/token") {
    const b = await readBody(req);
    if ((b.grant_type ?? "") !== "authorization_code") return json({ error: "unsupported_grant_type" }, 400);
    const code = b.code ?? "";
    const verifier = b.code_verifier ?? "";
    const { data: flow } = await admin().from("mcp_oauth_flows").select("*").eq("auth_code", code).maybeSingle();
    if (!flow || !flow.email) return json({ error: "invalid_grant" }, 400);
    if (!(await verifyPkce(verifier, flow.client_code_challenge as string))) return json({ error: "invalid_grant", error_description: "PKCE failed" }, 400);

    const token = randomToken(40);
    const expiresAt = new Date(Date.now() + TOKEN_TTL_SECONDS * 1000).toISOString();
    const { error } = await admin().from("mcp_oauth_tokens").insert({ token, email: flow.email, expires_at: expiresAt });
    if (error) return json({ error: "server_error", error_description: error.message }, 500);
    await admin().from("mcp_oauth_flows").delete().eq("flow_id", flow.flow_id); // single-use code
    return json({ access_token: token, token_type: "Bearer", expires_in: TOKEN_TTL_SECONDS, scope: "jarvis" });
  }

  // ---- GET base: friendly discovery/health (some clients probe before POST) ----
  if (req.method === "GET") {
    return json({
      server: SERVER_INFO,
      protocolVersion: PROTOCOL_VERSION,
      transport: "streamable-http",
      tools: TOOLS.map((t) => t.name),
      auth: REQUIRE_AUTH ? `oauth (${PROVIDER})` : "open",
      note: "POST JSON-RPC 2.0 to this URL. MCP endpoint for JARVIS.",
    });
  }

  if (req.method !== "POST") return new Response("method not allowed", { status: 405, headers: CORS });

  // ---- MCP transport: identity-aware auth gate ----
  const identity = await bearerIdentity(req.headers.get("authorization"), e.token);
  if (REQUIRE_AUTH && !identity) {
    // Challenge → the client discovers our OAuth server and runs the flow.
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401,
      headers: { ...JSON_H, "WWW-Authenticate": `Bearer realm="jarvis-mcp", resource_metadata="${ISSUER}/.well-known/oauth-protected-resource"` },
    });
  }

  let body: unknown;
  try { body = await req.json(); }
  catch { return json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "parse error" } }, 400); }

  // MCP allows a single message or a batch. Notifications (no id) yield no reply.
  const messages: RpcMessage[] = Array.isArray(body) ? body as RpcMessage[] : [body as RpcMessage];
  const responses = [];
  for (const m of messages) {
    const res = await handleRpc(m, e);
    if (res) responses.push(res);
  }

  if (responses.length === 0) return new Response(null, { status: 202, headers: CORS });
  const payload = Array.isArray(body) ? responses : responses[0];
  return json(payload);
});
