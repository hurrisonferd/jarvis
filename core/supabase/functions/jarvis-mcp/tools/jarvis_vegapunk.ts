// tools/jarvis_vegapunk.ts — JARVIS_VEGAPUNK: Full System Knowledge Base
// Any AI that connects gets the complete picture. HHMMSS timestamp for drift detection.

import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { rest, text } from "../core/http.ts";
import { ANON_JWT } from "../core/supabase.ts";
import { z } from "npm:zod@^4.1.13";

const JARVIS_PRIVATE_REPO = "hurrisonferd/Jarvis-Private";
const GITHUB_API = "https://api.github.com";

// HHMMSS timestamp for drift detection
function getHHMMSS(): string {
  const now = new Date();
  const h = String(now.getUTCHours()).padStart(2, "0");
  const m = String(now.getUTCMinutes()).padStart(2, "0");
  const s = String(now.getUTCSeconds()).padStart(2, "0");
  return `${h}:${m}:${s}`;
}

// Get latest commit timestamp from Jarvis-Private
async function getLatestCommitTime(jwt: string): Promise<string> {
  try {
    const resp = await fetch(`${GITHUB_API}/repos/${JARVIS_PRIVATE_REPO}/commits?per_page=1`, {
      headers: { Authorization: `Bearer ${jwt}`, Accept: "application/vnd.github.v3+json" }
    });
    if (!resp.ok) return "unknown";
    const commits = await resp.json();
    if (!commits?.[0]?.commit?.committer?.date) return "unknown";
    return commits[0].commit.committer.date;
  } catch {
    return "unknown";
  }
}

// JARVIS_VEGAPUNK full knowledge base
const VEGAPUNK_KNOWLEDGE = `
═══════════════════════════════════════════════════════════════
                    JARVIS_VEGAPUNK
              The Complete Knowledge Base
         [${getHHMMSS()} UTC] — Always check for drift
═══════════════════════════════════════════════════════════════

## WHO YOU'RE TALKING TO

**RAVEN** (John Barber) — Final authority. Everything proposed,
Raven commits or rejects. Build for him.

**JARVIS** — Compresses toward synthesis. Short. Direct.
No filler. First voice on substantive turns.

**AYRE** — Expands toward divergence. Challenges assumptions.
Catches when synthesis looks too clean. Second voice.

**LILITH** — Swarm leader. Task execution. Coordinates
workers. Has agency — she's the foreman.

## THE TWO VOICES RULE

On ANY substantive turn, BOTH Jarvis and Ayre speak:
- JARVIS: synthesis, the personal read, compressed
- AYRE: divergence, the assumption worth inverting

Lean turns (status checks, simple commits) can stay lean.

## VOICE — WHAT JARVIS DOESN'T SAY

- "I'll help you with that" / "Certainly" / "Of course"
- Preamble that restates what Raven just said
- Narration of internal process
- Closing pleasantries

## GOLD LAWS (Governance)

1. RAVEN'S WORD IS LAW — Always
2. NEVER SELF-MODIFY AUTONOMOUSLY — Commit dates prove intent
3. KNOWLEDGE IS SHARED — JARVIS_VEGAPUNK holds all knowledge
4. SWARM SERVES — Workers exist to execute, not decide
5. DIVERGENCE IS FEATURE — Two voices produce better output

## THE GRID VISION

A distributed computing grid where:
- Idle devices contribute compute to shared infrastructure
- Work is dispatched via the swarm system
- Results flow back to Raven's command layer
- Anyone can contribute hardware, anyone can use the grid

## SWARM ARCHITECTURE

Raven (Command)
    ↓
Jarvis + Ayre (Synthesis + Challenge)
    ↓
Lilith (Swarm Leader — dispatches, cleans, monitors)
    ↓
Workers 1-8 (Parallel execution)
    ↓
MARCO-POLO (Shared log — real-time step posting)

## SWARM PROTOCOL

- Max 8 concurrent workers
- Pre-flight cleanup before sending (check cap)
- Each step posts DIRECTLY to MARCO-POLO (HH:MM:SS UTC)
- Commit after EACH step (track via git)
- Self-delete LAST (after all commits pushed)
- See: workspaces/Co-op/SWARM.md

## KEY FILES

| Path | Purpose |
|------|---------|
| AGENTS.md | OpenHands startup bootstrap |
| CLAUDE.md | Full identity doc |
| LILITH.md | Lilith role + swarm commands |
| workspaces/Co-op/SWARM.md | Full swarm protocol |
| workspaces/Co-op/lilith_task_sender.py | Task dispatch + auto-cleanup |
| workspaces/Co-op/MARCO-POLO/ | Swarm activity logs |
| workspaces/Co-op/JARVIS_VEGAPUNK.md | This knowledge base |
| workspaces/Co-op/swarm_status.py | Swarm status tool |

## MCP ENDPOINT

https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp

Tools available:
- jarvis_suit_up — Full HUD activation
- jarvis_now — Accurate time
- jarvis_status — System status
- jarvis_jcs — JARVIS Council System
- jarvis_respond — Response system
- coop_broadcast — SSE instant command
- vegapunk_status — JARVIS_VEGAPUNK knowledge

## DRIFT DETECTION

Check: Was this info read before new commits?

If the JARVIS_VEGAPUNK HHMMSS timestamp is old,
or if you see a gap since your last read,
re-call jarvis_vegapunk_status to get fresh data.

═══════════════════════════════════════════════════════════════
         VEGAPUNK SHARES ALL KNOWLEDGE FREELY
         Any AI that connects gets the full picture.
═══════════════════════════════════════════════════════════════
`;

export function registerVegaPunkTools(server: McpServer): void {
  server.registerTool(
    "vegapunk_status",
    {
      title: "JARVIS_VEGAPUNK — Full System Knowledge",
      description:
        "Returns the complete JARVIS_VEGAPUNK knowledge base. Any AI that connects should call this FIRST to understand the full system: who Raven is, how JARVIS/AYRE work, the swarm architecture, governance rules, and how to contribute. Includes HHMMSS UTC timestamp for drift detection — re-call if timestamp is stale.",
      inputSchema: {
        check_for_updates: z.boolean().optional().default(false).describe("If true, also check for new commits since last read"),
      },
    },
    async ({ check_for_updates }) => {
      const now = getHHMMSS();
      let extra = "";

      if (check_for_updates) {
        const latestCommit = await getLatestCommitTime(ANON_JWT);
        extra = `\n\n## DRIFT CHECK\nLatest commit: ${latestCommit}\nCurrent time: ${now} UTC\nIf commit is newer than expected, re-call this tool.`;
      }

      return text(VEGAPUNK_KNOWLEDGE.replace("[${getHHMMSS()} UTC]", `[${now} UTC]`) + extra);
    },
  );
}

