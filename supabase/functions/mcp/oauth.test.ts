// OAuth bridge tests. Run: node --experimental-strip-types oauth.test.ts
import {
  authServerMetadata,
  b64url,
  buildClientRedirect,
  isRaven,
  parseAuthorizeParams,
  protectedResourceMetadata,
  randomToken,
  registerClient,
  s256,
  supabaseAuthorizeUrl,
  verifyPkce,
} from "./oauth.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

const ISSUER = "https://x.supabase.co/functions/v1/mcp";

// --- protected resource metadata ---
const prm = protectedResourceMetadata(ISSUER, ISSUER);
check("PRM names the authorization server", prm.authorization_servers[0] === ISSUER);
check("PRM advertises header bearer", prm.bearer_methods_supported.includes("header"));

// --- auth server metadata ---
const asm = authServerMetadata(ISSUER);
check("ASM authorize endpoint", asm.authorization_endpoint === ISSUER + "/authorize");
check("ASM token endpoint", asm.token_endpoint === ISSUER + "/token");
check("ASM registration endpoint", asm.registration_endpoint === ISSUER + "/register");
check("ASM requires PKCE S256", asm.code_challenge_methods_supported.includes("S256") && asm.code_challenge_methods_supported.length === 1);
check("ASM is a public client model", asm.token_endpoint_auth_methods_supported.includes("none"));
check("ASM only auth-code grant", asm.grant_types_supported.length === 1 && asm.grant_types_supported[0] === "authorization_code");

// --- dynamic client registration ---
const reg = registerClient({ redirect_uris: ["https://claude.ai/api/mcp/auth_callback"], client_name: "Claude" }, () => "mcp_fixed");
check("DCR issues a client_id", reg.ok && (reg as any).client.client_id === "mcp_fixed");
check("DCR echoes redirect_uris", reg.ok && (reg as any).client.redirect_uris[0] === "https://claude.ai/api/mcp/auth_callback");
check("DCR keeps client public (no secret)", reg.ok && (reg as any).client.token_endpoint_auth_method === "none" && !("client_secret" in (reg as any).client));
check("DCR rejects missing redirect_uris", !registerClient({}).ok);
check("DCR rejects non-absolute redirect", !registerClient({ redirect_uris: ["/relative"] }).ok);

// --- PKCE S256 round-trip ---
// challenge for verifier "abc123" computed via the same b64url(SHA-256) path.
const verifier = "the-quick-brown-fox-jumps-over-the-lazy-dog-0123456789";
const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
const challenge = b64url(new Uint8Array(digest));
check("PKCE verifies a correct verifier", await verifyPkce(verifier, challenge));
check("PKCE rejects a wrong verifier", !(await verifyPkce("wrong", challenge)));
check("PKCE rejects empty inputs", !(await verifyPkce("", challenge)) && !(await verifyPkce(verifier, "")));

// --- b64url has no padding or unsafe chars ---
check("b64url is url-safe + unpadded", !/[+/=]/.test(b64url(new Uint8Array([251, 252, 253, 254, 255]))));

// --- random tokens are unique + non-trivial ---
const t1 = randomToken(), t2 = randomToken();
check("randomToken is unique", t1 !== t2 && t1.length >= 40);

// --- identity gate ---
const RAVEN = "johnbarber720@gmail.com";
check("isRaven matches Raven (case-insensitive)", isRaven("JohnBarber720@Gmail.com", RAVEN));
check("isRaven rejects a stranger", !isRaven("someone@else.com", RAVEN));
check("isRaven rejects null", !isRaven(null, RAVEN));

// --- authorize param validation ---
const good = parseAuthorizeParams(new URLSearchParams({ response_type: "code", redirect_uri: "https://claude.ai/cb", code_challenge: "abc", code_challenge_method: "S256", state: "xyz", client_id: "mcp_1" }));
check("authorize accepts a valid PKCE request", good.ok && (good as any).redirectUri === "https://claude.ai/cb" && (good as any).state === "xyz");
check("authorize rejects non-code response_type", !parseAuthorizeParams(new URLSearchParams({ response_type: "token", redirect_uri: "https://x/cb", code_challenge: "a", code_challenge_method: "S256" })).ok);
check("authorize rejects missing PKCE", !parseAuthorizeParams(new URLSearchParams({ response_type: "code", redirect_uri: "https://x/cb" })).ok);
check("authorize rejects plain PKCE method", !parseAuthorizeParams(new URLSearchParams({ response_type: "code", redirect_uri: "https://x/cb", code_challenge: "a", code_challenge_method: "plain" })).ok);
check("authorize rejects relative redirect_uri", !parseAuthorizeParams(new URLSearchParams({ response_type: "code", redirect_uri: "/cb", code_challenge: "a", code_challenge_method: "S256" })).ok);

// --- supabase authorize URL ---
const sbUrl = supabaseAuthorizeUrl("https://x.supabase.co", "github", "https://x.supabase.co/functions/v1/mcp/callback?flow=f1", "CHAL");
check("supabase URL targets the provider authorize", sbUrl.startsWith("https://x.supabase.co/auth/v1/authorize?"));
check("supabase URL carries the provider", new URL(sbUrl).searchParams.get("provider") === "github");
check("supabase URL carries the PKCE challenge", new URL(sbUrl).searchParams.get("code_challenge") === "CHAL");
check("supabase URL round-trips redirect_to", new URL(sbUrl).searchParams.get("redirect_to")!.includes("flow=f1"));

// --- client redirect builder ---
const cr = buildClientRedirect("https://claude.ai/cb", "AUTHCODE", "STATE");
check("client redirect carries code + state", new URL(cr).searchParams.get("code") === "AUTHCODE" && new URL(cr).searchParams.get("state") === "STATE");
const crNoState = buildClientRedirect("https://claude.ai/cb?x=1", "C", "");
check("client redirect preserves existing query, omits empty state", crNoState.includes("x=1") && !crNoState.includes("state="));

// --- s256 derivation matches verifyPkce ---
const v = "verifier-xyz-1234567890";
check("s256 derives the challenge verifyPkce accepts", await verifyPkce(v, await s256(v)));

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
