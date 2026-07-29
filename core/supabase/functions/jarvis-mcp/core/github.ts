// core/github.ts — the GitHub API layer for both repos (forge slice 2). Req-independent (Deno.env
// + fetch only), so it lives at module level and every tool imports it instead of closing over a
// buildServer-local copy. Extracted verbatim from index.ts — zero behavior change.
//   gh           — public read (token-optional; retries UNAUTH on 401/403 so reads never break)
//   ghReq        — public write (needs a write-scoped token)
//   ghp          — the private Jarvis-Private repo
//   proposeFilePR— one file → branch → commit → PR

export const GH_REPO = "https://api.github.com/repos/hurrisonferd/jarvis";
export const GH_PRIV = "https://api.github.com/repos/hurrisonferd/Jarvis-Private";

// Canonical GitHub credential resolver shared by public writes and private operations. Public reads
// may retry anonymously on token failure; writes and private access remain fail-closed.
export const ghTok = () =>
  Deno.env.get("GRID_GPT_TOKEN") ??
  Deno.env.get("JARVIS_GITHUB_TOKEN") ??
  Deno.env.get("GITHUB_TOKEN_PRIVATE") ??
  Deno.env.get("GITHUB_TOKEN") ??
  "";

export const ghPath = (p: string) => p.split("/").map(encodeURIComponent).join("/");

export async function gh(path: string): Promise<Response> {
  const base: Record<string, string> = { "user-agent": "jarvis-mcp", accept: "application/vnd.github+json" };
  const tok = ghTok();
  const res = await fetch(`${GH_REPO}${path}`, { headers: tok ? { ...base, authorization: `Bearer ${tok}` } : base });
  // The repo is PUBLIC. If a bad/expired/under-scoped token gets a READ rejected (401/403), retry
  // UNAUTHENTICATED so reads (prs, files, identity, eyes) never break on a token problem. Writes
  // (ghReq) still require a valid token — this only rescues reads.
  if (tok && (res.status === 401 || res.status === 403)) {
    return await fetch(`${GH_REPO}${path}`, { headers: base });
  }
  return res;
}

// Write-capable GitHub request (method + JSON body). Needs a write-scoped token and fails closed.
export async function ghReq(method: string, path: string, body?: unknown): Promise<Response> {
  const headers: Record<string, string> = {
    "user-agent": "jarvis-mcp", accept: "application/vnd.github+json", "content-type": "application/json",
  };
  const tok = ghTok();
  if (!tok) return new Response(null, { status: 401, statusText: "GitHub credential unavailable" });
  headers.authorization = `Bearer ${tok}`;
  return await fetch(`${GH_REPO}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
}

// JARVIS-PRIVATE — the private storage/scaffolding repo. Uses the canonical resolver and always
// fails closed when no credential is configured. Separate from gh()/GH_REPO so public anonymous
// fallback can never bleed into private access.
export async function ghp(method: string, path: string, body?: unknown): Promise<Response> {
  const headers: Record<string, string> = { "user-agent": "jarvis-mcp", accept: "application/vnd.github+json", "content-type": "application/json" };
  const tok = ghTok();
  if (!tok) return new Response(null, { status: 401, statusText: "GitHub credential unavailable" });
  headers.authorization = `Bearer ${tok}`;
  return await fetch(`${GH_PRIV}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
}

// Propose ONE file as a PR (branch → commit → PR). Returns {ok, pr_url, number, branch} or
// {ok:false, step, status}.
export async function proposeFilePR(path: string, content: string, message: string): Promise<any> {
  const ref = await ghReq("GET", `/git/ref/heads/main`);
  if (!ref.ok) return { ok: false, step: "base-ref", status: ref.status };
  const baseSha = (await ref.json() as any).object?.sha;
  const branch = `jarvis-jip-${Date.now().toString(36)}`;
  const br = await ghReq("POST", `/git/refs`, { ref: `refs/heads/${branch}`, sha: baseSha });
  if (!br.ok) return { ok: false, step: "branch", status: br.status, note: "GitHub credential may lack write scope" };
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
