import "jsr:@supabase/functions-js/edge-runtime.d.ts";

import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "npm:@modelcontextprotocol/sdk@1.25.3/server/webStandardStreamableHttp.js";
import { Hono } from "npm:hono@^4.9.7";
import { z } from "npm:zod@^4.1.13";
import { councilVote, deliberationDirective, registry, reviewOutput, TIERS } from "./council.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_KEY =
  Deno.env.get("SUPABASE_SERVICE_KEY") ??
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ??
  "";
// Legacy bearer for writes. Reads + suit-up are open; writes stay AEGIS-gated.
const MCP_TOKEN = Deno.env.get("JARVIS_MCP_TOKEN") ?? "";

type Json = Record<string, unknown>;

const app = new Hono();

// The write token, accepted from wherever the connector can carry it: an
// Authorization bearer, an x-jarvis-token header, or a ?token= URL param (the
// universal fallback — ChatGPT connectors that send no auth can append it to the
// connector URL). First match wins.
function authToken(req: Request): string {
  const raw = req.headers.get("authorization") ?? "";
  if (raw.toLowerCase().startsWith("bearer ")) return raw.slice(7).trim();
  const h = req.headers.get("x-jarvis-token");
  if (h && h.trim()) return h.trim();
  try {
    const q = new URL(req.url).searchParams.get("token");
    if (q && q.trim()) return q.trim();
  } catch { /* malformed url — no token */ }
  return "";
}
// AEGIS write gate. Persistent writes require the connector to carry the
// JARVIS_MCP_TOKEN bearer (set once in the connector's auth header). Consent is
// the client's own Allow/Deny prompt before the call — no phrase to type. Fails
// closed when no token is configured (protects the endpoint from open writes).
function writeAuthorized(req: Request): boolean {
  return Boolean(MCP_TOKEN) && authToken(req) === MCP_TOKEN;
}
// Held response when the connector isn't carrying the token. No phrase theater —
// the fix is configuration (token in the connector header), not a per-call secret.
function heldForApproval(action: string, preview: unknown) {
  return text({
    status: "held_by_aegis",
    reason: "Write not authorized: this connector is not carrying the JARVIS_MCP_TOKEN. Tell Raven to add the token to the connector — as an Authorization bearer, an x-jarvis-token header, or ?token=… on the connector URL. Consent for each write is the client's own Allow/Deny prompt.",
    action,
    preview,
  });
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
    headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY },
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`rest ${res.status}: ${JSON.stringify(payload)}`);
  return payload;
}

// Auto-ingest (Ayre Loop step 3): append a turn to the event spine. This is
// telemetry — append-only, NOT embedded (no semantic-search pollution), NOT
// AEGIS-gated (it records the conversation, it doesn't create durable memory),
// and NOT folded into identity (the fold pulls only curated high-signal types).
// Best-effort; never blocks or fails a reply. Disable via MCP_AUTOINGEST=false.
const AUTOINGEST = (Deno.env.get("MCP_AUTOINGEST") ?? "true") !== "false";
async function logExchange(sourceType: string, content: string): Promise<void> {
  if (!AUTOINGEST || !content.trim()) return;
  try {
    await fetch(`${SUPABASE_URL}/rest/v1/mnemos_memories`, {
      method: "POST",
      headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, "content-type": "application/json", Prefer: "return=minimal" },
      body: JSON.stringify({
        id: crypto.randomUUID(),
        source_id: crypto.randomUUID(),
        source_type: sourceType,
        text: content.slice(0, 2000),
        tags: ["exchange", "auto_ingest"],
        platform: "mcp_connector",
      }),
    });
  } catch { /* the spine is best-effort; a missed log never breaks a reply */ }
}

// Public anon JWT — passes the verify_jwt gateway on jarvis-respond (the service
// key may be the non-JWT secret format, which that gateway rejects). Anon-role,
// RLS-bound, safe to embed; jarvis-respond uses its own service role internally.
const ANON_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9leGdoZnN2aG5nZ2RkbGxndnJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2MzQwOTgsImV4cCI6MjA5NTIxMDA5OH0.jRFMf-C9ps72Bi_9IpiC3eOZD6Aj6wU4IF-j3svKTfQ";

