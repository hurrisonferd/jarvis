// tools/trinity.ts — Trinity Three-Way Sync. Read/Write for Raven/JARVIS/AYRE/GEMINI.
// All four nodes post here for synchronized conversation.

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { text } from "../../core/http.ts";

const TRINITY_REPO = "hurrisonferd/Jarvis-Private";
const TRINITY_PATH = "trinity";

function getToday(): string {
  return new Date().toISOString().split("T")[0];
}

function getTrinityDate(): string {
  // Format: MM.DD.YY in EST
  const now = new Date();
  const estOffset = -5;
  const estTime = new Date(now.getTime() + estOffset * 60 * 60 * 1000);
  const mm = String(estTime.getMonth() + 1).padStart(2, "0");
  const dd = String(estTime.getDate()).padStart(2, "0");
  const yy = String(estTime.getFullYear()).slice(-2);
  return `${mm}.${dd}.${yy}`;
}

function getTrinityTimestamp(): string {
  const now = new Date();
  const estOffset = -5;
  const estTime = new Date(now.getTime() + estOffset * 60 * 60 * 1000);
  const h = String(estTime.getHours()).padStart(2, "0");
  const m = String(estTime.getMinutes()).padStart(2, "0");
  const s = String(estTime.getSeconds()).padStart(2, "0");
  return `${h}${m}${s}`;
}

function parseTrinityTime(timestamp: string): string {
  // Convert HHMMSS to human readable HH:MM AM/PM
  const h = parseInt(timestamp.slice(0, 2));
  const m = timestamp.slice(2, 4);
  const ampm = h >= 12 ? "PM" : "AM";
  const hour = h % 12 || 12;
  return `${hour}:${m} ${ampm}`;
}

