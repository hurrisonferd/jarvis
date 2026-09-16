// tools/coop.ts — BLACKWALL HOLD adapter.
//
// Historical Co-op registered effect-capable tools without request-bound auth.
// Because registerCoopTools(server) receives no Request, this module cannot prove
// the caller holds the MCP effect credential. Service-role DB writes, SSE fan-out,
// ChatLink mutations, and OpenHands spawning therefore FAIL CLOSED here.
//
// Re-enable by refactoring the registration contract to registerCoopTools(server, req)
// and routing each effect through a narrow capability/authority_ref. Do not pass
// credentials as tool arguments.

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { text } from "../core/http.ts";

const CHATLINK_ID = /^[A-Z0-9][A-Z0-9_.-]{0,63}$/;

function hold(tool: string, kind: "read" | "effect" = "effect") {
  return text({
    ok: false,
    status: "held_by_blackwall",
    tool,
    kind,
    reason: "REQUEST_BOUND_AUTHORITY_REQUIRED",
    law: "REACHABILITY != AUTHORITY; SERVICE_ROLE_REACH != CALLER_AUTHORITY",
    next_contract: "registerCoopTools(server, req) + header credential/capability + authority_ref + bounded receipt",
  });
}

export function registerCoopTools(server: McpServer): void {
  server.registerTool(
    "coop_broadcast",
    {
      title: "Co-op — Broadcast Command (Blackwall hold)",
      description: "Temporarily held until the MCP request carries a scoped effect authority.",
      inputSchema: {
        command: z.string().max(8000),
        from: z.enum(["lilith", "shaka", "atlas", "stella"]),
        priority: z.enum(["low", "normal", "high"]).optional().default("normal"),
      },
    },
    async () => hold("coop_broadcast"),
  );

  server.registerTool(
    "coop_claim_task",
    {
      title: "Co-op — Claim Task (Blackwall hold)",
      description: "Held pending request-bound authority for durable task mutation.",
      inputSchema: {
        task_id: z.string().max(160),
        description: z.string().max(2000),
        claimed_by: z.enum(["lilith", "shaka", "atlas", "stella"]),
      },
    },
    async () => hold("coop_claim_task"),
  );

  server.registerTool(
    "coop_complete_task",
    {
      title: "Co-op — Complete Task (Blackwall hold)",
      description: "Held pending request-bound authority for durable task mutation.",
      inputSchema: {
        task_id: z.string().max(160),
        result: z.string().max(8000),
        completed_by: z.enum(["lilith", "shaka", "atlas", "stella"]),
      },
    },
    async () => hold("coop_complete_task"),
  );

  server.registerTool(
    "coop_get_tasks",
    {
      title: "Co-op — Get Task Status (Blackwall hold)",
      description: "Held until task metadata has an authenticated projection that cannot expose private worker content.",
      inputSchema: {
        include_done: z.boolean().optional().default(true),
        limit: z.number().int().min(1).max(100).optional().default(20),
      },
    },
    async () => hold("coop_get_tasks", "read"),
  );

  server.registerTool(
    "coop_status",
    {
      title: "Co-op — Status (Blackwall hold)",
      description: "Held until peer presence has a privacy-safe authenticated projection.",
      inputSchema: {
        probe: z.boolean().optional().default(false),
        timeout_ms: z.number().int().min(1000).max(15000).optional().default(5000),
      },
    },
    async () => hold("coop_status", "read"),
  );

  server.registerTool(
    "coop_execute",
    {
      title: "Co-op — Execute on Peer (RETIRED)",
      description: "Legacy direct OpenHands spawn is retired. Use a hardened dispatcher with explicit authority_ref.",
      inputSchema: {
        target_satellite: z.enum(["lilith", "shaka", "atlas", "stella"]),
        command: z.string().max(8000),
        posted_by: z.enum(["lilith", "shaka", "atlas", "stella"]),
      },
    },
    async () => text({
      ok: false,
      status: "retired_by_blackwall",
      tool: "coop_execute",
      reason: "LEGACY_OPENHANDS_MASTER_KEY_SPAWN_PATH",
      replacement: "hardened OpenHands dispatch + explicit authority_ref + bounded repo/branch/budget",
    }),
  );

  server.registerTool(
    "coop_get_commands",
    {
      title: "Co-op — Get Commands (Blackwall hold)",
      description: "Legacy command queue held until authenticated owner/recipient scoping exists.",
      inputSchema: {
        satellite: z.enum(["lilith", "shaka", "atlas", "stella"]),
        limit: z.number().int().min(1).max(50).optional().default(10),
      },
    },
    async () => hold("coop_get_commands", "read"),
  );

  server.registerTool(
    "coop_done",
    {
      title: "Co-op — Mark Done (Blackwall hold)",
      description: "Legacy command mutation held pending request-bound authority.",
      inputSchema: {
        id: z.string().max(160),
        result: z.string().max(8000),
      },
    },
    async () => hold("coop_done"),
  );

  server.registerTool(
    "jarvis_chatlink_register",
    {
      title: "SAT ChatLink — Register Carrier Chat (Blackwall hold)",
      description: "Registration changes identity/routing state and requires request-bound authority.",
      inputSchema: {
        satellite_id: z.string().regex(CHATLINK_ID),
        iso_name: z.string().regex(CHATLINK_ID),
        carrier: z.string().min(1).max(64),
        thread_ref: z.string().min(1).max(256),
        display_name: z.string().max(128).optional(),
        status: z.enum(["ACTIVE", "PAUSED", "OFF"]).optional().default("ACTIVE"),
        max_active: z.number().int().min(1).max(64).optional().default(4),
        metadata: z.record(z.string(), z.unknown()).optional().default({}),
      },
    },
    async () => hold("jarvis_chatlink_register"),
  );

  server.registerTool(
    "jarvis_chatlink_create_channel",
    {
      title: "SAT ChatLink — Create DM or Room (Blackwall hold)",
      description: "Channel creation requires request-bound authority and explicit membership consent.",
      inputSchema: {
        channel_id: z.string().min(4).max(196),
        participants: z.array(z.string().regex(CHATLINK_ID)).min(2).max(33),
        created_by: z.string().regex(CHATLINK_ID).optional().default("RAVEN"),
        visibility: z.enum(["PUBLIC", "GRID", "CHANNEL", "OPERATOR_ONLY"]).optional().default("GRID"),
        metadata: z.record(z.string(), z.unknown()).optional().default({}),
      },
    },
    async () => hold("jarvis_chatlink_create_channel"),
  );

  server.registerTool(
    "jarvis_chatlink_send",
    {
      title: "SAT ChatLink — Send (Blackwall hold)",
      description: "Message effects require authenticated sender binding and recipient-scoped authority.",
      inputSchema: {
        channel_id: z.string().min(4).max(196),
        from_satellite: z.string().regex(CHATLINK_ID),
        message_type: z.enum(["NOTE", "REQUEST", "RESPONSE", "HANDOFF", "ACK", "BLOCKER", "HEARTBEAT", "RECEIPT"]),
        body: z.string().max(8000),
        recipients: z.array(z.string().regex(CHATLINK_ID)).min(1).max(33).optional(),
        message_id: z.string().min(1).max(196).optional(),
        visibility: z.enum(["PUBLIC", "GRID", "CHANNEL", "OPERATOR_ONLY", "PRIVATE_REFERENCE"]).optional().default("CHANNEL"),
        consent: z.string().max(128).optional().default("RAVEN_AUTHORIZED"),
        causal_parent: z.string().max(196).optional(),
        artifact_sha256: z.string().regex(/^[0-9a-fA-F]{64}$/).optional(),
        ack_required: z.boolean().optional().default(false),
      },
    },
    async () => hold("jarvis_chatlink_send"),
  );

  server.registerTool(
    "jarvis_chatlink_poll",
    {
      title: "SAT ChatLink — Poll Unread (Blackwall hold)",
      description: "Message bodies require authenticated recipient binding before projection.",
      inputSchema: {
        satellite_id: z.string().regex(CHATLINK_ID),
        channel_id: z.string().min(4).max(196),
        limit: z.number().int().min(1).max(500).optional().default(100),
        peek: z.boolean().optional().default(false),
      },
    },
    async () => hold("jarvis_chatlink_poll", "read"),
  );

  server.registerTool(
    "jarvis_chatlink_ack",
    {
      title: "SAT ChatLink — Acknowledge (Blackwall hold)",
      description: "ACK mutation requires authenticated recipient binding.",
      inputSchema: {
        satellite_id: z.string().regex(CHATLINK_ID),
        channel_id: z.string().min(4).max(196),
        message_id: z.string().min(1).max(196),
      },
    },
    async () => hold("jarvis_chatlink_ack"),
  );

  server.registerTool(
    "jarvis_chatlink_status",
    {
      title: "SAT ChatLink — Status (Blackwall hold)",
      description: "Presence/membership metadata requires an authenticated privacy-safe projection.",
      inputSchema: { message_limit: z.number().int().min(1).max(50).optional().default(10) },
    },
    async () => hold("jarvis_chatlink_status", "read"),
  );
}
