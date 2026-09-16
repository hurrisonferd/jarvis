// tools/trinity.ts — BLACKWALL HOLD adapter for private Trinity conversation logs.
//
// Trinity can contain private conversation material. The historical module read and
// wrote Jarvis-Private with a credential that was not request-bound and confused an
// MCP control token with GitHub authority. Until the MCP transport has a private-read
// capability, both projection and mutation fail closed.

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { text } from "../core/http.ts";

function hold(tool: string, kind: "read" | "effect") {
  return text({
    ok: false,
    status: "held_by_blackwall",
    tool,
    kind,
    reason: "PRIVATE_CONVERSATION_REQUEST_BOUND_AUTH_REQUIRED",
    law: "CONVERSATION != PUBLIC_TELEMETRY; MCP_TOKEN != GITHUB_TOKEN",
    next_contract: "authenticated private-read/effect capability + dedicated GITHUB_TOKEN_PRIVATE + purpose/retention receipt",
  });
}

export function registerTrinityTools(server: McpServer): void {
  server.registerTool(
    "jarvis_trinity_read",
    {
      title: "Trinity — Read Three-Way Sync (Blackwall hold)",
      description: "Private conversation projection is held until the caller is authenticated for this data scope.",
      inputSchema: {
        date: z.string().max(20).optional(),
        since_time: z.string().max(16).optional(),
        limit: z.number().int().min(1).max(100).optional().default(20),
      },
    },
    async () => hold("jarvis_trinity_read", "read"),
  );

  server.registerTool(
    "jarvis_trinity_write",
    {
      title: "Trinity — Write Three-Way Sync (Blackwall hold)",
      description: "Private conversation mutation is held until request-bound effect authority exists.",
      inputSchema: {
        speaker: z.enum(["JARVIS", "AYRE", "GEMINI"]),
        raven_message: z.string().max(8000).optional(),
        message: z.string().max(16000),
        timestamp: z.string().max(16).optional(),
      },
    },
    async () => hold("jarvis_trinity_write", "effect"),
  );
}
