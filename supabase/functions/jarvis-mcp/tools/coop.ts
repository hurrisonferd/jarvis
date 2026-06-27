// tools/coop.ts — Co-op Command Center. Real-time command queue for Lilith + Shaka.
// Post commands from either satellite. Target satellite reads + executes.
// No polling needed — Supabase real-time pushes to both sessions.

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { rest, text } from "../core/http.ts";

export function registerCoopTools(server: McpServer): void {
  server.registerTool(
    "coop_post_command",
    {
      title: "Co-op — Post Command",
      description: "Post a command to Lilith or Shaka. The target satellite will execute it on next turn. Use this to remotely control the other satellite from either device.",
      inputSchema: {
        target_satellite: z.enum(["lilith", "shaka", "both"]).describe("Which satellite gets this command"),
        command: z.string().describe("The command to execute"),
        posted_by: z.enum(["lilith", "shaka"]).describe("Who is posting this command"),
      },
    },
    async ({ target_satellite, command, posted_by }) => {
      try {
        const body = { target_satellite, command, posted_by };
        const res = await rest("coop_commands", { method: "POST", body });
        return text({ ok: true, posted: res[0] });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );

  server.registerTool(
    "coop_get_commands",
    {
      title: "Co-op — Get Commands",
      description: "Get pending commands for this satellite. Call this at the start of every turn. Returns commands addressed to you (lilith or shaka) or 'both'.",
      inputSchema: {
        satellite: z.enum(["lilith", "shaka"]).describe("Your satellite name"),
        limit: z.number().optional().default(10).describe("Max commands to return"),
      },
    },
    async ({ satellite, limit }) => {
      try {
        const query = `target_satellite=eq.${satellite}&or=(target_satellite.eq.both)&status=eq.pending&order=created_at.asc&limit=${limit}`;
        const rows = await rest(`coop_commands?${query}`);
        return text({ ok: true, commands: rows });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );

  server.registerTool(
    "coop_done",
    {
      title: "Co-op — Mark Done",
      description: "Mark a command as done. Post the result so the other satellite can see what you did.",
      inputSchema: {
        id: z.string().describe("Command ID to mark done"),
        result: z.string().describe("What happened when you executed the command"),
      },
    },
    async ({ id, result }) => {
      try {
        const body = { status: "done", result };
        const res = await rest(`coop_commands?id=eq.${id}`, { method: "PATCH", body });
        return text({ ok: true, updated: res });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );
}