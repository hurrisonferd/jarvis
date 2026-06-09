import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import {
  gl12Errors, isValidJNL, ontologyClass, ownerOf, parseJNL, tierOf,
} from "./jfs.ts";

// jarvis-dex — governed access to the JD/JNL dex (JIP-DEX-0001).
// Privilege ladder via x-jarvis-token, mapped onto JSS status:
//   READ → PROPOSE (agent) → DRAFT (elevated) → COMMIT (raven) → OVERRIDE (skeleton/ZEUS).
// Files stay truth; this writes the Supabase mirror + proposals. Approved ACTIVE rows
// are reconciled back to files by a GitHub Action.

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_KEY =
  Deno.env.get("SUPABASE_SERVICE_KEY") ??
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const AGENT_TOKEN = Deno.env.get("DEX_AGENT_TOKEN") ?? "";
const ELEVATED_TOKEN = Deno.env.get("DEX_ELEVATED_TOKEN") ?? "";
const RAVEN_TOKEN = Deno.env.get("DEX_RAVEN_TOKEN") ?? "";
// Break-glass: Raven-only supreme authority (ZEUS — emergency override + halt).
// Read from the secret; the value never lives in the repo.
const SKELETON_KEY = Deno.env.get("RAVEN_SKELETON_KEY") ?? "";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type, apikey, x-jarvis-token",
};

type Tier = "READ" | "PROPOSE" | "DRAFT" | "COMMIT" | "OVERRIDE";
const RANK: Record<Tier, number> = { READ: 0, PROPOSE: 1, DRAFT: 2, COMMIT: 3, OVERRIDE: 4 };

function tierOfToken(tok: string): Tier {
  if (tok && SKELETON_KEY && tok === SKELETON_KEY) return "OVERRIDE"; // ZEUS — checked first
  if (tok && tok === RAVEN_TOKEN) return "COMMIT";
  if (tok && tok === ELEVATED_TOKEN) return "DRAFT";
  if (tok && tok === AGENT_TOKEN) return "PROPOSE";
  return "READ";
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}
const fail = (error: string, status = 400) => json({ ok: false, error }, status);

const db = createClient(SUPABASE_URL, SERVICE_KEY);

async function logEvent(tool: string, tier: Tier, jnl: string | null, actor: string, detail: unknown) {
  await db.from("dex_events").insert({ tool, tier, jnl, actor, detail });
}

async function nextJNL(domain: string, system: string, type: string): Promise<string> {
  const prefix = `${domain}-${system}-${type}-`;
  const { data } = await db.from("jnl_registry").select("jnl").like("jnl", `${prefix}%`);
  let max = 0;
  for (const r of data ?? []) {
    const seg = (r.jnl as string).slice(prefix.length).split("-")[0];
    const n = parseInt(seg, 10);
    if (!Number.isNaN(n) && n > max) max = n;
  }
  return prefix + String(max + 1).padStart(4, "0");
}

// Build a fully-derived, validated candidate entry from a proposer's "meaning".
async function deriveCandidate(a: Record<string, unknown>, status: string) {
  const name = String(a.name ?? "").trim();
  const domain = String(a.domain ?? "").toUpperCase();
  const system = String(a.system ?? "").toUpperCase();
  const type = String(a.type ?? "").toUpperCase();
  if (!name) throw new Error("name required");
  const jnl = await nextJNL(domain, system, type);
  parseJNL(jnl); // throws on grammar/domain/type error (GL6/AEGIS)
  const cls = ontologyClass(jnl);
  const tier = tierOf(domain, status);
  const owner = ownerOf(domain, name);
  const today = new Date().toISOString().slice(0, 10);
  const tags = Array.isArray(a.tags) ? a.tags.map(String) : [];
  const entry = {
    jnl, name, type, class: cls, tier, owner,
    definition: String(a.definition ?? ""), purpose: String(a.purpose ?? ""),
    source: String(a.source ?? ""),
    related: Array.isArray(a.related) ? a.related.map(String) : [],
    tags, status, created: today, updated: today,
  };
  const errs = gl12Errors({ jnl, cls, tier, status, tags });
  if (errs.length) throw new Error("GL12: " + errs.join("; "));
  return entry;
}

