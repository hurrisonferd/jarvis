// core/env.ts — the forge's foundation. Environment + node identity + the advertised tool
// surface, in one place every other module imports. First stone of the modular grimoire:
// adding a spell shouldn't mean editing a 2,000-line file — it means a new module that
// imports from here. (Extracted from index.ts, zero behavior change.)

export type Json = Record<string, unknown>;

export const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
export const SERVICE_KEY =
  Deno.env.get("SUPABASE_SERVICE_KEY") ??
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ??
  "";
// Canonical connector bearer with legacy fallback. Reads + suit-up are open; writes stay AEGIS-gated.
export const MCP_TOKEN =
  Deno.env.get("ATOM_MCP_TOKEN") ??
  Deno.env.get("JARVIS_MCP_TOKEN") ??
  "";

// THE GRID — this node's identity. Raven's node is the first node.
export const NODE_ID = Deno.env.get("JARVIS_NODE_ID") ?? "raven-node-0";
export const BASE_URL = `${SUPABASE_URL}/functions/v1/jarvis-mcp`;

// Generated from actual server.registerTool(...) calls. CI rejects any registry drift.
export { JARVIS_MCP_VERSION, TOOL_COUNT, TOOL_NAMES, TOOL_SOURCES } from "../tool-registry.generated.ts";
