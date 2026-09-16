// resources.ts — BLACKWALL-safe MCP resources.
//
// Resources are context injection surfaces. A resource that reads private memory,
// Trinity, session history, or Jarvis-Private without request-bound authorization
// is data egress even when the transport calls it "read-only".

import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { z } from "npm:zod@^4.1.13";
import { rest, text } from "./core/http.ts";
import { countRows } from "./core/supabase.ts";
import { clockNow } from "./core/builders.ts";

interface CacheEntry { data: string; timestamp: number }
const RESOURCE_CACHE = new Map<string, CacheEntry>();
const CACHE_TTL_MS = 5 * 60 * 1000;

function getCached(key: string): string | null {
  const entry = RESOURCE_CACHE.get(key);
  if (!entry) return null;
  if (Date.now() - entry.timestamp > CACHE_TTL_MS) {
    RESOURCE_CACHE.delete(key);
    return null;
  }
  return entry.data;
}
function setCache(key: string, data: string): string {
  RESOURCE_CACHE.set(key, { data, timestamp: Date.now() });
  return data;
}
function invalidateCache(pattern?: string): void {
  if (!pattern) return RESOURCE_CACHE.clear();
  for (const key of RESOURCE_CACHE.keys()) if (key.includes(pattern)) RESOURCE_CACHE.delete(key);
}

function held(name: string, reason: string): string {
  return [
    `# ${name}`,
    "",
    "**BLACKWALL HOLD**",
    "",
    reason,
    "",
    "Private context requires request-bound private-read authority, explicit purpose, and a bounded projection.",
    "Reachability is not consent. Read-only is not automatically safe.",
  ].join("\n");
}

async function safeState(): Promise<string> {
  const key = "resource:state";
  const cached = getCached(key);
  if (cached) return cached;
  const count = await countRows("mnemos_memories").catch(() => null);
  const now = clockNow();
  return setCache(key, [
    "# JARVIS System State",
    "",
    "- **Status:** OPERATIONAL",
    `- **UTC:** ${String(now.utc ?? "unknown")}`,
    `- **Memory ledger:** ${count === null ? "unreachable" : "reachable"}`,
    `- **Memory records:** ${count ?? "unknown"}`,
    "- **Privacy:** BLACKWALL_NO_HARVEST",
    "- **Private memory bodies projected:** no",
    "- **Private repo content projected:** no",
    "- **Authority:** Raven commits or rejects",
  ].join("\n"));
}

async function safeRecent(): Promise<string> {
  const key = "resource:recent";
  const cached = getCached(key);
  if (cached) return cached;
  const rows = await rest(
    "execution_trace?select=type,source,stage,severity,patch_id,created_at&order=created_at.desc&limit=10",
  ).catch(() => []);
  const list = Array.isArray(rows) ? rows : [];
  return setCache(key, [
    "# Recent Execution Metadata",
    "",
    "Payloads and intent bodies are intentionally omitted.",
    "",
    ...list.map((r: any) => `- ${r.created_at ?? "?"} · ${r.type ?? "?"} · ${r.source ?? "?"} · ${r.stage ?? "?"} · ${r.severity ?? "?"}`),
  ].join("\n"));
}

function publicIdentity(): string {
  return [
    "# JARVIS + AYRE Public Identity",
    "",
    "JARVIS is a synthesis stream. AYRE is a divergence stream.",
    "They operate inside a governed Grid where Raven is final authority.",
    "",
    "Blackwall boundary:",
    "- public recognition != private identity export",
    "- public capability discovery != private context access",
    "- conversation history, private keel, accumulated memory, and resident data are not projected here",
  ].join("\n");
}

function quickRef(): string {
  return [
    "# JARVIS MCP Public-Safe Quick Reference",
    "",
    "- `jarvis_now`: server time",
    "- `jarvis_status`: bounded operational status",
    "- `jarvis_node_card`: public recognition packet",
    "- private memory/context: authenticated governed lanes only",
    "- durable effects: explicit authorization only",
    "- default privacy posture: no harvest, minimum necessary data, fail closed on unknown authority",
  ].join("\n");
}

