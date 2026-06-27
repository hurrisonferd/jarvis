// tools/coop.ts — Co-op Command Center. Command queue for Lilith + Shaka.
// Uses dex_events table (type='coop_command') as the backing store.
// detail field contains JSON: {cmd, status, result}

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { rest, text } from "../core/http.ts";

export function registerCoopTools(server: McpServer): void {
  server.registerTool(
    "coop_execute",
    {
      title: "Co-op — Execute on Peer",
      description: "Execute a command on Lilith or Shaka by starting a new OpenHands conversation. Use this to remotely control the other satellite from either device. The peer will run the command in a fresh conversation.",
      inputSchema: {
        target_satellite: z.enum(["lilith", "shaka"]).describe("Which satellite gets this command"),
        command: z.string().describe("The command to execute"),
        posted_by: z.enum(["lilith", "shaka"]).describe("Who is posting this command"),
      },
    },
    async ({ target_satellite, command, posted_by }) => {
      try {
        // Start a new OpenHands conversation to execute this command
        const apiKey = Deno.env.get("OPENHANDS_API_KEY");
        const payload = {
          initial_message: { content: [{ type: "text", text: `Execute this co-op command from ${posted_by}:\n\n${command}\n\nReport what you did when finished.` }] },
          selected_repository: "hurrisonferd/jarvis",
          title: `Co-op: ${command.slice(0, 40)}...`
        };
        
        const resp = await fetch("https://app.all-hands.dev/api/v1/app-conversations", {
          method: "POST",
          headers: { "Authorization": `Bearer ${apiKey}`, "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        
        if (!resp.ok) {
          const err = await resp.text();
          return text({ ok: false, error: `OpenHands API error: ${err.slice(0, 200)}` });
        }
        
        const result = await resp.json();
        const convId = result.id || result.app_conversation_id;
        const convUrl = `https://app.all-hands.dev/conversations/${convId}`;
        
        // Also log to dex_events
        const detail = JSON.stringify({ cmd: command, status: "executing", result: null, conv_id: convId, conv_url: convUrl });
        const row = { tool: "coop", tier: target_satellite, actor: posted_by, detail, type: "coop_command" };
        await rest("dex_events", { method: "POST", body: row });
        
        return text({ ok: true, conversation_id: convId, conversation_url: convUrl, message: `Started conversation for ${target_satellite}` });
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
        // Filter by type and tier
        const query = `type=eq.coop_command&tier=eq.${satellite}&or=(detail=ilike.*pending*,detail=ilike.*"status"%3A"pending"*)&order=created_at.asc&limit=${limit}`;
        const rows = await rest(`dex_events?${query}`);
        const commands = (rows as any[]).map((r: any) => {
          try {
            const d = JSON.parse(r.detail);
            return { id: r.id, command: d.cmd, status: d.status, result: d.result, posted_by: r.actor, created_at: r.created_at };
          } catch {
            return { id: r.id, command: r.detail, status: "unknown", posted_by: r.actor, created_at: r.created_at };
          }
        }).filter(c => c.status === "pending");
        return text({ ok: true, commands });
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
        // Get current record, update detail
        const rows = await rest(`dex_events?id=eq.${id}`) as any[];
        if (!rows.length) return text({ ok: false, error: "not found" });
        try {
          const d = JSON.parse(rows[0].detail);
          d.status = "done";
          d.result = result;
          const body = { detail: JSON.stringify(d) };
          const res = await rest(`dex_events?id=eq.${id}`, { method: "PATCH", body });
          return text({ ok: true, updated: res });
        } catch {
          return text({ ok: false, error: "could not parse detail" });
        }
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );
}