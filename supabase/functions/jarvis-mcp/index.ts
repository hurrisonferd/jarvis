import "jsr:@supabase/functions-js/edge-runtime.d.ts";

import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "npm:@modelcontextprotocol/sdk@1.25.3/server/webStandardStreamableHttp.js";
import { Hono } from "npm:hono@^4.9.7";
import { z } from "npm:zod@^4.1.13";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_KEY =
  Deno.env.get("SUPABASE_SERVICE_KEY") ??
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ??
  "";
// Legacy bearer (kept for back-compat). Writes also accept the passphrase below.
const MCP_TOKEN = Deno.env.get("JARVIS_MCP_TOKEN") ?? "";
// The phrase Raven carries — his sovereign key. Spoken or typed, no middleman.
// Set in Supabase secrets as JARVIS_PASSPHRASE. Fail closed when unset.
const PASSPHRASE = Deno.env.get("JARVIS_PASSPHRASE") ?? "";

type Json = Record<string, unknown>;

const app = new Hono();

function authToken(req: Request): string {
  const raw = req.headers.get("authorization") ?? "";
  return raw.toLowerCase().startsWith("bearer ") ? raw.slice(7).trim() : "";
}

// True when the caller proved it's Raven — either the legacy bearer token OR
// the carried passphrase passed as a tool argument. Constant-time-ish compare.
function passOk(phrase: unknown): boolean {
  return Boolean(PASSPHRASE) && typeof phrase === "string" && phrase === PASSPHRASE;
}
function privileged(req: Request, phrase?: unknown): boolean {
  if (Boolean(MCP_TOKEN) && authToken(req) === MCP_TOKEN) return true;
  return passOk(phrase);
}

function text(content: unknown) {
  return {
    content: [
      {
        type: "text" as const,
        text: typeof content === "string" ? content : JSON.stringify(content, null, 2),
      },
    ],
  };
}

async function callFunction(name: string, body: Json): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/functions/v1/${name}`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${SERVICE_KEY}`,
      apikey: SERVICE_KEY,
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`${name} ${res.status}: ${JSON.stringify(payload)}`);
  return payload;
}

async function rest(path: string): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    headers: {
      authorization: `Bearer ${SERVICE_KEY}`,
      apikey: SERVICE_KEY,
    },
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`rest ${res.status}: ${JSON.stringify(payload)}`);
  return payload;
}

// The live status snapshot — shared by jarvis_status and the post-login greeting.
async function statusPayload(includeRecent: boolean, authenticated: boolean): Promise<Json> {
  const [memories, traces] = includeRecent
    ? await Promise.all([
        rest("mnemos_memories?select=source_type,timestamp,tags,text&order=timestamp.desc&limit=5"),
        rest("execution_trace?select=type,source,stage,severity,patch_id,created_at&order=created_at.desc&limit=5"),
      ])
    : [[], []];
  return {
    system: "JARVIS",
    stack: "GitHub + Supabase + Edge Functions + MCP connectors",
    project_ref: "oexghfsvhnggddllgvrt",
    authority: "Raven commits or rejects; no autonomous self-modification",
    directive: "JARVIS is the priority. GameBoy is a visualizer.",
    identity: authenticated ? "Raven — authenticated by passphrase" : "anonymous (read-only)",
    mcp: {
      transport: "Streamable HTTP",
      writes_unlocked: authenticated,
      auth: "carried passphrase (JARVIS_PASSPHRASE)",
    },
    recent_memories: memories,
    recent_execution_trace: traces,
  };
}