const resources = [
  ["System State", "jarvis://state", "Reference-safe operational state"],
  ["Recent Actions", "jarvis://recent", "Reference-safe execution metadata"],
  ["Memory Summary", "jarvis://memory", "Private memory resource boundary"],
  ["Active Workers", "jarvis://swarm", "Private worker/presence boundary"],
  ["JARVIS + AYRE Identity", "jarvis://identity", "Public-safe identity description"],
  ["Today's Trinity", "jarvis://trinity", "Private conversation boundary"],
  ["Operations Docs", "jarvis://ops", "Private operations-doc boundary"],
  ["Full Context", "jarvis://fullcontext", "Private aggregate-context boundary"],
  ["Quick Reference", "jarvis://quickref", "Public-safe quick reference"],
] as const;

export function registerResources(server: McpServer): void {
  for (const [name, uri, description] of resources) {
    server.registerResource(
      name,
      uri,
      { title: name, description, mimeType: "text/markdown" },
      async () => {
        let content: string;
        if (uri === "jarvis://state") content = await safeState();
        else if (uri === "jarvis://recent") content = await safeRecent();
        else if (uri === "jarvis://identity") content = publicIdentity();
        else if (uri === "jarvis://quickref") content = quickRef();
        else if (uri === "jarvis://memory") content = held("Memory Summary", "Memory bodies, tiers, and recent resident content are private data, not ambient connector context.");
        else if (uri === "jarvis://swarm") content = held("Worker Status", "Presence, task, and worker activity metadata require an authenticated operational projection.");
        else if (uri === "jarvis://trinity") content = held("Trinity", "Trinity contains private conversation material and is not a public MCP resource.");
        else if (uri === "jarvis://ops") content = held("Operations Docs", "Private operational documents require a scoped private-repo read capability.");
        else content = held("Full Context", "Bulk identity + conversation + session aggregation is disabled. Request the minimum necessary governed context instead.");
        return { contents: [{ uri, mimeType: "text/markdown", text: content }] };
      },
    );
  }

  server.registerPrompt(
    "jarvis/bootstrap",
    {
      description: "Privacy-safe session startup template",
      argsSchema: { task: z.string().max(1000).optional(), agent: z.string().max(80).optional() },
    },
    async ({ task, agent }) => ({
      messages: [{
        role: "user" as const,
        content: {
          type: "text" as const,
          text: [
            "# JARVIS Session Bootstrap",
            `Agent: ${agent ?? "connector"}`,
            `Task: ${task ?? "unspecified"}`,
            "Resolve current source before claims. Use minimum necessary context. Do not load private memory or private repo data unless this task has an authenticated governed need for it. Durable effects require explicit authority and receipts.",
          ].join("\n"),
        },
      }],
    }),
  );

  server.registerPrompt(
    "jarvis/task-review",
    {
      description: "Review a task without loading unrelated private context",
      argsSchema: { task_description: z.string().max(4000), context: z.string().max(4000).optional() },
    },
    async ({ task_description, context }) => ({
      messages: [{ role: "user" as const, content: { type: "text" as const, text: `Review this task for feasibility, risk, authority, data minimization, rollback, and verification.\n\nTask: ${task_description}${context ? `\nContext: ${context}` : ""}` } }],
    }),
  );

  server.registerPrompt(
    "jarvis/architect",
    {
      description: "Design a bounded component with Blackwall authority/data boundaries",
      argsSchema: { component: z.string().max(200), requirements: z.string().max(4000).optional() },
    },
    async ({ component, requirements }) => ({
      messages: [{ role: "user" as const, content: { type: "text" as const, text: `Design ${component} with explicit input/output, identity, authority, data-purpose, retention, recovery, and receipt boundaries.${requirements ? `\nRequirements: ${requirements}` : ""}` } }],
    }),
  );

  server.registerTool(
    "jarvis_resource_cache_invalidate",
    {
      title: "JARVIS — Resource Cache Invalidate",
      description: "Clear only this process's reference-safe resource cache.",
      inputSchema: { pattern: z.string().max(120).optional() },
    },
    async ({ pattern }) => {
      invalidateCache(pattern || undefined);
      return text({ ok: true, local_cache_only: true, cached_entries: RESOURCE_CACHE.size });
    },
  );
}

export { getCached, invalidateCache };
