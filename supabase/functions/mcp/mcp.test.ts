// MCP tests. Run: node --experimental-strip-types mcp.test.ts
import { authorized, callFunction, handleRpc, PROTOCOL_VERSION, TOOLS, type McpEnv } from "./mcp.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

const ENV: McpEnv = { baseUrl: "https://x.supabase.co", authKey: "svc", token: "secret" };

// --- auth ---
check("open when no token set", authorized(null, ""));
check("rejects missing header when token set", !authorized(null, "secret"));
check("accepts matching bearer", authorized("Bearer secret", "secret"));
check("accepts raw token", authorized("secret", "secret"));
check("rejects wrong token", !authorized("Bearer nope", "secret"));

// --- initialize ---
const init = await handleRpc({ jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2025-06-18" } }, ENV);
check("initialize answers", init?.id === 1 && !!init?.result);
check("initialize echoes client protocol version", (init?.result as any).protocolVersion === "2025-06-18");
check("initialize falls back to default version", ((await handleRpc({ jsonrpc: "2.0", id: 2, method: "initialize", params: {} }, ENV))!.result as any).protocolVersion === PROTOCOL_VERSION);
check("initialize names the server jarvis", (init?.result as any).serverInfo.name === "jarvis");

// --- tools/list ---
const list = await handleRpc({ jsonrpc: "2.0", id: 3, method: "tools/list" }, ENV);
const tools = (list?.result as any).tools;
check("lists all four tools", tools.length === 4);
check("every tool has an inputSchema", tools.every((t: any) => t.inputSchema?.type === "object"));
check("exposes jarvis_respond", tools.some((t: any) => t.name === "jarvis_respond"));
check("tool list omits internal fn field", tools.every((t: any) => !("fn" in t)));

// --- notifications: no id → null (no reply) ---
const note = await handleRpc({ jsonrpc: "2.0", method: "notifications/initialized" }, ENV);
check("notification yields no response", note === null);

// --- ping ---
check("ping returns empty result", !!(await handleRpc({ jsonrpc: "2.0", id: 4, method: "ping" }, ENV))?.result);

// --- unknown method ---
check("unknown method errors -32601", (await handleRpc({ jsonrpc: "2.0", id: 5, method: "bogus" }, ENV))?.error?.code === -32601);

// --- tools/call with a stub fetch (proxy + content shaping) ---
const stubFetch = (async (url: string, init: any) => {
  const body = JSON.parse(init.body);
  if (String(url).endsWith("/jarvis-respond")) return new Response(JSON.stringify({ response: "Here, Raven." }), { status: 200 });
  if (String(url).endsWith("/mnemos-search")) return new Response(JSON.stringify({ method: "semantic", results: [{ text: "Raven = Armored Core" }] }), { status: 200 });
  if (String(url).endsWith("/mnemos-store")) return new Response(JSON.stringify({ ok: true, id: "abc", tags: ["x"] }), { status: 200 });
  if (String(url).endsWith("/bifrost")) return new Response(JSON.stringify({ answer: "Live result for " + body.query }), { status: 200 });
  return new Response("nope", { status: 404 });
}) as unknown as typeof fetch;

const said = await handleRpc({ jsonrpc: "2.0", id: 6, method: "tools/call", params: { name: "jarvis_respond", arguments: { input: "hi" } } }, ENV, stubFetch);
check("jarvis_respond returns spoken reply", (said?.result as any).content[0].text === "Here, Raven.");

const found = await handleRpc({ jsonrpc: "2.0", id: 7, method: "tools/call", params: { name: "mnemos_search", arguments: { query: "raven" } } }, ENV, stubFetch);
check("mnemos_search lists memories", (found?.result as any).content[0].text.includes("Armored Core"));

const stored = await handleRpc({ jsonrpc: "2.0", id: 8, method: "tools/call", params: { name: "mnemos_store", arguments: { text: "note" } } }, ENV, stubFetch);
check("mnemos_store confirms id", (stored?.result as any).content[0].text.includes("abc"));

const reach = await handleRpc({ jsonrpc: "2.0", id: 9, method: "tools/call", params: { name: "bifrost_reach", arguments: { query: "godot" } } }, ENV, stubFetch);
check("bifrost_reach returns answer", (reach?.result as any).content[0].text.includes("godot"));

const bad = await handleRpc({ jsonrpc: "2.0", id: 10, method: "tools/call", params: { name: "ghost", arguments: {} } }, ENV, stubFetch);
check("unknown tool errors -32602", bad?.error?.code === -32602);

// --- tool error surfaces as isError content, not RPC fault ---
const errFetch = (async () => new Response("boom", { status: 500 })) as unknown as typeof fetch;
const errd = await handleRpc({ jsonrpc: "2.0", id: 11, method: "tools/call", params: { name: "jarvis_respond", arguments: { input: "x" } } }, ENV, errFetch);
check("tool failure returns isError content", (errd?.result as any).isError === true);

// --- callFunction sends the service bearer ---
let seenAuth = "";
const peek = (async (_url: string, init: any) => { seenAuth = init.headers.Authorization; return new Response("{}", { status: 200 }); }) as unknown as typeof fetch;
await callFunction("bifrost", { query: "x" }, ENV, peek);
check("callFunction authorizes with service key", seenAuth === "Bearer svc");

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
