// core/auth.ts — the AEGIS write gate. Reads + suit-up may remain open where the
// individual tool is safe; persistent writes require the connector to carry
// ATOM_MCP_TOKEN (with JARVIS_MCP_TOKEN retained as a legacy server fallback).
//
// BLACKWALL: secrets belong in headers, never URLs. Held responses diagnose only
// the auth state, never secret length/fingerprints.

import { MCP_TOKEN } from "./env.ts";
import { text } from "./http.ts";

export function authToken(req: Request): string {
  const h = req.headers.get("x-jarvis-token");
  if (h && h.trim()) return h.trim();
  const raw = req.headers.get("authorization") ?? "";
  if (raw.toLowerCase().startsWith("bearer ")) return raw.slice(7).trim();
  return "";
}

export type TokenState = "ok" | "server_unset" | "client_missing" | "mismatch";

function safeEqual(a: string, b: string): boolean {
  if (!a || !b || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export function tokenState(req: Request): TokenState {
  const sent = authToken(req);
  if (!MCP_TOKEN) return "server_unset";
  if (!sent) return "client_missing";
  return safeEqual(sent, MCP_TOKEN) ? "ok" : "mismatch";
}

export function writeAuthorized(req: Request): boolean {
  return tokenState(req) === "ok";
}

export function heldForApproval(action: string, preview: unknown, req: Request) {
  const st = tokenState(req);
  const reason: Record<TokenState, string> = {
    ok: "Authorized — no hold.",
    server_unset: "Write not authorized: the deployed MCP write credential is not configured.",
    client_missing: "Write not authorized: the connector sent no MCP write credential. Use a bearer or x-jarvis-token header.",
    mismatch: "Write not authorized: the connector credential does not match the deployed MCP write credential.",
  };
  if (st !== "ok") console.error(`AEGIS hold [${action}] token_state=${st}`);
  return text({
    status: "held_by_aegis",
    token_state: st,
    reason: reason[st],
    action,
    preview,
  });
}
