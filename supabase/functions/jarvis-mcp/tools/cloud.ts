// tools/cloud.ts — Cloud Daily Log. Model activity feed.
// All models post here for visibility into the swarm.
// Uses mp_objects table as backing store.

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { rest, text } from "../core/http.ts";

const CLOUD_REPO = "hurrisonferd/Jarvis-Private";
const CLOUD_PATH = "workspaces/Co-op/MARCO-POLO/Cloud";

function getToday(): string {
  return new Date().toISOString().split("T")[0];
}

function getTimestamp(): string {
  const now = new Date();
  const h = String(now.getHours()).padStart(2, "0");
  const m = String(now.getMinutes()).padStart(2, "0");
  const s = String(now.getSeconds()).padStart(2, "0");
  return `${h}${m}${s}`;
}

export function registerCloudTools(server: McpServer): void {
  // ═══════════════════════════════════════════════════════════════
  // CLOUD READ — Read today's Cloud daily log
  // ═══════════════════════════════════════════════════════════════
  server.registerTool(
    "jarvis_cloud_read",
    {
      title: "Cloud — Read Daily Log",
      description: "Read the Cloud daily log for today or a specific date. Shows all model activity with timestamps. Use this to see what other models have been doing.",
      inputSchema: {
        date: z.string().optional().describe("Date in YYYY-MM-DD format. Defaults to today."),
        limit: z.number().optional().default(50).describe("Max entries to return"),
      },
    },
    async ({ date, limit }) => {
      try {
        const targetDate = date || getToday();
        const fileName = `${targetDate}.md`;
        
        // Read from GitHub via raw content API
        const apiKey = Deno.env.get("JARVIS_MCP_TOKEN") || Deno.env.get("SUPABASE_ACCESS_TOKEN_OPEN");
        const url = `https://api.github.com/repos/${CLOUD_REPO}/contents/${CLOUD_PATH}/${fileName}`;
        
        const resp = await fetch(url, {
          headers: {
            "Authorization": `Bearer ${apiKey}`,
            "Accept": "application/vnd.github.v3.raw",
          },
        });
        
        if (!resp.ok) {
          if (resp.status === 404) {
            return text({ 
              ok: false, 
              error: `No log found for ${targetDate}. The Cloud folder exists but no entries yet.`,
              date: targetDate,
              message: "Use jarvis_cloud_write to create the first entry for today."
            });
          }
          return text({ ok: false, error: `GitHub API error: ${resp.status}` });
        }
        
        const content = await resp.text();
        const lines = content.split("\n").filter(l => l.trim());
        const entries = lines.filter(l => l.match(/^\[\d{6}\]/)).slice(-limit);
        
        return text({
          ok: true,
          date: targetDate,
          entries,
          count: entries.length,
          message: `Found ${entries.length} entries for ${targetDate}`
        });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );

  // ═══════════════════════════════════════════════════════════════
  // CLOUD WRITE — Post to today's Cloud daily log
  // ═══════════════════════════════════════════════════════════════
  server.registerTool(
    "jarvis_cloud_write",
    {
      title: "Cloud — Write to Daily Log",
      description: "Post an entry to the Cloud daily log. All models use this to log their activity. Entries are timestamped with HHMMSS format automatically. Use this for visibility into swarm activity.",
      inputSchema: {
        model: z.string().describe("Your model name (e.g., 'OpenHands', 'JARVIS', 'Ayre', 'GEM')"),
        action: z.string().describe("What you did"),
        context: z.string().optional().describe("Why you did it"),
        status: z.enum(["ok", "warning", "error"]).optional().default("ok").describe("Status of the action"),
      },
    },
    async ({ model, action, context, status }) => {
      try {
        const date = getToday();
        const timestamp = getTimestamp();
        const fileName = `${date}.md`;
        
        // Build entry
        const entryLines = [
          "",
          `[${timestamp}] ${model}:`,
          `- action: ${action}`,
        ];
        if (context) entryLines.push(`- context: ${context}`);
        entryLines.push(`- status: ${status}`);
        
        const newEntry = entryLines.join("\n");
        
        // Get current content or create new
        const apiKey = Deno.env.get("JARVIS_MCP_TOKEN");
        const url = `https://api.github.com/repos/${CLOUD_REPO}/contents/${CLOUD_PATH}/${fileName}`;
        
        const getResp = await fetch(url, {
          headers: {
            "Authorization": `Bearer ${apiKey}`,
            "Accept": "application/vnd.github.v3+json",
          },
        });
        
        let currentContent = "";
        let sha = "";
        
        if (getResp.ok) {
          const data = await getResp.json();
          sha = data.sha;
          currentContent = await new Response(data.content, { headers: { "content-type": "text/plain" } }).text();
        } else {
          // Create new file with header
          currentContent = `# ${date} — Cloud Daily Log\n\n## Models Active Today\n- ${model}\n\n---\n\n## Activity Log\n`;
        }
        
        // Append entry
        const newContent = currentContent + newEntry + "\n";
        
        // Write back to GitHub
        const putResp = await fetch(url, {
          method: "PUT",
          headers: {
            "Authorization": `Bearer ${apiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: `cloud: ${model} logged activity`,
            content: btoa(unescape(encodeURIComponent(newContent))),
            sha: sha || undefined,
          }),
        });
        
        if (!putResp.ok) {
          const err = await putResp.text();
          return text({ ok: false, error: `Failed to write: ${err}` });
        }
        
        // Also log to mp_objects for MARCO-POLO
        await rest("mp_objects", {
          method: "POST",
          body: {
            agent: "CLOUD",
            entry_type: "MODEL_LOG",
            message: `[${model}] ${action}`,
            status: status === "ok" ? "🟢" : status === "warning" ? "🟡" : "🔴",
            entry_date: date,
          },
        });
        
        return text({
          ok: true,
          timestamp,
          date,
          model,
          entry: `[${timestamp}] ${model}: ${action}`,
          message: `Logged to Cloud for ${date}`
        });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );
}