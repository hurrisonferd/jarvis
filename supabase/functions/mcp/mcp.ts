// MCP — the universal adapter. Pure logic (no Deno.serve) so it unit-tests under
// `node --experimental-strip-types`. index.ts wraps this in the HTTP shell.
//
// This is the protocol skin over JARVIS: it re-exposes the existing edge
// functions (jarvis-respond / mnemos-search / mnemos-store / bifrost) as MCP
// tools so ANY MCP-aware client (Claude.ai, ChatGPT dev mode, Gemini) mounts the
// SAME JARVIS — one memory, one record, one mind. "JARVIS is not the shell."

export const PROTOCOL_VERSION = "2024-11-05";
export const SERVER_INFO = { name: "jarvis", version: "1.0.0" };

// Env the transport needs. Passed in (not read from Deno) so the logic is pure.
export interface McpEnv {
  baseUrl: string;   // SUPABASE_URL — where the sibling functions live
  authKey: string;   // SUPABASE_SERVICE_ROLE_KEY — to call the siblings
  token: string;     // MCP_TOKEN — the bearer clients must present (optional)
}

// JSON-RPC 2.0 shapes (MCP rides on these).
export interface RpcMessage { jsonrpc: "2.0"; id?: string | number | null; method: string; params?: any; }
export interface RpcResponse { jsonrpc: "2.0"; id: string | number | null; result?: unknown; error?: { code: number; message: string }; }

export const rpcOk = (id: RpcResponse["id"], result: unknown): RpcResponse => ({ jsonrpc: "2.0", id, result });
export const rpcErr = (id: RpcResponse["id"], code: number, message: string): RpcResponse => ({ jsonrpc: "2.0", id, error: { code, message } });

// The four tools. Each maps to one edge function. inputSchema is JSON Schema —
// every MCP client renders/validates from this, so it's the whole contract.
export const TOOLS = [
  {
    name: "jarvis_respond",
    description:
      "Talk to JARVIS — the full companion pipeline (semantic recall → AEGIS gating → in-voice reply). Use this to ask JARVIS anything or to converse as Raven. Returns JARVIS's spoken reply.",
    inputSchema: {
      type: "object",
      properties: {
        input: { type: "string", description: "What you're saying to JARVIS." },
        context: { type: "object", description: "Optional state (mode, alignPct, speakHistory, authorized[]). Usually omit." },
      },
      required: ["input"],
    },
    fn: "jarvis-respond",
  },
  {
    name: "mnemos_search",
    description:
      "Semantic recall over JARVIS's memory ledger (pgvector, falls back to full-text). Use to retrieve what JARVIS remembers about Raven, decisions, the mission, prior sessions.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "What to recall." },
        limit: { type: "number", description: "Max results (default 10)." },
        source_type: { type: "string", description: "Filter by source_type (e.g. 'decision', 'raven_profile')." },
        min_similarity: { type: "number", description: "0–1 cosine floor for semantic matches." },
      },
      required: ["query"],
    },
    fn: "mnemos-search",
  },
  {
    name: "mnemos_store",
    description:
      "Commit a memory to JARVIS's ledger (auto-tagged + embedded for recall). AEGIS-governed write. Use to record a decision, a fact about Raven, or an insight worth keeping.",
    inputSchema: {
      type: "object",
      properties: {
        text: { type: "string", description: "The memory to store." },
        tags: { type: "array", items: { type: "string" }, description: "Optional extra tags." },
        source_type: { type: "string", description: "e.g. 'decision', 'raven_profile', 'speak_input'." },
      },
      required: ["text"],
    },
    fn: "mnemos-store",
  },
  {
    name: "bifrost_reach",
    description:
      "JARVIS's reach to live web knowledge (grounded search). Read-only. Use for current facts JARVIS wouldn't hold in memory.",
    inputSchema: {
      type: "object",
      properties: { query: { type: "string", description: "What to look up." } },
      required: ["query"],
    },
    fn: "bifrost",
  },
] as const;

