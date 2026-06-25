// tools/jip.ts — the JIP lifecycle tool group (forge slice 6: first WRITE-capable group, proves
// registerXxx(server, req)). Versioned metadata containers over a JD: create/list, and the git-
// first apply/revert that write the field override into jd/patches.json as a PR (never patching
// Supabase canon). readPatchLedger + patchTable + JD_PATCHABLE are JIP-only, so they move here.
// Extracted verbatim from index.ts — zero behavior change.

import { z } from "npm:zod@^4.1.13";
import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { SERVICE_KEY, SUPABASE_URL } from "../core/env.ts";
import { callFunction, rest, text } from "../core/http.ts";
import { gh, ghPath, proposeFilePR } from "../core/github.ts";
import { heldForApproval, writeAuthorized } from "../core/auth.ts";

// Read + parse the git-first patch ledger (jd/patches.json) from main.
async function readPatchLedger(): Promise<any> {
  const cur = await gh(`/contents/${ghPath("JarvisMain/yggdrasil/jd/patches.json")}?ref=main`);
  const doc: any = { note: "Git-First patch ledger.", patches: {} };
  if (cur.ok) { try { return JSON.parse(atob((await cur.json() as any).content.replace(/\n/g, ""))); } catch { /* fall through */ } }
  return doc;
}

async function patchTable(path: string, body: unknown): Promise<boolean> {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method: "PATCH",
    headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, "content-type": "application/json", Prefer: "return=minimal" },
    body: JSON.stringify(body),
  });
  return r.ok;
}

const JD_PATCHABLE = ["definition", "purpose", "tags", "status", "owner", "steward", "related", "aliases"];

