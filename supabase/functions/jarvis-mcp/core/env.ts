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
// Legacy bearer for writes. Reads + suit-up are open; writes stay AEGIS-gated.
export const MCP_TOKEN = Deno.env.get("JARVIS_MCP_TOKEN") ?? "";

// THE GRID — this node's identity. Raven's node is the first node.
export const NODE_ID = Deno.env.get("JARVIS_NODE_ID") ?? "raven-node-0";
export const BASE_URL = `${SUPABASE_URL}/functions/v1/jarvis-mcp`;

// The node's advertised capabilities (its tool surface) — published in the card.
export const TOOL_NAMES = [
  "jarvis_suit_up", "jarvis_status", "jarvis_council", "jarvis_query", "jarvis_format",
  "jarvis_recall", "jarvis_remember", "jarvis_event", "jarvis_jmms",
  "jarvis_dex_list", "jarvis_dex_search", "jarvis_dex_graph", "jarvis_dex_events", "jarvis_dex_propose",
  "jarvis_jd_resolve", "jarvis_jc_recall", "jarvis_grimoire",
  "jarvis_repo_tree", "jarvis_repo_read", "jarvis_github_tree", "jarvis_github_file", "jarvis_media_view", "jarvis_github_commits", "jarvis_github_write", "jarvis_repo_edit", "jarvis_repo_search", "jarvis_self_test", "jarvis_prs", "jarvis_pr_merge", "jarvis_deploy",
  "jarvis_db_inspect", "jarvis_db_read", "jarvis_db_schema",
  "jarvis_now",
  "jarvis_timeline", "jarvis_identity_read", "jarvis_identity_grow", "jarvis_omnivision",
  "jarvis_eyes", "jarvis_pinch", "jarvis_muster", "jarvis_shiroe", "jarvis_ainz", "jarvis_continuity", "jarvis_listen", "jarvis_dither",
  "jarvis_jip_create", "jarvis_jip_list", "jarvis_jip_apply", "jarvis_jip_revert",
  "jarvis_voice_brief",
  "jarvis_node_card", "jarvis_export", "jarvis_node_inbox", "jarvis_node_send", "jarvis_node_register_key",
  "jarvis_halo",
];