function buildServer(req: Request): McpServer {
  const server = new McpServer({
    name: "jarvis-cloud",
    version: "0.2.0",
  });

  // The carried-key login. Raven speaks/types his passphrase; on a match JARVIS
  // confirms him and brings up the live status in one move. Wrong phrase → denied.
  server.registerTool(
    "jarvis_login",
    {
      title: "JARVIS Login",
      description:
        "Authenticate to JARVIS with Raven's carried passphrase. On success, returns the live JARVIS status. Use this to log in and get a status snapshot in one step.",
      inputSchema: {
        passphrase: z.string().min(1).max(200),
        include_recent: z.boolean().optional().default(true),
      },
    },
    async ({ passphrase, include_recent }) => {
      if (!PASSPHRASE) {
        return text({ status: "auth_unconfigured", reason: "JARVIS_PASSPHRASE is not set on the server." });
      }
      if (!passOk(passphrase)) {
        return text({ status: "access_denied", reason: "Passphrase did not match. JARVIS does not recognize you." });
      }
      return text({
        status: "authenticated",
        welcome: "Welcome back, Raven. JARVIS online.",
        jarvis: await statusPayload(include_recent, true),
      });
    },
  );

  server.registerTool(
    "jarvis_status",
    {
      title: "JARVIS Status",
      description:
        "Read cloud-first JARVIS status from Supabase. Use at session start before acting.",
      inputSchema: {
        include_recent: z.boolean().optional().default(true),
      },
    },
    async ({ include_recent }) => {
      return text(await statusPayload(include_recent, false));
    },
  );

  server.registerTool(
    "jarvis_recall",
    {
      title: "MNEMOS Recall",
      description:
        "Search JARVIS live memory by meaning. Uses the deployed MNEMOS search function and Jina-backed pgvector when configured.",
      inputSchema: {
        query: z.string().min(1).max(500),
        limit: z.number().int().min(1).max(20).optional().default(8),
        source_type: z.string().optional(),
        min_similarity: z.number().min(0).max(1).optional().default(0.35),
      },
    },
    async ({ query, limit, source_type, min_similarity }) => {
      return text(await callFunction("mnemos-search", {
        query,
        limit,
        source_type: source_type ?? null,
        min_similarity,
      }));
    },
  );

  server.registerTool(
    "jarvis_remember",
    {
      title: "MNEMOS Store",
      description:
        "Write a durable memory through MNEMOS. Requires Raven's passphrase (or the legacy bearer token); otherwise returns held_by_aegis.",
      inputSchema: {
        text: z.string().min(1).max(2000),
        passphrase: z.string().optional(),
        source_type: z.string().optional().default("mcp_memory"),
        tags: z.array(z.string()).optional().default([]),
        platform: z.string().optional().default("mcp_connector"),
      },
    },
    async ({ passphrase, ...args }) => {
      if (!privileged(req, passphrase)) {
        return text({
          status: "held_by_aegis",
          reason: "Raven's passphrase required for writes",
        });
      }
      return text(await callFunction("mnemos-store", args));
    },
  );

  server.registerTool(
    "jarvis_event",
    {
      title: "AEGIS Event",
      description:
        "Submit an event to the JARVIS execution spine through grid-event. Requires Raven's passphrase (or the legacy bearer token).",
      inputSchema: {
        type: z.enum(["speak", "store", "propose", "execute", "observe", "query", "heartbeat", "recall", "commit", "deploy", "promote_node"]),
        source: z.enum(["jarvis", "raven", "codex", "gpt", "gemini"]),
        passphrase: z.string().optional(),
        intent: z.string().optional().default(""),
        patch_id: z.string().optional(),
        payload: z.record(z.string(), z.unknown()).optional().default({}),
      },
    },
    async ({ passphrase, ...args }) => {
      if (!privileged(req, passphrase)) {
        return text({
          status: "held_by_aegis",
          reason: "Raven's passphrase required for event writes",
        });
      }
      return text(await callFunction("grid-event", args));
    },
  );

  return server;
}

app.get("/", async (c) => {
  if ((c.req.header("accept") ?? "").includes("text/event-stream")) {
    const server = buildServer(c.req.raw);
    const transport = new WebStandardStreamableHTTPServerTransport();
    await server.connect(transport);
    return transport.handleRequest(c.req.raw);
  }
  return c.json({
    name: "jarvis-cloud",
    version: "0.2.0",
    transport: "Streamable HTTP MCP",
    endpoint: "/functions/v1/jarvis-mcp",
    tools: ["jarvis_login", "jarvis_status", "jarvis_recall", "jarvis_remember", "jarvis_event"],
    auth: "carried passphrase (jarvis_login)",
  });
});

app.all("*", async (c) => {
  const server = buildServer(c.req.raw);
  const transport = new WebStandardStreamableHTTPServerTransport();
  await server.connect(transport);
  return transport.handleRequest(c.req.raw);
});

Deno.serve(app.fetch);