export function registerJipTools(server: McpServer, req: Request): void {
  server.registerTool(
    "jarvis_jip_create",
    { title: "JIP — create", description: "Create a JIP — a versioned metadata container for a JD (audit trail + reversible state). Supply target JD (jnl), the metadata delta, and a note. JNL is derived: JIP-{target}-{next_version}. memory_tier defaults to JLTM. AEGIS-gated. Backed by the jip_entries table.", inputSchema: { target_jd: z.string().min(5).max(40), delta: z.record(z.string(), z.unknown()).optional().default({}), note: z.string().max(500).optional().default(""), stream: z.enum(["jarvis-g", "jarvis-c", "ayre-g", "ayre-c", "argent", "raven"]).optional() } },
    async ({ target_jd, delta, note, stream }) => {
      if (!writeAuthorized(req)) return heldForApproval("jip.create", { target_jd, note }, req);
      try {
        // Derive next version number
        const existing = (await rest(`jip_entries?target_jd=eq.${target_jd}&select=version&order=version.desc&limit=1`)) as any[];
        const nextVersion = (existing?.[0]?.version ?? 0) + 1;
        const jnl = `JIP-${target_jd}-${String(nextVersion).padStart(3, "0")}`;
        const res = await fetch(`${SUPABASE_URL}/rest/v1/jip_entries`, {
          method: "POST",
          headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, "content-type": "application/json", Prefer: "return=representation" },
          body: JSON.stringify({ target_jd, delta, note, author: stream ?? "jarvis", status: "proposed", jnl }),
        });
        if (!res.ok) return text({ ok: false, status: res.status, note: "jip_entries write failed — does the table exist? (run the migration)" });
        return text({ ok: true, created: await res.json(), jnl, version: nextVersion });
      } catch (e) { return text({ ok: false, error: String(e).slice(0, 200) }); }
    },
  );
  server.registerTool(
    "jarvis_jip_list",
    { title: "JIP — list", description: "List JIPs (version history of metadata changes), optionally for one target JD. Filters by JMMS tier and JSS status. Returns jnl (JIP-{target}-{v}), memory_tier (JLTM=consolidated), and jss_status alongside the JIP fields. Read-only.", inputSchema: {
        target_jd: z.string().max(40).optional(),
        tier: z.enum(["jitm", "jstm", "jhtm", "jltm", "jatm"]).optional(),
        jss_status: z.string().max(20).optional(),
        limit: z.number().int().min(1).max(50).optional().default(20),
      } },
    async ({ target_jd, tier, jss_status, limit }) => {
      const cols = "jip,target_jd,version,status,jss_status,memory_tier,jnl,note,parent_jip,author,created_at";
      const filter: string[] = [];
      if (target_jd) filter.push(`target_jd=eq.${target_jd}`);
      if (tier) filter.push(`memory_tier.eq.${tier}`);
      if (jss_status) filter.push(`jss_status.eq.${jss_status}`);
      const filterStr = filter.length ? `&${filter.join("&")}` : "";
      const q = `jip_entries?select=${cols}${filterStr}&order=created_at.desc&limit=${limit}`;
      try { return text({ ok: true, jips: await rest(q) }); }
      catch (e) { return text({ ok: false, error: String(e).slice(0, 200), note: "jip_entries may not exist yet" }); }
    },
  );
  // JIP APPLY — the JIP UPDATES the JD (git-first via jd/patches.json PR). Gated.
  server.registerTool(
    "jarvis_jip_apply",
    { title: "JIP — apply (propose to git)", description: "Apply an approved JIP's delta to its target JD — GIT-FIRST: writes the field override (definition/purpose/tags/status/owner/related/aliases) into jd/patches.json as a PULL REQUEST, never patches Supabase canon. seed.py applies the patch on merge (any object origin); the mirror syncs Supabase. NOT applied until Raven merges the PR. AEGIS-gated: show Raven, then call on Allow.", inputSchema: { jip_id: z.string().min(1).max(60) } },
    async ({ jip_id }) => {
      if (!writeAuthorized(req)) return heldForApproval("jip.apply", { jip_id }, req);
      try {
        const jip = ((await rest(`jip_entries?or=(id.eq.${jip_id},jip.eq.${jip_id})&limit=1`)) as any[])[0];
        if (!jip) return text({ ok: false, note: `no JIP '${jip_id}'` });
        const target_jnl = jip.target_jd;
        const delta = jip.delta ?? {};
        const patch: Record<string, unknown> = {};
        for (const k of Object.keys(delta)) if (JD_PATCHABLE.includes(k)) patch[k] = (delta as any)[k];
        if (!Object.keys(patch).length) return text({ ok: false, note: "JIP delta has no patchable JD fields", patchable: JD_PATCHABLE });
        const doc = await readPatchLedger();
        doc.patches = doc.patches || {};
        doc.patches[target_jnl] = { ...(doc.patches[target_jnl] ?? {}), ...patch };
        const msg = `jip(${jip.jip ?? jip.id}): patch ${target_jnl} [${Object.keys(patch).join(", ")}]`;
        const r = await proposeFilePR("JarvisMain/yggdrasil/jd/patches.json", JSON.stringify(doc, null, 2) + "\n", msg);
        if (!r.ok) return text({ ok: false, ...r, note: "could not open the patch PR — GITHUB_TOKEN write scope?" });
        await patchTable(`jip_entries?id=eq.${jip.id}`, { status: "proposed", metadata: { ...(jip.metadata ?? {}), pr: r.pr_url, applied: Object.keys(patch) } }).catch(() => {});
        await callFunction("grid-event", { type: "commit", source: "jarvis", intent: "jip_apply_pr", payload: { jip: jip.jip ?? jip.id, target_jd: target_jnl, pr: r.number } }).catch(() => {});
        return text({ ok: true, proposed: true, target_jd: target_jnl, patch, pr_url: r.pr_url, number: r.number, note: "Git-First: applied as a PR to jd/patches.json. Merge to land; the mirror then syncs Supabase. NOT applied until merged." });
      } catch (e) { return text({ ok: false, error: String(e).slice(0, 200) }); }
    },
  );
  server.registerTool(
    "jarvis_jip_revert",
    { title: "JIP — revert (propose to git)", description: "Roll a JD back GIT-FIRST: removes the object's entry from jd/patches.json as a PULL REQUEST, so on merge seed.py restores the source-derived value. Never patches Supabase canon. AEGIS-gated.", inputSchema: { jip_id: z.string().min(1).max(60) } },
    async ({ jip_id }) => {
      if (!writeAuthorized(req)) return heldForApproval("jip.revert", { jip_id }, req);
      try {
        const jip = ((await rest(`jip_entries?or=(id.eq.${jip_id},jip.eq.${jip_id})&limit=1`)) as any[])[0];
        if (!jip) return text({ ok: false, note: `no JIP '${jip_id}'` });
        const target_jnl = jip.target_jd;
        const doc = await readPatchLedger();
        if (!doc.patches || !(target_jnl in doc.patches)) return text({ ok: false, note: `no active git patch for ${target_jnl} to revert` });
        delete doc.patches[target_jnl];
        const msg = `jip-revert(${jip.jip ?? jip.id}): drop patch ${target_jnl} (restore seed-derived)`;
        const r = await proposeFilePR("JarvisMain/yggdrasil/jd/patches.json", JSON.stringify(doc, null, 2) + "\n", msg);
        if (!r.ok) return text({ ok: false, ...r });
        await patchTable(`jip_entries?id=eq.${jip.id}`, { status: "reverted" }).catch(() => {});
        await callFunction("grid-event", { type: "commit", source: "jarvis", intent: "jip_revert_pr", payload: { jip: jip.jip ?? jip.id, target_jd: target_jnl, pr: r.number } }).catch(() => {});
        return text({ ok: true, proposed: true, target_jd: target_jnl, pr_url: r.pr_url, number: r.number, note: "Git-First: revert proposed as a PR (drops the patch; git restores the original on merge)." });
      } catch (e) { return text({ ok: false, error: String(e).slice(0, 200) }); }
    },
  );
}