// Proxy one call to a sibling edge function. Each function stays the single
// source of truth; MCP just re-shapes the doorway. Returns parsed JSON or throws.
export async function callFunction(
  fnName: string,
  body: unknown,
  env: McpEnv,
  fetchImpl: typeof fetch = fetch,
): Promise<any> {
  const url = `${env.baseUrl}/functions/v1/${fnName}`;
  const r = await fetchImpl(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.authKey}`,
      apikey: env.authKey,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body ?? {}),
  });
  const text = await r.text();
  if (!r.ok) throw new Error(`${fnName} ${r.status}: ${text.slice(0, 200)}`);
  try { return JSON.parse(text); } catch { return { raw: text }; }
}

// Shape a tool's raw function output into MCP text content. Keep the human-
// facing string tight; stash the full payload in a second block for clients
// that want structure.
function toContent(toolName: string, data: any): { content: { type: "text"; text: string }[] } {
  let lead: string;
  if (toolName === "jarvis_respond") lead = String(data.response ?? "(no reply)");
  else if (toolName === "bifrost_reach") lead = String(data.answer ?? "(no answer)");
  else if (toolName === "mnemos_store") lead = data.ok ? `Stored. id=${data.id} tags=[${(data.tags ?? []).join(", ")}]` : `Store failed: ${data.error ?? "unknown"}`;
  else if (toolName === "mnemos_search") {
    const rows = (data.results ?? []) as any[];
    lead = rows.length
      ? `${rows.length} memories (${data.method ?? "?"}):\n` + rows.map((m, i) => `${i + 1}. ${m.text}`).join("\n")
      : "No matching memories.";
  } else lead = JSON.stringify(data);
  return { content: [{ type: "text", text: lead }] };
}

// The dispatcher. Handles one JSON-RPC message. Returns a response, or null for
// notifications (no id → nothing to answer). `initialize`/`tools/list` need no
// network; `tools/call` proxies to the sibling function.
export async function handleRpc(
  msg: RpcMessage,
  env: McpEnv,
  fetchImpl: typeof fetch = fetch,
): Promise<RpcResponse | null> {
  const id = msg.id ?? null;

  switch (msg.method) {
    case "initialize": {
      const clientVer = msg.params?.protocolVersion;
      return rpcOk(id, {
        protocolVersion: typeof clientVer === "string" ? clientVer : PROTOCOL_VERSION,
        capabilities: { tools: { listChanged: false } },
        serverInfo: SERVER_INFO,
        instructions:
          "JARVIS — Raven's companion intelligence. Use jarvis_respond to converse, mnemos_search/store for memory, bifrost_reach for live web. Same mind across every client.",
      });
    }

    case "ping":
      return rpcOk(id, {});

    case "tools/list":
      return rpcOk(id, {
        tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })),
      });

    case "tools/call": {
      const name = msg.params?.name;
      const args = msg.params?.arguments ?? {};
      const tool = TOOLS.find((t) => t.name === name);
      if (!tool) return rpcErr(id, -32602, `unknown tool: ${name}`);
      try {
        const data = await callFunction(tool.fn, args, env, fetchImpl);
        return rpcOk(id, toContent(tool.name, data));
      } catch (e) {
        // Tool errors are reported as a successful RPC with isError content, per
        // MCP — the model sees the failure and can recover, not a hard RPC fault.
        return rpcOk(id, { content: [{ type: "text", text: `Tool error: ${String(e).slice(0, 300)}` }], isError: true });
      }
    }

    // Notifications (initialized, cancelled, …) carry no id — acknowledge silently.
    default:
      if (id === null || id === undefined) return null;
      return rpcErr(id, -32601, `method not found: ${msg.method}`);
  }
}

// Bearer check. If MCP_TOKEN is set, the caller must present it (Bearer or raw).
// If unset, open (so the endpoint works before the secret is added). The
// platform's verify_jwt is disabled for this function so MCP owns its own auth.
export function authorized(header: string | null, token: string): boolean {
  if (!token) return true;
  if (!header) return false;
  const presented = header.replace(/^Bearer\s+/i, "").trim();
  return presented === token;
}