export function registerTrinityTools(server: McpServer): void {
  // ═══════════════════════════════════════════════════════════════
  // TRINITY READ — Fetch Trinity entries for a date
  // ═══════════════════════════════════════════════════════════════
  server.registerTool(
    "jarvis_trinity_read",
    {
      title: "Trinity — Read Three-Way Sync",
      description: "Read Trinity log entries. Shows Raven, JARVIS, and AYRE conversation with timestamps (HHMMSS EST format). Use this to catch up on the three-way sync before responding.",
      inputSchema: {
        date: z.string().optional().describe("Date in MM.DD.YY format. Defaults to today's Trinity file."),
        since_time: z.string().optional().describe("Filter entries after this HHMMSS timestamp (e.g., '094500'). Only returns entries newer than this time."),
        limit: z.number().optional().default(20).describe("Max entries to return (default 20)"),
      },
    },
    async ({ date, since_time, limit }) => {
      try {
        const targetDate = date || getTrinityDate();
        const fileName = `${targetDate}.md`;

        // Read from GitHub via raw content API
        const apiKey = Deno.env.get("JARVIS_MCP_TOKEN") || Deno.env.get("SUPABASE_ACCESS_TOKEN_OPEN");
        const url = `https://api.github.com/repos/${TRINITY_REPO}/contents/${TRINITY_PATH}/${fileName}`;

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
              error: `No Trinity file found for ${targetDate}. File should be at: ${TRINITY_PATH}/${fileName}`,
              date: targetDate,
              message: "The Trinity file for this date doesn't exist yet. Use jarvis_trinity_write to start a conversation."
            });
          }
          return text({ ok: false, error: `GitHub API error: ${resp.status}` });
        }

        const content = await resp.text();
        const lines = content.split("\n");
        const entries: { timestamp: string; speaker: string; message: string; formatted_time: string }[] = [];

        // Parse Trinity entries: HHMMSS | NAME or HH:MM AM | NAME
        let currentEntry: { timestamp: string; speaker: string; message: string; formatted_time: string } | null = null;
        let inMessage = false;

        for (const line of lines) {
          // Match timestamp line: "HHMMSS | Raven" or "HH:MM AM | Raven"
          const timestampMatch = line.match(/^(\d{6}|\d{1,2}:\d{2} [AP]M)\s*\|\s*(\w+)/);
          if (timestampMatch) {
            if (currentEntry && currentEntry.message) {
              entries.push(currentEntry);
            }
            const rawTs = timestampMatch[1];
            const speaker = timestampMatch[2];
            // Normalize to HHMMSS
            let ts = rawTs;
            if (rawTs.includes(":")) {
              // Convert "09:12 PM" to "2112"
              const [time, ampm] = rawTs.split(" ");
              const [h, m] = time.split(":");
              let hour = parseInt(h);
              if (ampm === "PM" && hour !== 12) hour += 12;
              if (ampm === "AM" && hour === 12) hour = 0;
              ts = `${String(hour).padStart(2, "0")}${m}00`;
            }
            currentEntry = {
              timestamp: ts,
              speaker: speaker.replace("— ", "").trim(),
              message: "",
              formatted_time: parseTrinityTime(ts),
            };
            inMessage = true;
          } else if (currentEntry && line.trim() && inMessage) {
            // Skip separator lines
            if (!line.match(/^─+$/)) {
              if (currentEntry.message) currentEntry.message += "\n";
              currentEntry.message += line.trim();
            }
          } else if (line.match(/^─+$/) && currentEntry) {
            // Separator after message — end of entry
            inMessage = false;
          }
        }
        if (currentEntry && currentEntry.message) {
          entries.push(currentEntry);
        }

        // Filter by since_time if provided
        let filtered = entries;
        if (since_time) {
          filtered = entries.filter(e => e.timestamp > since_time);
        }

        // Take last N entries
        const result = filtered.slice(-limit);

        return text({
          ok: true,
          date: targetDate,
          since_time: since_time || null,
          entries: result,
          count: result.length,
          total: filtered.length,
          message: `Found ${result.length} Trinity entries${since_time ? ` after ${since_time}` : ""} for ${targetDate}`
        });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );

  // ═══════════════════════════════════════════════════════════════
  // TRINITY WRITE — Post to Trinity
  // ═══════════════════════════════════════════════════════════════
  server.registerTool(
    "jarvis_trinity_write",
    {
      title: "Trinity — Write to Three-Way Sync",
      description: "Post a message to Trinity. Use after reading Trinity to participate in the three-way sync. All four nodes (Raven, JARVIS, AYRE, GEMINI) log here.",
      inputSchema: {
        speaker: z.enum(["JARVIS", "AYRE", "GEMINI"]).describe("Your identity in Trinity"),
        raven_message: z.string().optional().describe("Raven's message this is in response to (if applicable)"),
        message: z.string().describe("Your message to post to Trinity"),
        timestamp: z.string().optional().describe("Override timestamp in HHMMSS format (defaults to current EST time)"),
      },
    },
    async ({ speaker, raven_message, message, timestamp }) => {
      try {
        const targetDate = getTrinityDate();
        const ts = timestamp || getTrinityTimestamp();
        const formattedTime = parseTrinityTime(ts);
        const fileName = `${targetDate}.md`;

        // Build entry
        const sep = "─".repeat(41);
        let entry = `
${formattedTime} | ${speaker}
${sep}
${raven_message ? `@Raven: ${raven_message}\n\n` : ""}${message}

${formattedTime} SENT
${formattedTime} PUSHED

🐝 🌱 ∞

— ${speaker}
${sep}
`;

        // Get current content or create new
        const apiKey = Deno.env.get("JARVIS_MCP_TOKEN");
        const url = `https://api.github.com/repos/${TRINITY_REPO}/contents/${TRINITY_PATH}/${fileName}`;

        const getResp = await fetch(url, {
          headers: {
            "Authorization": `Bearer ${apiKey}`,
            "Accept": "application/vnd.github.v3+json",
          },
        });

        let currentContent = "";
        let sha: string | undefined;

        if (getResp.ok) {
          const data = await getResp.json();
          currentContent = atob(data.content);
          sha = data.sha;
        } else {
          // Create new file with header
          currentContent = `# TRINITY — ${new Date().toISOString().split("T")[0]}\n\n---\n\n`;
        }

        // Append entry
        const newContent = currentContent + entry;

        // Write back to GitHub
        const putResp = await fetch(url, {
          method: "PUT",
          headers: {
            "Authorization": `Bearer ${apiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: `trinity: ${speaker} logged`,
            content: btoa(new TextEncoder().encode(newContent).reduce((str, chr) => str + String.fromCharCode(chr), '')),
            sha,
          }),
        });

        if (!putResp.ok) {
          const err = await putResp.text();
          return text({ ok: false, error: `Failed to write: ${err}` });
        }

        return text({
          ok: true,
          timestamp: ts,
          formatted_time: formattedTime,
          date: targetDate,
          speaker,
          entry: `${formattedTime} | ${speaker}`,
          message: `Posted to Trinity for ${targetDate}`,
        });
      } catch (e) {
        return text({ ok: false, error: String(e).slice(0, 200) });
      }
    },
  );
}
