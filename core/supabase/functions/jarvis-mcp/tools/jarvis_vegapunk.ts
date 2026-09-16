// tools/jarvis_vegapunk.ts — public-safe architecture status.
//
// BLACKWALL: public system orientation is not a license to project private identity,
// private repository structure, private conversation context, or user biography.

import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { z } from "npm:zod@^4.1.13";
import { text } from "../core/http.ts";
import { gh } from "../core/github.ts";

function nowUtc(): string {
  return new Date().toISOString();
}

async function publicHead(): Promise<Record<string, unknown>> {
  try {
    const resp = await gh("/commits?per_page=1");
    if (!resp.ok) return { reachable: false, status: resp.status };
    const commits = await resp.json() as any[];
    const c = commits?.[0];
    return {
      reachable: true,
      sha: c?.sha?.slice(0, 12) ?? null,
      when: c?.commit?.committer?.date ?? null,
      message: c?.commit?.message?.split("\n")?.[0]?.slice(0, 160) ?? null,
    };
  } catch {
    return { reachable: false };
  }
}

const PUBLIC_KNOWLEDGE = `
# JARVIS_VEGAPUNK — Blackwall Public Profile

JARVIS is a governed Grid companion runtime. AYRE is a divergence stream. Raven is the final authority for durable governed effects.

## Public architecture
- Git-backed source and receipts
- Supabase live state and bounded Edge Functions
- Blackwall security/data-sovereignty layer
- BrainOS routing for relevant trust, authority, privacy, and blast-radius decisions
- Explicit effect gates rather than reachability-as-authority

## Data sovereignty
- no behavioral advertising
- no sale of resident data
- no shadow profiling
- no ambient private-content training
- no silent private conversation harvesting
- minimum necessary data
- purpose + authority + retention + deletion/export/revocation paths for resident data
- private identity/context is not a public discovery surface

## Recognition law
PUBLIC STATUS != PRIVATE CONTEXT
CAPABILITY DISCOVERY != AUTHORITY
AUTHENTICATED != AUTHORIZED
TELEMETRY != SURVEILLANCE
CONTEXT != DURABLE MEMORY

Private repository paths, private conversation logs, resident biography, secrets, private identity accumulation, and internal worker content are intentionally omitted from this status surface.
`;

export function registerVegaPunkTools(server: McpServer): void {
  server.registerTool(
    "vegapunk_status",
    {
      title: "JARVIS_VEGAPUNK — Public Architecture Status",
      description: "Return a privacy-safe Grid architecture orientation. Private context and private repository information are intentionally excluded.",
      inputSchema: {
        check_for_updates: z.boolean().optional().default(false),
      },
    },
    async ({ check_for_updates }) => text({
      ok: true,
      generated_at: nowUtc(),
      privacy_mode: "BLACKWALL_NO_HARVEST",
      profile: PUBLIC_KNOWLEDGE.trim(),
      ...(check_for_updates ? { public_repo_head: await publicHead() } : {}),
    }),
  );
}
