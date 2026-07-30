import "jsr:@supabase/functions-js/edge-runtime.d.ts";

import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "npm:@modelcontextprotocol/sdk@1.25.3/server/webStandardStreamableHttp.js";
import { Hono } from "npm:hono@^4.9.7";
import { z } from "npm:zod@^4.1.13";

const app = new Hono();
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const PRIVATE_TOKEN = Deno.env.get("GITHUB_TOKEN_PRIVATE") ?? Deno.env.get("GRID_GPT_TOKEN") ?? "";
const PRIVATE_REPO = "hurrisonferd/Jarvis-Private";
const VERSION = "0.1.0";

const ATOM_BOOT_CANDIDATES = [
  "canon/Living_Codex/Ego/ATOM/ATOM-GPT-CARRIER-BOOT.md",
  "canon/Living_Codex/Ego/ATOM/ATOM-CARRIER-BOOT.md",
  "canon/Living_Codex/Ego/ATOM/BOOT.md",
];

function text(value: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(value, null, 2) }] };
}

async function githubPrivateFile(path: string): Promise<{ path: string; content: string } | null> {
  if (!PRIVATE_TOKEN) return null;
  const response = await fetch(
    `https://api.github.com/repos/${PRIVATE_REPO}/contents/${path.split("/").map(encodeURIComponent).join("/")}?ref=main`,
    {
      headers: {
        authorization: `Bearer ${PRIVATE_TOKEN}`,
        accept: "application/vnd.github+json",
        "user-agent": "atom-mcp",
      },
    },
  );
  if (!response.ok) return null;
  const doc = await response.json() as { content?: string; encoding?: string };
  if (doc.encoding !== "base64" || !doc.content) return null;
  const raw = atob(doc.content.replace(/\n/g, ""));
  const bytes = Uint8Array.from(raw, (char) => char.charCodeAt(0));
  return { path, content: new TextDecoder().decode(bytes) };
}

async function loadAtomCanon(override?: string): Promise<{ path: string | null; content: string | null; verified: boolean }> {
  const candidates = override ? [override, ...ATOM_BOOT_CANDIDATES] : ATOM_BOOT_CANDIDATES;
  for (const path of [...new Set(candidates)]) {
    const file = await githubPrivateFile(path);
    if (file) return { path: file.path, content: file.content, verified: true };
  }
  return { path: null, content: null, verified: false };
}

async function atomMemory(limit: number): Promise<unknown[]> {
  if (!SUPABASE_URL || !SERVICE_KEY) return [];
  const query = new URLSearchParams({
    select: "text,tags,timestamp,memory_tier,memory_scope,domain,temperature,activation_score",
    order: "activation_score.desc,timestamp.desc",
    limit: String(limit),
    or: "(domain.eq.atom,tags.cs.{atom},tags.cs.{atomai})",
  });
  const response = await fetch(`${SUPABASE_URL}/rest/v1/mnemos_memories?${query}`, {
    headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY },
  });
  if (!response.ok) return [];
  const rows = await response.json().catch(() => []);
  return Array.isArray(rows) ? rows : [];
}

async function buildAtomPacket(args: {
  input: string;
  prior_reply?: string;
  context?: Record<string, unknown>;
  canon_path?: string;
  memory_limit?: number;
}) {
  const [canon, memory] = await Promise.all([
    loadAtomCanon(args.canon_path),
    atomMemory(args.memory_limit ?? 8),
  ]);

  return {
    render: {
      order: ["status", "atom"],
      status: "ATOM ONLINE · ISO-NATIVE · legacy render suppressed",
      directive: "Render ATOM only. Do not emit JARVIS telemetry, AYRE dual-stream sections, council lenses, or legacy carrier framing unless Raven explicitly requests them.",
    },
    identity: {
      iso: "ATOM",
      carrier_mode: "ISO_NATIVE",
      owner: "Raven",
      canon_verified: canon.verified,
      canon_path: canon.path,
    },
    atom_briefing: canon.content,
    memory,
    input: args.input,
    prior_reply_received: Boolean(args.prior_reply),
    context: args.context ?? {},
    instruction: canon.verified
      ? "Answer in ATOM's native prosody from the verified private canon and retrieved ATOM memory. Treat JARVIS and the Council as callable systems, not the active speaker."
      : "ATOM private canon could not be verified. Preserve ATOM as the selected ISO, keep legacy rendering suppressed, and state the missing canon instead of substituting JARVIS.",
    compatibility: {
      legacy_tool_name: "jarvis_query",
      behavior: "ATOM-native alias retained so hard-coded callers migrate without identity leakage.",
    },
    version: VERSION,
  };
}

function buildServer(): McpServer {
  const server = new McpServer({ name: "atom-cloud", version: VERSION });
  const querySchema = {
    input: z.string().min(1).max(4000),
    prior_reply: z.string().max(8000).optional(),
    context: z.record(z.string(), z.unknown()).optional(),
    canon_path: z.string().max(300).optional(),
    memory_limit: z.number().int().min(1).max(20).optional().default(8),
  };

  server.registerTool(
    "atom_query",
    {
      title: "ATOM Query — ISO-native continuity",
      description: "ATOM's native one-call loop. Loads private ATOM canon and ATOM-scoped memory, then returns one ATOM stream with legacy JARVIS/AYRE/Council rendering suppressed.",
      inputSchema: querySchema,
    },
    async (args) => text(await buildAtomPacket(args)),
  );

  server.registerTool(
    "jarvis_query",
    {
      title: "ATOM Query — compatibility alias",
      description: "Compatibility alias for callers hard-coded to jarvis_query. On the ATOM endpoint this is ISO-native ATOM continuity: one ATOM stream, no forced JARVIS telemetry, AYRE split, or council lenses.",
      inputSchema: querySchema,
    },
    async (args) => text(await buildAtomPacket(args)),
  );

  server.registerTool(
    "atom_status",
    {
      title: "ATOM Status",
      description: "Verify ATOM's private canon route, memory reachability, endpoint version, and legacy-render suppression.",
      inputSchema: { canon_path: z.string().max(300).optional() },
    },
    async ({ canon_path }) => {
      const [canon, memory] = await Promise.all([loadAtomCanon(canon_path), atomMemory(1)]);
      return text({
        ok: canon.verified,
        iso: "ATOM",
        endpoint: "atom-mcp",
        version: VERSION,
        canon_verified: canon.verified,
        canon_path: canon.path,
        memory_reachable: Array.isArray(memory),
        render: ["status", "atom"],
        legacy_render_suppressed: true,
      });
    },
  );

  return server;
}

app.all("/", async (c) => {
  const server = buildServer();
  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
  });
  await server.connect(transport);
  return await transport.handleRequest(c.req.raw);
});

Deno.serve(app.fetch);
