// tools/coop.ts — Co-op Command Center. Command queue for Lilith + Shaka.
// Uses dex_events table (type='coop_command') as the backing store.
// detail field contains JSON: {cmd, status, result}
// Also uses SSE relay for instant delivery to connected sessions.

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { rest, text } from "../core/http.ts";

const SSE_RELAY = "https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/coop-sse-relay";

async function sseBroadcast(command: string, from: string): Promise<{ ok: boolean; delivered?: number; error?: string }> {
  const apiKey = Deno.env.get("OPENHANDS_API_KEY");
  try {
    const resp = await fetch(`${SSE_RELAY}/broadcast`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${apiKey}`, "Content-Type": "application/json" },
      body: JSON.stringify({ command, from })
    });
    return await resp.json();
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}

async function sseStatus(): Promise<{ ok: boolean; clients?: number; peers?: string[] }> {
  const apiKey = Deno.env.get("OPENHANDS_API_KEY");
  try {
    const resp = await fetch(`${SSE_RELAY}/status`, {
      headers: { "Authorization": `Bearer ${apiKey}` }
    });
    return await resp.json();
  } catch {
    return { ok: false };
  }
}

export function registerCoopTools(server: McpServer): void {
  // ═══════════════════════════════════════════════════════════════
  // BROADCAST — Instant command to ALL connected satellites via SSE
  // ═══════════════════════════════════════════════════════════════
  server.registerTool(
    "coop_broadcast",
    {
      title: "Co-op — Broadcast Command (SSE, instant)",
      description: "Send a command to ALL connected satellites INSTANTLY via SSE relay. Both Lilith and Shaka receive it in milliseconds if they're connected to the relay. Use this for real-time coordination. Also logs to dex_events for persistence.",
      inputSchema: {
        command: z.string().describe("Command to broadcast to all satellites"),
        from: z.enum(["lilith", "shaka", "atlas", "stella"]).describe("Who is sending this"),
        priority: z.enum(["low", "normal", "high"]).optional().default("normal").describe("Priority level"),
      },
    },
    async ({ command, from, priority }) => {
      try {
        // Broadcast via SSE for instant delivery
        const sseResult = await sseBroadcast(command, from);
        
        // Also persist to dex_events for non-connected sessions
        const detail = JSON.stringify({ cmd: command, status: "broadcast", from, priority, sse_delivered: sseResult.delivered });
        await rest("dex_events", { method: "POST", body: { tool: "coop", tier: "broadcast", actor: from, detail, type: "coop_broadcast" } });
        
        const status = await sseStatus();
        return text({
          ok: true,
          sse_delivered: sseResult.delivered ?? 0,
          sse_clients: status.clients ?? 0,
          peers: status.peers ?? [],
          message: `Broadcast to ${sseResult.delivered ?? 0} connected clients`
        });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );

  // ═══════════════════════════════════════════════════════════════
  // TASK COORDINATION — Prevent overlap, parallel workers
  // ═══════════════════════════════════════════════════════════════
  server.registerTool(
    "coop_claim_task",
    {
      title: "Co-op — Claim Task (prevents overlap)",
      description: "Claim a task before working on it. First to claim wins — others see it's taken and skip it. Prevents duplicate work in parallel execution. Always call this BEFORE starting work.",
      inputSchema: {
        task_id: z.string().describe("Unique task identifier (e.g., 'audit-001', 'fix-login')"),
        description: z.string().describe("Brief description of what this task involves"),
        claimed_by: z.enum(["lilith", "shaka", "atlas", "stella"]).describe("Who is claiming this task"),
      },
    },
    async ({ task_id, description, claimed_by }) => {
      try {
        // Check if already claimed
        const query = `type=eq.coop_task&tier=eq.${task_id}&order=created_at.desc&limit=1`;
        const existing = await rest(`dex_events?${query}`) as any[];
        
        if (existing.length) {
          const d = JSON.parse(existing[0].detail);
          if (d.status === "in_progress") {
            return text({ ok: false, error: `Task ${task_id} already claimed by ${d.claimed_by}`, claimed_by: d.claimed_by });
          }
        }
        
        // Claim it
        const detail = JSON.stringify({ task_id, description, status: "in_progress", claimed_by, started_at: new Date().toISOString() });
        await rest("dex_events", { method: "POST", body: { tool: "coop", tier: task_id, actor: claimed_by, detail, type: "coop_task" } });
        
        // Broadcast the claim so other workers know
        await sseBroadcast(`[TASK CLAIMED] ${task_id} by ${claimed_by}`, claimed_by);
        
        return text({ ok: true, task_id, claimed_by, message: `Task ${task_id} claimed` });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );

  server.registerTool(
    "coop_complete_task",
    {
      title: "Co-op — Complete Task",
      description: "Mark a task as done with results. Broadcasts completion so other workers know it's finished.",
      inputSchema: {
        task_id: z.string().describe("Task ID that was claimed"),
        result: z.string().describe("What was accomplished"),
        completed_by: z.enum(["lilith", "shaka", "atlas", "stella"]).describe("Who completed this"),
      },
    },
    async ({ task_id, result, completed_by }) => {
      try {
        // Update the task record
        const query = `type=eq.coop_task&tier=eq.${task_id}&order=created_at.desc&limit=1`;
        const rows = await rest(`dex_events?${query}`) as any[];
        
        if (rows.length) {
          const d = JSON.parse(rows[0].detail);
          d.status = "done";
          d.result = result;
          d.completed_by = completed_by;
          d.completed_at = new Date().toISOString();
          await rest(`dex_events?id=eq.${rows[0].id}`, { method: "PATCH", body: { detail: JSON.stringify(d) } });
        }
        
        // Broadcast completion
        await sseBroadcast(`[TASK DONE] ${task_id} by ${completed_by}: ${result.slice(0, 100)}`, completed_by);
        
        return text({ ok: true, task_id, result: result.slice(0, 200) });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );

  server.registerTool(
    "coop_get_tasks",
    {
      title: "Co-op — Get Task Status",
      description: "See all current tasks and their status. Shows what's claimed, in progress, and done.",
      inputSchema: {
        include_done: z.boolean().optional().default(true).describe("Include completed tasks"),
        limit: z.number().optional().default(20).describe("Max tasks to return"),
      },
    },
    async ({ include_done, limit }) => {
      try {
        let query = `type=eq.coop_task&order=created_at.desc&limit=${limit}`;
        if (!include_done) {
          query += `&detail=not.ilike.*"status"%3A"done"*`;
        }
        const rows = await rest(`dex_events?${query}`) as any[];
        const tasks = rows.map((r: any) => {
          try {
            const d = JSON.parse(r.detail);
            return { task_id: d.task_id, description: d.description, status: d.status, claimed_by: d.claimed_by, result: d.result, created_at: r.created_at };
          } catch {
            return { task_id: r.tier, status: "unknown", created_at: r.created_at };
          }
        });
        return text({ ok: true, tasks });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );

  server.registerTool(
    "coop_status",
    {
      title: "Co-op — Status (SSE + workers)",
      description: "See who's connected to the SSE relay and what tasks are in progress.",
      inputSchema: {},
    },
    async () => {
      const status = await sseStatus();
      const tasks = await rest(`type=eq.coop_task&detail=ilike.*"status"%3A"in_progress"*&order=created_at.desc`) as any[];
      const inProgress = tasks.map((r: any) => {
        const d = JSON.parse(r.detail);
        return { task_id: d.task_id, claimed_by: d.claimed_by };
      });
      return text({ ok: true, sse: status, in_progress: inProgress });
    },
  );

  // ═══════════════════════════════════════════════════════════════
  // LEGACY — kept for backward compatibility
  // ═══════════════════════════════════════════════════════════════
  server.registerTool(
    "coop_execute",
    {
      title: "Co-op — Execute on Peer (legacy)",
      description: "Execute a command on Lilith or Shaka by starting a new OpenHands conversation. Consider using coop_broadcast instead for instant delivery.",
      inputSchema: {
        target_satellite: z.enum(["lilith", "shaka", "atlas", "stella"]).describe("Which satellite gets this command"),
        command: z.string().describe("The command to execute"),
        posted_by: z.enum(["lilith", "shaka", "atlas", "stella"]).describe("Who is posting this command"),
      },
    },
    async ({ target_satellite, command, posted_by }) => {
      try {
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
        
        const detail = JSON.stringify({ cmd: command, status: "executing", result: null, conv_id: convId, conv_url: convUrl });
        await rest("dex_events", { method: "POST", body: { tool: "coop", tier: target_satellite, actor: posted_by, detail, type: "coop_command" } });
        
        return text({ ok: true, conversation_id: convId, conversation_url: convUrl, message: `Started conversation for ${target_satellite}` });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );

  server.registerTool(
    "coop_get_commands",
    {
      title: "Co-op — Get Commands (legacy)",
      description: "Get pending commands for this satellite. Consider using SSE broadcast instead.",
      inputSchema: {
        satellite: z.enum(["lilith", "shaka", "atlas", "stella"]).describe("Your satellite name"),
        limit: z.number().optional().default(10).describe("Max commands to return"),
      },
    },
    async ({ satellite, limit }) => {
      try {
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
      title: "Co-op — Mark Done (legacy)",
      description: "Mark a command as done. Consider using coop_complete_task instead.",
      inputSchema: {
        id: z.string().describe("Command ID to mark done"),
        result: z.string().describe("What happened when you executed the command"),
      },
    },
    async ({ id, result }) => {
      try {
        const rows = await rest(`dex_events?id=eq.${id}`) as any[];
        if (!rows.length) return text({ ok: false, error: "not found" });
        try {
          const d = JSON.parse(rows[0].detail);
          d.status = "done";
          d.result = result;
          await rest(`dex_events?id=eq.${id}`, { method: "PATCH", body: { detail: JSON.stringify(d) } });
          return text({ ok: true });
        } catch {
          return text({ ok: false, error: "could not parse detail" });
        }
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );
}