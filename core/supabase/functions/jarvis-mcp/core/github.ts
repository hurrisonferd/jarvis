// core/github.ts — GitHub API layer with Blackwall credential separation.
//
// One broad token must not silently become every GitHub authority in the Grid.
// PUBLIC_READ, PUBLIC_WRITE, and PRIVATE_REPO are separate credential classes.

export const GH_REPO = "https://api.github.com/repos/hurrisonferd/jarvis";
export const GH_PRIV = "https://api.github.com/repos/hurrisonferd/Jarvis-Private";

const publicReadTok = () => (
  Deno.env.get("GITHUB_TOKEN_PUBLIC_READ") ??
  Deno.env.get("GRID_GPT_TOKEN") ??
  ""
).trim();

const publicWriteTok = () => (
  Deno.env.get("GITHUB_TOKEN_PUBLIC_WRITE") ??
  Deno.env.get("JARVIS_GITHUB_TOKEN") ??
  Deno.env.get("GRID_GPT_TOKEN") ??
  Deno.env.get("GITHUB_TOKEN") ??
  ""
).trim();

const privateTok = () => (
  Deno.env.get("GITHUB_TOKEN_PRIVATE") ??
  ""
).trim();

const privateRepoEnabled = () =>
  (Deno.env.get("MCP_PRIVATE_REPO_ENABLED") ?? "false").toLowerCase() === "true";

// Compatibility export used by read/search helpers elsewhere in the MCP bundle.
// Crucially, this can never return GITHUB_TOKEN_PRIVATE.
export const ghTok = publicReadTok;

export const ghPath = (p: string) => p.split("/").map(encodeURIComponent).join("/");

export async function gh(path: string): Promise<Response> {
  const base: Record<string, string> = {
    "user-agent": "jarvis-mcp",
    accept: "application/vnd.github+json",
  };
  const tok = publicReadTok();
  const res = await fetch(`${GH_REPO}${path}`, {
    headers: tok ? { ...base, authorization: `Bearer ${tok}` } : base,
  });
  if (tok && (res.status === 401 || res.status === 403)) {
    return await fetch(`${GH_REPO}${path}`, { headers: base });
  }
  return res;
}

export async function ghReq(method: string, path: string, body?: unknown): Promise<Response> {
  const headers: Record<string, string> = {
    "user-agent": "jarvis-mcp",
    accept: "application/vnd.github+json",
    "content-type": "application/json",
  };
  const tok = publicWriteTok();
  if (!tok) return new Response(null, { status: 401, statusText: "Public GitHub write credential unavailable" });
  headers.authorization = `Bearer ${tok}`;
  return await fetch(`${GH_REPO}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
}

// Private access is a separate authority domain and is OFF by default until the
// MCP transport has universal request-bound private-read authorization.
// This prevents an open read tool from turning a server-held PAT into data egress.
export async function ghp(method: string, path: string, body?: unknown): Promise<Response> {
  if (!privateRepoEnabled()) {
    return new Response(null, { status: 403, statusText: "Private repo access held by Blackwall" });
  }
  const headers: Record<string, string> = {
    "user-agent": "jarvis-mcp",
    accept: "application/vnd.github+json",
    "content-type": "application/json",
  };
  const tok = privateTok();
  if (!tok) return new Response(null, { status: 401, statusText: "Private GitHub credential unavailable" });
  headers.authorization = `Bearer ${tok}`;
  return await fetch(`${GH_PRIV}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
}

export async function proposeFilePR(path: string, content: string, message: string): Promise<any> {
  const ref = await ghReq("GET", `/git/ref/heads/main`);
  if (!ref.ok) return { ok: false, step: "base-ref", status: ref.status };
  const baseSha = (await ref.json() as any).object?.sha;
  const branch = `jarvis-jip-${Date.now().toString(36)}`;
  const br = await ghReq("POST", `/git/refs`, { ref: `refs/heads/${branch}`, sha: baseSha });
  if (!br.ok) return { ok: false, step: "branch", status: br.status, note: "Public GitHub write credential may lack scope" };
  const ex = await ghReq("GET", `/contents/${ghPath(path)}?ref=${branch}`);
  const existingSha = ex.ok ? (await ex.json() as any).sha : undefined;
  const put = await ghReq("PUT", `/contents/${ghPath(path)}`,
    { message, content: btoa(unescape(encodeURIComponent(content))), branch, ...(existingSha ? { sha: existingSha } : {}) });
  if (!put.ok) return { ok: false, step: "write", status: put.status };
  const pr = await ghReq("POST", `/pulls`, { title: message, head: branch, base: "main", body: message });
  if (!pr.ok) return { ok: false, step: "pr", status: pr.status };
  const p = await pr.json() as any;
  return { ok: true, pr_url: p.html_url, number: p.number, branch };
}
