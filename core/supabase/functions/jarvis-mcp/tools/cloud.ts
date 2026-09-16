// tools/cloud.ts — BLACKWALL HOLD adapter for private Cloud logs.
//
// The historical implementation used JARVIS_MCP_TOKEN as if it were a GitHub PAT
// and exposed private-repo reads/writes from a module with no request-bound auth.
// Credential type confusion + open private data projection is now fail-closed.

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { text } from "../core/http.ts";

function hold(tool: string, kind: "read" | "effect") {
  return text({
    ok: false,
    status: "held_by_blackwall",
    tool,
    kind,
    reason: "PRIVATE_REPO_REQUEST_BOUND_AUTH_REQUIRED",
    law: "MCP_TOKEN != GITHUB_TOKEN; PRIVATE_DATA_REACH != CALLER_AUTHORITY",
    next_contract: "dedicated GITHUB_TOKEN_PRIVATE behind authenticated private-read/effect capability",
  });
}

export function registerCloudTools(server: McpServer): void {
  server.registerTool(
    "jarvis_cloud_read",
    {
      title: "Cloud — Read Daily Log (Blackwall hold)",
      description: "Private Cloud log projection is held until private-read authorization is bound to the MCP request.",
      inputSchema: {
        date: z.string().max(20).optional(),
        limit: z.number().int().min(1).max(100).optional().default(50),
      },
    },
    async () => hold("jarvis_cloud_read", "read"),
  );

  server.registerTool(
    "jarvis_cloud_write",
    {
      title: "Cloud — Write Daily Log (Blackwall hold)",
      description: "Private-repo log mutation is held until request-bound effect authority and a dedicated private GitHub credential exist.",
      inputSchema: {
        model: z.string().max(80),
        action: z.string().max(2000),
        context: z.string().max(4000).optional(),
        status: z.enum(["ok", "warning", "error"]).optional().default("ok"),
      },
    },
    async () => hold("jarvis_cloud_write", "effect"),
  );
}
