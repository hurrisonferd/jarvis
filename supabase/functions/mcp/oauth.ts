// OAuth 2.1 bridge logic for the JARVIS MCP server — pure functions (no Deno,
// no network) so it unit-tests under `node --experimental-strip-types`.
//
// The shape: an MCP client (Claude.ai, ChatGPT) treats this endpoint as a
// protected resource. On a 401 it discovers our authorization server, registers
// itself (Dynamic Client Registration, RFC 7591), runs Authorization Code +
// PKCE, and gets a token. We bridge that flow to Supabase Auth → Google, then
// gate on the verified email being Raven's. Sovereign identity as the key.
//
// This module owns the deterministic pieces: discovery metadata, DCR, PKCE
// verification. The Google round-trip (authorize/callback/token) lives in
// index.ts because it needs network + Supabase, and is verified live.

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

// base64url without padding — the PKCE + token wire format.
export function b64url(bytes: Uint8Array): string {
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// PKCE S256 verification: SHA-256(verifier) must equal the stored challenge.
// async because it uses WebCrypto (present in Deno and Node 22 as global crypto).
export async function verifyPkce(verifier: string, challenge: string): Promise<boolean> {
  if (!verifier || !challenge) return false;
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
  return b64url(new Uint8Array(digest)) === challenge;
}

// A short random opaque token (authorization codes, flow ids).
export function randomToken(bytes = 32): string {
  return b64url(crypto.getRandomValues(new Uint8Array(bytes)));
}

// Is this the authority? Identity gate — only Raven's verified email may write.
export function isRaven(email: string | null | undefined, ravenEmail: string): boolean {
  return !!email && !!ravenEmail && email.toLowerCase() === ravenEmail.toLowerCase();
}