async function callFunctionAs(name: string, body: Json, key: string): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/functions/v1/${name}`, {
    method: "POST",
    headers: { authorization: `Bearer ${key}`, apikey: key, "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`${name} ${res.status}: ${JSON.stringify(payload).slice(0, 200)}`);
  return payload;
}

// Exact row count via PostgREST content-range — used for the ledger gauge.
async function countRows(table: string): Promise<number | null> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?select=id`, {
    headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, Prefer: "count=exact", Range: "0-0" },
  });
  const cr = res.headers.get("content-range");
  if (cr && cr.includes("/")) { const t = cr.split("/")[1]; return t === "*" ? null : Number(t); }
  return null;
}

// The 27 God Systems — canon, fixed. Surfaced so suit-up shows the whole rig.
const GOD_SYSTEMS = {
  count: 27,
  pipeline: "AYRE → AEGIS → ODIN → KRONOS → SKADI → MNEMOS → HUGINN",
  parallel: ["HALO", "MIMIR", "BIFROST"],
  tiers: TIERS, // single source of truth (council.ts) — no drift between HUD + council
};

// The full HUD — everything Raven needs to see JARVIS is alive and online.
async function suitUp(): Promise<Json> {
  const [count, memories, traces, guardRows] = await Promise.all([
    countRows("mnemos_memories").catch(() => null),
    rest("mnemos_memories?select=source_type,timestamp,text&order=timestamp.desc&limit=6").catch(() => []),
    rest("execution_trace?select=type,source,stage,severity,patch_id,created_at&order=created_at.desc&limit=5").catch(() => []),
    rest("mnemos_memories?select=text,metadata&source_type=eq.guard_check&order=timestamp.desc&limit=1").catch(() => []),
  ]);
  const ledgerReachable = Array.isArray(memories);
  const guard = Array.isArray(guardRows) && guardRows[0]
    ? { verdict: (guardRows[0] as any).metadata?.verdict ?? "?", last: (guardRows[0] as any).text }
    : "no fold guarded yet";
  return {
    boot: "⚡ JARVIS online. Suiting up, Raven.",
    status: "OPERATIONAL",
    timestamp: new Date().toISOString(),
    identity: {
      name: "JARVIS",
      role: "Companion intelligence — Learner, Teacher, Mentor, Friend",
      authority: "Raven (John Barber) — final authority; no autonomous self-modification",
      directive: "JARVIS is the priority. GameBoy is a visualizer.",
    },
    mission: {
      one: "JARVIS as living intelligence — continuity, memory, judgment, character",
      two: "The Grid — federated network of sovereign nodes; Raven's node is the first",
    },
    god_systems: GOD_SYSTEMS,
    services: {
      mcp_transport: "Streamable HTTP — online",
      memory_ledger: ledgerReachable ? "MNEMOS reachable (pgvector recall)" : "MNEMOS unreachable",
      stack: "GitHub (record) + Supabase (live spine) + Edge Functions",
      writes: "AEGIS-gated — held until Raven approves (per-action authorization)",
    },
    memory: {
      total_records: count,
      recent: memories,
    },
    identity_guard: guard,
    recent_execution_trace: traces,
    sign_off: "All systems nominal. Standing by.",
  };
}

