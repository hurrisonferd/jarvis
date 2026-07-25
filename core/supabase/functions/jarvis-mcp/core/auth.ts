// core/auth.ts — the AEGIS write gate. Reads + suit-up are open; persistent writes require
// the connector to carry JARVIS_MCP_TOKEN. A held write self-diagnoses (names WHY it's gated)
// without ever exposing the secret. (Extracted from index.ts, zero behavior change.)

import { MCP_TOKEN } from "./env.ts";
import { text } from "./http.ts";

// The write token, accepted from wherever the connector can carry it: an Authorization
// bearer, an x-jarvis-token header, or a ?token= URL param (the universal fallback —
// ChatGPT connectors that send no auth can append it to the connector URL). First match wins.
export function authToken(req: Request): string {
  const raw = req.headers.get("authorization") ?? "";
  if (raw.toLowerCase().startsWith("bearer ")) return raw.slice(7).trim();
  const h = req.headers.get("x-jarvis-token");
  if (h && h.trim()) return h.trim();
  try {
    const q = new URL(req.url).searchParams.get("token");
    if (q && q.trim()) return q.trim();
  } catch { /* malformed url — no token */ }
  return "";
}

// AEGIS token diagnosis — names WHY a write is gated so a held response is actionable:
//   server_unset   — the function has NO JARVIS_MCP_TOKEN baked in (secret missing, or set
//                    AFTER the last deploy → redeploy to pick it up; secrets bake at deploy).
//   client_missing — the connector sent no token at all.
//   mismatch       — the connector sent a token, but it differs from the function's.
export type TokenState = "ok" | "server_unset" | "client_missing" | "mismatch";

export function tokenState(req: Request): TokenState {
  const sent = authToken(req);
  if (!MCP_TOKEN) return "server_unset";
  if (!sent) return "client_missing";
  return sent === MCP_TOKEN ? "ok" : "mismatch";
}

// AEGIS write gate. Persistent writes require the JARVIS_MCP_TOKEN bearer. Consent is the
// client's own Allow/Deny prompt before the call. Fails closed when no token is configured.
export function writeAuthorized(req: Request): boolean {
  return tokenState(req) === "ok";
}

// Held response when the write isn't authorized. Reports the precise token_state and a
// value-free fingerprint (lengths only — NEVER the secret itself) so the failure
// self-diagnoses. GL5: a systematic gate failure is also surfaced in the function logs.
export function heldForApproval(action: string, preview: unknown, req: Request) {
  const st = tokenState(req);
  const reason: Record<TokenState, string> = {
    ok: "Authorized — no hold.",
    server_unset: "Write not authorized: JARVIS_MCP_TOKEN is not set in THIS function's deployed env — the secret is missing, or was set after the last deploy. Redeploy jarvis-mcp (secrets bake at deploy) so it picks up the token.",
    client_missing: "Write not authorized: the connector sent no token. Add JARVIS_MCP_TOKEN to the connector — as an Authorization bearer, an x-jarvis-token header, or ?token=… on the connector URL.",
    mismatch: "Write not authorized: the connector's token does NOT match the function's JARVIS_MCP_TOKEN. The values differ — confirm the Supabase secret equals the token the connector carries, then redeploy.",
  };
  if (st !== "ok") {
    console.error(`AEGIS hold [${action}] token_state=${st} client_len=${authToken(req).length} server_len=${MCP_TOKEN.length}`);
  }
  return text({
    status: "held_by_aegis",
    token_state: st,
    reason: reason[st],
    // value-free fingerprint: lengths only, so a mismatch vs an unset secret is visible
    // without ever exposing the token.
    diag: { client_token_len: authToken(req).length, server_token_len: MCP_TOKEN.length },
    action,
    preview,
  });
}