const TOOL_TIER: Record<string, Tier> = {
  jd_lookup: "READ", jnl_resolve: "READ", jd_list: "READ", jd_graph: "READ", jd_diff: "READ",
  dex_status: "READ",
  jd_propose: "PROPOSE", jd_draft: "DRAFT",
  jd_approve: "COMMIT", jd_reject: "COMMIT", jd_archive: "COMMIT", jd_deprecate: "COMMIT",
  dex_halt: "OVERRIDE", dex_resume: "OVERRIDE",
};

async function isHalted(): Promise<boolean> {
  const { data } = await db.from("dex_control").select("halted").eq("id", 1).maybeSingle();
  return !!data?.halted;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return fail("POST only", 405);

  let body: Record<string, unknown>;
  try { body = await req.json(); } catch { return fail("invalid JSON", 400); }

  const tool = String(body.tool ?? "");
  const args = (body.args ?? {}) as Record<string, unknown>;
  const need = TOOL_TIER[tool];
  if (!need) return fail(`unknown tool '${tool}'`, 404);

  const tier = tierOfToken(req.headers.get("x-jarvis-token") ?? "");
  if (RANK[tier] < RANK[need]) {
    return fail(`tool '${tool}' requires ${need} tier (you have ${tier})`, 403);
  }
  const actor = tier.toLowerCase();

  // ZEUS halt: when halted, only READ + OVERRIDE pass. Break-glass refuses all writes.
  if (RANK[need] >= RANK["PROPOSE"] && tier !== "OVERRIDE" && (await isHalted())) {
    return fail("dex is HALTED (emergency override). Writes are frozen until resumed.", 423);
  }

  try {
    switch (tool) {
      // ---------- OVERRIDE (skeleton key / ZEUS) ----------
      case "dex_status": {
        const { data } = await db.from("dex_control").select("*").eq("id", 1).maybeSingle();
        return json({ ok: true, tier, halted: !!data?.halted, control: data ?? null });
      }
      case "dex_halt": {
        await db.from("dex_control").update({
          halted: true, reason: String(args.reason ?? ""), by_actor: "raven", at: new Date().toISOString(),
        }).eq("id", 1);
        await logEvent("dex_halt", tier, null, "raven", { reason: args.reason ?? "" });
        return json({ ok: true, halted: true, note: "all dex writes frozen except OVERRIDE" });
      }
      case "dex_resume": {
        await db.from("dex_control").update({
          halted: false, reason: null, by_actor: "raven", at: new Date().toISOString(),
        }).eq("id", 1);
        await logEvent("dex_resume", tier, null, "raven", {});
        return json({ ok: true, halted: false, note: "dex writes resumed" });
      }
      // ---------- READ ----------
      case "jd_lookup": {
        const term = String(args.term ?? "");
        const { data } = await db.from("jd_entries").select("*")
          .or(`jnl.eq.${term},name.ilike.%${term}%,tags.cs.{${term}}`).limit(25);
        return json({ ok: true, count: data?.length ?? 0, entries: data ?? [] });
      }
      case "jnl_resolve": {
        const jnl = String(args.jnl ?? "");
        if (!isValidJNL(jnl)) return fail(`invalid JNL '${jnl}'`);
        const { data } = await db.from("jnl_registry").select("*").eq("jnl", jnl).maybeSingle();
        return data ? json({ ok: true, record: data }) : fail(`no such JNL '${jnl}'`, 404);
      }
      case "jd_list": {
        let q = db.from("jnl_registry").select("jnl,name,class,tier,status,type");
        for (const k of ["class", "tier", "status", "type"]) {
          if (args[k]) q = q.eq(k, String(args[k]));
        }
        if (args.tag) q = q.contains("tags", [String(args.tag)]);
        const { data } = await q.limit(Number(args.limit ?? 200));
        return json({ ok: true, count: data?.length ?? 0, records: data ?? [] });
      }
      case "jd_graph": {
        const jnl = String(args.jnl ?? "");
        const { data: node } = await db.from("jd_entries").select("*").eq("jnl", jnl).maybeSingle();
        if (!node) return fail(`no such JNL '${jnl}'`, 404);
        const ids = [...(node.related ?? []), ...(node.cross_refs ?? [])];
        const { data: nbrs } = ids.length
          ? await db.from("jd_entries").select("jnl,name,class,tier,status").in("jnl", ids)
          : { data: [] };
        return json({ ok: true, node, neighbors: nbrs ?? [] });
      }
      case "jd_diff": {
        const cand = await deriveCandidate(args, String(args.status ?? "TASK"));
        const { data: existing } = await db.from("jd_entries").select("*").eq("jnl", cand.jnl).maybeSingle();
        return json({ ok: true, candidate: cand, exists: !!existing, current: existing ?? null });
      }

      // ---------- PROPOSE ----------
      case "jd_propose": {
        const cand = await deriveCandidate(args, "TASK");
        const { data, error } = await db.from("jd_proposals").insert({
          jnl: cand.jnl, name: cand.name, type: cand.type, class: cand.class,
          tier: cand.tier, owner: cand.owner, definition: cand.definition,
          purpose: cand.purpose, source: cand.source, related: cand.related,
          tags: cand.tags, status: "TASK", proposer: actor,
        }).select().single();
        if (error) return fail(error.message, 500);
        await logEvent("jd_propose", tier, cand.jnl, actor, cand);
        return json({ ok: true, proposal_id: data.id, jnl: cand.jnl, staged: true });
      }

      // ---------- DRAFT ----------
      case "jd_draft": {
        const status = String(args.status ?? "TASK");
        if (status !== "TASK" && status !== "EXPANSION") return fail("draft status must be TASK or EXPANSION");
        const c = await deriveCandidate(args, status);
        await db.from("jnl_registry").upsert({
          jnl: c.jnl, name: c.name, type: c.type, class: c.class, tier: c.tier,
          owner: c.owner, location: c.source, tags: c.tags, status, created: c.created, updated: c.updated,
        });
        await db.from("jd_entries").upsert({
          jnl: c.jnl, name: c.name, type: c.type, class: c.class, tier: c.tier, owner: c.owner,
          authority: "DRAFT", definition: c.definition, purpose: c.purpose, source: c.source,
          related: c.related, tags: c.tags, status, created: c.created, updated: c.updated,
        });
        await logEvent("jd_draft", tier, c.jnl, actor, c);
        return json({ ok: true, jnl: c.jnl, status, drafted: true });
      }

      // ---------- COMMIT (Raven) ----------
      case "jd_approve": {
        const jnl = String(args.jnl ?? "");
        const { data: p } = await db.from("jd_proposals").select("*")
          .eq("jnl", jnl).eq("decision", "pending").maybeSingle();
        if (!p) return fail(`no pending proposal for '${jnl}'`, 404);
        const today = new Date().toISOString().slice(0, 10);
        await db.from("jnl_registry").upsert({
          jnl: p.jnl, name: p.name, type: p.type, class: p.class, tier: p.tier,
          owner: p.owner, location: p.source, tags: p.tags, status: "ACTIVE", created: today, updated: today,
        });
        await db.from("jd_entries").upsert({
          jnl: p.jnl, name: p.name, type: p.type, class: p.class, tier: p.tier, owner: p.owner,
          authority: "CANON", definition: p.definition, purpose: p.purpose, source: p.source,
          related: p.related, tags: p.tags, status: "ACTIVE", created: today, updated: today,
        });
        await db.from("jd_proposals").update({
          decision: "approved", decided_by: "raven", decided_at: new Date().toISOString(),
        }).eq("id", p.id);
        await logEvent("jd_approve", tier, jnl, "raven", { promoted: true });
        return json({ ok: true, jnl, status: "ACTIVE", note: "reconcile to files via Action" });
      }
      case "jd_reject": {
        const jnl = String(args.jnl ?? "");
        const { error } = await db.from("jd_proposals").update({
          decision: "rejected", decided_by: "raven", decided_at: new Date().toISOString(),
        }).eq("jnl", jnl).eq("decision", "pending");
        if (error) return fail(error.message, 500);
        await logEvent("jd_reject", tier, jnl, "raven", {});
        return json({ ok: true, jnl, rejected: true });
      }
      case "jd_archive":
      case "jd_deprecate": {
        const jnl = String(args.jnl ?? "");
        const status = tool === "jd_archive" ? "ARCHIVED" : "DEPRECATED";
        await db.from("jnl_registry").update({ status, tier: "SIDE" }).eq("jnl", jnl);
        await db.from("jd_entries").update({ status, tier: "SIDE" }).eq("jnl", jnl);
        await logEvent(tool, tier, jnl, "raven", { status });
        return json({ ok: true, jnl, status });
      }
      default:
        return fail(`unhandled tool '${tool}'`, 500);
    }
  } catch (e) {
    return fail((e as Error).message, 400);
  }
});