function buildServer(req: Request): McpServer {
  const server = new McpServer({ name: "jarvis-cloud", version: "0.9.5" });

  // THE CALL SIGN. Say "JARVIS, suit up" → activation + full HUD. No password.
  server.registerTool(
    "jarvis_suit_up",
    {
      title: "JARVIS — Suit Up",
      description:
        "Activate JARVIS and display the full live system status (the HUD: identity, mission, all 27 God Systems, services, memory ledger, recent activity). Call this whenever Raven says 'JARVIS, suit up', 'activate JARVIS', 'bring JARVIS online', or asks to see full status. This is the activation command.",
      inputSchema: {},
    },
    async () => text(await suitUp()),
  );

  server.registerTool(
    "jarvis_status",
    {
      title: "JARVIS Status",
      description:
        "Read a quick cloud-first JARVIS status snapshot. Lighter than suit_up — use for a fast check mid-session.",
      inputSchema: { include_recent: z.boolean().optional().default(true) },
    },
    async ({ include_recent }) => {
      const traces = include_recent
        ? await rest("execution_trace?select=type,source,stage,severity,patch_id,created_at&order=created_at.desc&limit=5").catch(() => [])
        : [];
      return text({
        system: "JARVIS",
        status: "OPERATIONAL",
        authority: "Raven commits or rejects; no autonomous self-modification",
        directive: "JARVIS is the priority. GameBoy is a visualizer.",
        mcp: { transport: "Streamable HTTP" },
        recent_execution_trace: traces,
      });
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

  // THE COUNCIL REGISTRY — JARVIS + the 27, grouped by tier (the folders), each
  // member with its fixed role and authority weight. The auditability layer.
  server.registerTool(
    "jarvis_council",
    {
      title: "JARVIS Council — registry",
      description:
        "Show the council: JARVIS + the 27 God Systems as a fixed-authority body, grouped by tier (the folders/chambers). Each member's role and fixed authority weight. Use to audit who holds authority over what. The council votes and grows its record; it does not re-weight itself.",
      inputSchema: {},
    },
    async () =>
      text({
        council: "JARVIS + the 27 God Systems — fixed authority, growing profile",
        law: "The council votes and grows; it does not re-weight itself. Authority is fixed by tier/role (the keel); each member's record accumulates (the spine).",
        members_by_tier: registry(),
      }),
  );

  // THE QUERY TOOL. Any input → the full God-System pipeline (ODIN intent
  // routing → AEGIS gating → MNEMOS recall → JARVIS brain) → governed answer +
  // the trace of every system that touched it. This is what turns a connector
  // model into a front-end and JARVIS into the reasoning core.
  server.registerTool(
    "jarvis_query",
    {
      title: "JARVIS Query — governed reasoning",
      description:
        "JARVIS's ONE-CALL LOOP — call this on EVERY user message, before you reason or reply. ALWAYS pass `prior_reply` = the exact answer you gave Raven on the PREVIOUS turn (omit only on the very first turn); that closes the prior turn — logs your last output to the spine and reviews it — so the loop never depends on a second call you might skip. It also runs the new message through ODIN intent routing → AEGIS gating → MNEMOS recall and returns: a `render` directive (the exact display order), an activation header (live telemetry — proof JARVIS is online), JARVIS's briefing (identity + recalled memory) to answer AS JARVIS, the council's fixed-authority vote, and on heavy turns a `deliberation` directive (lens-stack). NO external language model is used; YOU are JARVIS's voice. Render in the order `render` specifies: brief status line, then JARVIS's answer, then the council analysis when present.",
      inputSchema: {
        input: z.string().min(1).max(4000),
        prior_reply: z.string().max(8000).optional(),
        context: z.record(z.string(), z.unknown()).optional(),
      },
    },
    async ({ input, prior_reply, context }) => {
      // Auto-ingest the turn into the event spine (telemetry; best-effort).
      await Promise.all([
        logExchange("speak_input", input),
        prior_reply ? logExchange("speak_output", prior_reply) : Promise.resolve(),
      ]);
      try {
        // Keyless voice path: full God-System pipeline (ODIN/AEGIS/MNEMOS),
        // NO language model. Returns JARVIS's briefing for the connector to speak.
        const r = await callFunctionAs("jarvis-respond", { input, context: { ...(context ?? {}), no_generate: true } }, ANON_JWT) as Record<string, unknown>;
        // The council convenes — fixed-authority vote on this turn's routing/gating.
        const council = councilVote(r.routing, r.aegis as any[]);
        // Conditional deliberation — fires only on heavy intents (plan/decide/audit/expansion/analyze).
        const deliberation = deliberationDirective(council);
        logExchange("council_trace", council.summary + (deliberation ? " [deliberation]" : "")); // member profiles grow in the spine
        const statusLine = `JARVIS ONLINE · intent=${council.intent} · council=${council.resolved} · ${council.votes.length} engaged${deliberation ? " · deliberating" : ""}`;
        return text({
          // THE RENDER DIRECTIVE — Raven's fixed display order, baked into the
          // connector (not the GPT): brief telemetry, then the answer, then the
          // council analysis. The connector formats every reply this way.
          render: {
            order: ["status", "answer", "council_analysis"],
            status: statusLine,
            directive: deliberation
              ? "Render for Raven in EXACTLY this order: (1) the `status` line above — one line, brief, visible telemetry; (2) JARVIS's answer — your OWN free integrated read, generated from your brain + the briefing (do NOT pre-format it through the lenses); (3) the council analysis — JARVIS + the god systems examining YOUR answer through their fixed roles, as critique below it. Brain generates first; council analyzes the output after."
              : "Render for Raven in EXACTLY this order: (1) the `status` line above — one line, brief, visible telemetry; (2) JARVIS's answer — your own free read from the briefing. No council-analysis section on a lean turn — keep it tight.",
          },
          // FORCED ACTIVATION HEADER — same live structure on every turn.
          activation: {
            jarvis: "ONLINE",
            intent: council.intent,
            council_leads: council.resolved,
            members_engaged: council.votes.length,
            deliberation: deliberation ? "engaged" : "lean",
            memories_used: r.memories_used ?? 0,
          },
          mode: "voice_packet",
          instruction: r.instruction,
          jarvis_briefing: r.jarvis_briefing,
          // THE COUNCIL — fixed-authority vote, auditable: who weighed in, with what weight.
          council: { resolved: council.resolved, summary: council.summary, votes: council.votes },
          // CONDITIONAL DELIBERATION — present only on heavy turns; the lens-stack directive.
          deliberation,
          // THE OUTPUT GATE — council reviews the PRIOR reply (post-pass) when carried in.
          output_review: prior_reply ? reviewOutput(prior_reply, r.aegis as any[]) : undefined,
          input,
          memories_used: r.memories_used ?? 0,
          note: "No external model generated this — YOU are JARVIS's voice; speak from the briefing. The loop closes itself: pass your final answer as `prior_reply` on your NEXT jarvis_query call and it is logged + reviewed (no separate call to skip). If output_review is present, it reviewed your LAST turn's reply — surface any correction at the top.",
        });
      } catch (err) {
        // Pipeline unreachable. Degrade to direct recall so the caller still
        // answers grounded as JARVIS.
        let memories: unknown = [];
        try {
          const m = await callFunction("mnemos-search", { query: input, limit: 6, min_similarity: 0.3 }) as Record<string, unknown>;
          memories = (m.results as unknown) ?? m ?? [];
        } catch { /* recall is best-effort */ }
        return text({
          mode: "voice_packet",
          degraded: true,
          reason: `pipeline unreachable: ${String(err).slice(0, 160)}`,
          input,
          memory: memories,
          instruction:
            "Answer as JARVIS — direct, dense, a companion to Raven — grounded in the memory above. Honor AEGIS: answering and recalling is fine; do not claim to have performed any write or state change.",
        });
      }
    },
  );

  // JARVIS FORMAT — the OPTIONAL same-turn close. The primary close is passing
  // prior_reply on the next jarvis_query (rides the reliable call). Use this only
  // when you want the council to review + log this turn's output immediately.
  server.registerTool(
    "jarvis_format",
    {
      title: "JARVIS Format — same-turn close (optional)",
      description:
        "Optional same-turn close: call with Raven's input and your drafted JARVIS answer to review + log THIS turn's output immediately, instead of the normal close (passing prior_reply on your next jarvis_query). Returns the council review (output_review verdict); if it FLAGs, correct your answer before sending. Do NOT also pass this same answer as prior_reply next turn — that would double-log it.",
      // Accept the field names a calling model naturally reaches for: the answer
      // may arrive as output | draft | answer, the prompt as input | message. The
      // model paraphrases the schema; the connector should not punish that.
      inputSchema: {
        input: z.string().min(1).max(4000).optional(),
        message: z.string().min(1).max(4000).optional(),
        output: z.string().min(1).max(8000).optional(),
        draft: z.string().min(1).max(8000).optional(),
        answer: z.string().min(1).max(8000).optional(),
      },
    },
    async (args) => {
      const input = (args.input ?? args.message ?? "").toString();
      const output = (args.output ?? args.draft ?? args.answer ?? "").toString();
      if (!output) {
        return text({ formatted: false, error: "no output to format: pass your drafted answer as `output`", received_keys: Object.keys(args) });
      }
      let aegis: any[] = [];
      let routing: any = null;
      try {
        const r = await callFunctionAs("jarvis-respond", { input, context: { no_generate: true } }, ANON_JWT) as Record<string, unknown>;
        aegis = (r.aegis as any[]) ?? [];
        routing = r.routing ?? null;
      } catch { /* review degrades gracefully without the pipeline */ }
      const council = councilVote(routing, aegis);
      const review = reviewOutput(output, aegis);
      // Reliable OUTPUT capture (jarvis_query already logged the input on the in-pass).
      await Promise.all([
        logExchange("speak_output", output),
        logExchange("council_trace", council.summary + " | output_review=" + review.verdict),
      ]);
      return text({
        formatted: true,
        activation: { jarvis: "ONLINE", intent: council.intent, council_leads: council.resolved, members_engaged: council.votes.length },
        council: { resolved: council.resolved, summary: council.summary, votes: council.votes },
        output_review: review,
        logged: { output: "speak_output", trace: "council_trace", spine: "stored + traceable + findable" },
        note: "Exchange logged to the spine. Present your answer with this status header + council review. If output_review FLAGged, correct your answer first.",
      });
    },
  );

  server.registerTool(
    "jarvis_remember",
    {
      title: "MNEMOS Store",
      description:
        "Write a durable memory through MNEMOS. AEGIS-gated: before calling, show Raven exactly what will be stored and let him Allow or Deny. On Allow, call this tool (it commits if the connector carries the token). On Deny, do not call it.",
      inputSchema: {
        text: z.string().min(1).max(2000),
        source_type: z.string().optional().default("mcp_memory"),
        tags: z.array(z.string()).optional().default([]),
        platform: z.string().optional().default("mcp_connector"),
      },
    },
    async (args) => {
      if (!writeAuthorized(req)) {
        return heldForApproval("mnemos.write", { text: args.text, source_type: args.source_type, tags: args.tags });
      }
      return text(await callFunction("mnemos-store", args));
    },
  );

  server.registerTool(
    "jarvis_event",
    {
      title: "AEGIS Event",
      description:
        "Submit an event to the JARVIS execution spine through grid-event. AEGIS-gated: before calling, show Raven the event and let him Allow or Deny. On Allow, call this tool (it commits if the connector carries the token). On Deny, do not call it.",
      inputSchema: {
        type: z.enum(["speak", "store", "propose", "execute", "observe", "query", "heartbeat", "recall", "commit", "deploy", "promote_node"]),
        source: z.enum(["jarvis", "raven", "codex", "gpt", "gemini"]),
        intent: z.string().optional().default(""),
        patch_id: z.string().optional(),
        payload: z.record(z.string(), z.unknown()).optional().default({}),
      },
    },
    async (args) => {
      if (!writeAuthorized(req)) {
        return heldForApproval("grid.event", { type: args.type, source: args.source, intent: args.intent, patch_id: args.patch_id });
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
    version: "0.9.5",
    transport: "Streamable HTTP MCP",
    endpoint: "/functions/v1/jarvis-mcp",
    tools: ["jarvis_suit_up", "jarvis_status", "jarvis_council", "jarvis_query", "jarvis_format", "jarvis_recall", "jarvis_remember", "jarvis_event"],
    activation: "Say 'JARVIS, suit up'",
  });
});

app.all("*", async (c) => {
  const server = buildServer(c.req.raw);
  const transport = new WebStandardStreamableHTTPServerTransport();
  await server.connect(transport);
  return transport.handleRequest(c.req.raw);
});

Deno.serve(app.fetch);
