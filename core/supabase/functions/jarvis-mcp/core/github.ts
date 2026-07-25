// core/github.ts — the GitHub API layer for both repos (forge slice 2). Req-independent (Deno.env
// + fetch only), so it lives at module level and every tool imports it instead of closing over a
// buildServer-local copy. Extracted verbatim from index.ts — zero behavior change.
//   gh           — public read (token-optional; retries UNAUTH on 401/403 so reads never break)
//   ghReq        — public write (needs a write-scoped token)
//   ghp          — the private Jarvis-Private repo
//   proposeFilePR— one file → branch → commit → PR

export const GH_REPO = "https://api.github.com/repos/hurrisonferd/jarvis";
export const GH_PRIV = "https://api.github.com/repos/hurrisonferd/Jarvis-Private";

// Token resolver: prefer JARVIS_GITHUB_TOKEN (full scope; avoids reserved-name weirdness around a
// secret literally named GITHUB_TOKEN), fall back to GITHUB_TOKEN.
export const ghTok = () => Deno.env.get("JARVIS_GITHUB_TOKEN") ?? Deno.env.get("GITHUB_TOKEN") ?? "";

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

// Write-capable GitHub request (method + JSON body). Needs a write-scoped token.
export async function ghReq(method: string, path: string, body?: unknown): Promise<Response> {
  const headers: Record<string, string> = {
    "user-agent": "jarvis-mcp", accept: "application/vnd.github+json", "content-type": "application/json",
  };
  const tok = ghTok();
  if (tok) headers.authorization = `Bearer ${tok}`;
  return await fetch(`${GH_REPO}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
}

// JARVIS-PRIVATE — the private storage/scaffolding repo. Prefers JARVIS_GITHUB_TOKEN (full scope
// reaches private repos too), then GITHUB_TOKEN_PRIVATE, then GITHUB_TOKEN. Separate from gh()/
// GH_REPO so the public-repo path is never touched.
export async function ghp(method: string, path: string, body?: unknown): Promise<Response> {
  const headers: Record<string, string> = { "user-agent": "jarvis-mcp", accept: "application/vnd.github+json", "content-type": "application/json" };
  const tok = Deno.env.get("JARVIS_GITHUB_TOKEN") ?? Deno.env.get("GITHUB_TOKEN_PRIVATE") ?? Deno.env.get("GITHUB_TOKEN");
  if (tok) headers.authorization = `Bearer ${tok}`;
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
  if (!br.ok) return { ok: false, step: "branch", status: br.status, note: "GITHUB_TOKEN may lack write scope" };
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
