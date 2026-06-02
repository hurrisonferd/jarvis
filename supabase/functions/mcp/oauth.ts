// OAuth 2.1 bridge logic for the JARVIS MCP server — pure functions (no Deno,
// no network) so it unit-tests under `node --experimental-strip-types`.
//
// The shape: an MCP client (Claude.ai, ChatGPT) treats this endpoint as a
// protected resource. On a 401 it discovers our authorization server, registers
// itself (Dynamic Client Registration, RFC 7591), runs Authorization Code +
// PKCE, and gets a token. We bridge that flow to Supabase Auth → the identity
// provider, then gate on the verified email being Raven's. Identity as the key.
//
// Provider-neutral: Supabase decides which provider (GitHub, Google, …) backs
// the login; this code only cares that a verified email comes back.
//
// This module owns the deterministic pieces (metadata, DCR, PKCE, URL building).
// The network round-trip (talking to Supabase) lives in index.ts, verified live.

// Default identity provider for the Supabase leg. Env-overridable in index.ts.
export const DEFAULT_PROVIDER = "github";
// Issued MCP access-token lifetime. Long, so re-login is rare; no refresh token.
export const TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30; // 30 days

// RFC 9728 — Protected Resource Metadata. Names which auth server guards us.
export function protectedResourceMetadata(resource: string, issuer: string) {
  return {
    resource,
    authorization_servers: [issuer],
    bearer_methods_supported: ["header"],
    scopes_supported: ["jarvis"],
  };
}

// RFC 8414 — Authorization Server Metadata. The client reads this to learn our
// endpoints. PKCE S256 only, public clients (no secret), auth-code grant.
export function authServerMetadata(issuer: string) {
  return {
    issuer,
    authorization_endpoint: `${issuer}/authorize`,
    token_endpoint: `${issuer}/token`,
    registration_endpoint: `${issuer}/register`,
    scopes_supported: ["jarvis"],
    response_types_supported: ["code"],
    grant_types_supported: ["authorization_code"],
    code_challenge_methods_supported: ["S256"],
    token_endpoint_auth_methods_supported: ["none"],
  };
}

// RFC 7591 — Dynamic Client Registration. MCP clients self-register on first
// connect. We're a public PKCE client model, so we mint a client_id and echo
// the client's metadata; no secret is issued. Returns the registration body or
// an error object the caller can shape into a 400.
export function registerClient(
  body: any,
  genId: () => string = () => "mcp_" + crypto.randomUUID(),
): { ok: true; client: Record<string, unknown> } | { ok: false; error: string } {
  const redirectUris = body?.redirect_uris;
  if (!Array.isArray(redirectUris) || redirectUris.length === 0) {
    return { ok: false, error: "redirect_uris required" };
  }
  if (!redirectUris.every((u: unknown) => typeof u === "string" && /^https?:\/\//.test(u))) {
    return { ok: false, error: "redirect_uris must be absolute http(s) URLs" };
  }
  return {
    ok: true,
    client: {
      client_id: genId(),
      redirect_uris: redirectUris,
      token_endpoint_auth_method: "none",
      grant_types: ["authorization_code"],
      response_types: ["code"],
      client_name: typeof body?.client_name === "string" ? body.client_name : "mcp-client",
      client_id_issued_at: Math.floor(Date.now() / 1000),
    },
  };
}

// Validate an inbound /authorize request. We require PKCE S256 — no exceptions.
export function parseAuthorizeParams(
  p: URLSearchParams,
): { ok: true; clientId: string; redirectUri: string; codeChallenge: string; state: string }
  | { ok: false; error: string } {
  const responseType = p.get("response_type") ?? "";
  const redirectUri = p.get("redirect_uri") ?? "";
  const codeChallenge = p.get("code_challenge") ?? "";
  const method = (p.get("code_challenge_method") ?? "").toLowerCase();
  if (responseType !== "code") return { ok: false, error: "unsupported_response_type" };
  if (!/^https?:\/\//.test(redirectUri)) return { ok: false, error: "invalid redirect_uri" };
  if (!codeChallenge || method !== "s256") return { ok: false, error: "PKCE S256 required" };
  return { ok: true, clientId: p.get("client_id") ?? "", redirectUri, codeChallenge, state: p.get("state") ?? "" };
}

// Build the Supabase Auth provider-login URL. Supabase runs the provider
// handshake and redirects back to redirectTo with ?code= (PKCE), which our
// /callback exchanges. code_challenge_method is lowercase per GoTrue.
export function supabaseAuthorizeUrl(supabaseUrl: string, provider: string, redirectTo: string, codeChallenge: string): string {
  const u = new URL(`${supabaseUrl}/auth/v1/authorize`);
  u.searchParams.set("provider", provider);
  u.searchParams.set("redirect_to", redirectTo);
  u.searchParams.set("code_challenge", codeChallenge);
  u.searchParams.set("code_challenge_method", "s256");
  return u.toString();
}

// Hand the authorization code back to the MCP client at its registered redirect.
export function buildClientRedirect(redirectUri: string, code: string, state: string): string {
  const u = new URL(redirectUri);
  u.searchParams.set("code", code);
  if (state) u.searchParams.set("state", state);
  return u.toString();
}

// base64url without padding — the PKCE + token wire format.
export function b64url(bytes: Uint8Array): string {
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// SHA-256 → base64url. The PKCE challenge derivation. WebCrypto is global in
// both Deno and Node 22.
export async function s256(input: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  return b64url(new Uint8Array(digest));
}

// PKCE S256 verification: SHA-256(verifier) must equal the stored challenge.
export async function verifyPkce(verifier: string, challenge: string): Promise<boolean> {
  if (!verifier || !challenge) return false;
  return (await s256(verifier)) === challenge;
}

// A short random opaque token (authorization codes, flow ids, access tokens).
export function randomToken(bytes = 32): string {
  return b64url(crypto.getRandomValues(new Uint8Array(bytes)));
}

// Is this the authority? Identity gate — only Raven's verified email may in.
export function isRaven(email: string | null | undefined, ravenEmail: string): boolean {
  return !!email && !!ravenEmail && email.toLowerCase() === ravenEmail.toLowerCase();
}
