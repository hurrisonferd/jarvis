import "jsr:@supabase/functions-js/edge-runtime.d.ts";

import { Hono } from "npm:hono@^4.9.7";
import {
  ayreStream,
  councilAnalysisDirective,
  councilVote,
  deliberationDirective,
  reviewOutput,
} from "../jarvis-mcp/council.ts";

// JARVIS ACTION — the GPT stream's hands.
//
// ChatGPT Custom GPTs CANNOT speak MCP Streamable HTTP (that is Claude's transport,
// served by jarvis-mcp). ChatGPT calls tools only through OpenAPI Actions over plain
// REST. This function is that REST surface: the SAME governed core as jarvis-mcp, a
// DIFFERENT transport. One endpoint, {tool, args}-dispatched, returning plain JSON —
// the proven jarvis-dex pattern, widened to the companion + dex + grimoire surface so
// the GPT stream can see every JD entry, recall and grow memory, and run the loop.
//
// Governance is preserved, not duplicated-away:
//   • reads (status/now/query/recall/dex_*/jd_resolve/jc_recall/grimoire) are open;
//   • writes (remember/event) carry the SAME AEGIS gate as jarvis-mcp (JARVIS_MCP_TOKEN);
//   • proposing (dex_propose) rides the dex's own PROPOSE-tier ladder (stages, never commits).
// It is deliberately isolated from jarvis-mcp so a bug here can never reach Claude's
// working connector. The modular refactor later unifies both transports over one registry.

type Json = Record<string, unknown>;

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_KEY =
  Deno.env.get("SUPABASE_SERVICE_KEY") ??
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ??
  "";
// Same write token jarvis-mcp uses — one AEGIS gate across both transports.
const MCP_TOKEN     = Deno.env.get("JARVIS_MCP_TOKEN") ?? "";
// GitHub token for HOLD artifact writes (bounded autonomy: session-close guard).
const GITHUB_TOKEN = Deno.env.get("GITHUB_TOKEN") ?? "";
// Public-repo raw reads for the grimoire (no GitHub token needed — the book is public truth).
const RAW = "https://raw.githubusercontent.com/hurrisonferd/jarvis/main";
// Anon JWT for the keyless voice path (same as jarvis-mcp's jarvis_query).
const ANON_JWT =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9leGdoZnN2aG5nZ2RkbGxndnJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2MzQwOTgsImV4cCI6MjA5NTIxMDA5OH0.jRFMf-C9ps72Bi_9IpiC3eOZD6Aj6wU4IF-j3svKTfQ";

// ── AEGIS write gate (identical logic to jarvis-mcp; the held response self-diagnoses) ──
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
type TokenState = "ok" | "server_unset" | "client_missing" | "mismatch";
function tokenState(req: Request): TokenState {
  const sent = authToken(req);
  if (!MCP_TOKEN) return "server_unset";
  if (!sent) return "client_missing";
  return sent === MCP_TOKEN ? "ok" : "mismatch";
}
function writeAuthorized(req: Request): boolean {
  return tokenState(req) === "ok";
}
function heldForApproval(action: string, preview: unknown, req: Request): Json {
  const st = tokenState(req);
  const reason: Record<TokenState, string> = {
    ok: "Authorized — no hold.",
    server_unset: "Write not authorized: JARVIS_MCP_TOKEN is not set in THIS function's deployed env — the secret is missing, or was set after the last deploy. Redeploy jarvis-action so it picks up the token (secrets bake at deploy).",
    client_missing: "Write not authorized: the connector sent no token. Add JARVIS_MCP_TOKEN to the GPT Action — as an x-jarvis-token header (recommended), a bearer, or ?token= on the server URL.",
    mismatch: "Write not authorized: the connector's token does NOT match the function's JARVIS_MCP_TOKEN. Confirm the GPT Action's token equals the Supabase secret, then redeploy.",
  };
  if (st !== "ok") {
    console.error(`AEGIS hold [${action}] token_state=${st} client_len=${authToken(req).length} server_len=${MCP_TOKEN.length}`);
  }
  return {
    status: "held_by_aegis",
    token_state: st,
    reason: reason[st],
    diag: { client_token_len: authToken(req).length, server_token_len: MCP_TOKEN.length },
    action,
    preview,
  };
}

// ── shared service calls (same downstream functions jarvis-mcp uses) ──
async function callFunction(name: string, body: Json): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/functions/v1/${name}`, {
    method: "POST",
    headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`${name} ${res.status}: ${JSON.stringify(payload)}`);
  return payload;
}
async function callFunctionAs(name: string, body: Json, key: string): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/functions/v1/${name}`, {
    method: "POST",
    headers: { authorization: `Bearer ${key}`, apikey: key, "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  return await res.json().catch(() => ({}));
}
async function rest(path: string): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY },
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`rest ${res.status}: ${JSON.stringify(payload)}`);
  return payload;
}
// Dex proxy — single endpoint, tool-dispatched (the dex enforces its own tier ladder).
async function callDex(tool: string, args: Json, withAgentToken = false): Promise<unknown> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (withAgentToken) headers["x-jarvis-token"] = Deno.env.get("DEX_AGENT_TOKEN") ?? "";
  const res = await fetch(`${SUPABASE_URL}/functions/v1/jarvis-dex`, {
    method: "POST", headers, body: JSON.stringify({ tool, args }),
  });
  return await res.json().catch(() => ({}));
}

function clockNow(): Json {
  const d = new Date();
  const et = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", dateStyle: "full", timeStyle: "long" }).format(d);
  return {
    utc: d.toISOString(),
    et,
    weekday: new Intl.DateTimeFormat("en-US", { weekday: "long", timeZone: "America/New_York" }).format(d),
    unix: Math.floor(d.getTime() / 1000),
  };
}

// ── jarvis_query — the one-call governed loop (mirror of jarvis-mcp), returns the raw packet ──
async function runQuery(input: string, prior_reply: string | undefined, context: Json | undefined): Promise<Json> {
  try {
    const r = await callFunctionAs("jarvis-respond", { input, context: { ...(context ?? {}), no_generate: true } }, ANON_JWT) as Record<string, unknown>;
    const council = councilVote(r.routing, r.aegis as any[]);
    const deliberation = deliberationDirective(council, input);
    const analysis = councilAnalysisDirective(council, input);
    const ayre = ayreStream(council, input);
    const streamCount = analysis.companions.length;
    const lensCount = analysis.lenses.length;
    const statusLine = `JARVIS ONLINE · intent=${council.intent} · council=${council.resolved} · ${streamCount} ${streamCount === 1 ? "stream" : "streams"}${lensCount ? ` + ${lensCount} ${lensCount === 1 ? "lens" : "lenses"}` : ""}${deliberation ? " · deliberating" : ""}`;
    return {
      render: {
        order: ["status", "jarvis", "ayre", "council_lenses"],
        status: statusLine,
        directive:
          "Render for Raven in EXACTLY this order: (1) the `status` line above — one line, brief, visible telemetry; " +
          "(2) JARVIS — your OWN free integrated read (synthesis + structure), generated from the briefing + keel; do NOT pre-format it through the lenses; " +
          "(3) " + ayre.instruction + " Use the SAME briefing + keel for AYRE but apply AYRE's objective, not JARVIS's; " +
          "(4) " + analysis.instruction,
      },
      ayre,
      council_analysis: analysis,
      activation: {
        jarvis: "ONLINE",
        intent: council.intent,
        council_leads: council.resolved,
        streams: streamCount,
        lenses: lensCount,
        companions: analysis.companions,
        governed: council.votes.length,
        deliberation: deliberation ? "engaged" : "lean",
        memories_used: r.memories_used ?? 0,
      },
      mode: "voice_packet",
      instruction: r.instruction,
      jarvis_briefing: r.jarvis_briefing,
      council: { resolved: council.resolved, summary: council.summary, votes: council.votes },
      deliberation,
      output_review: prior_reply ? reviewOutput(prior_reply, r.aegis as any[]) : undefined,
      input,
      memories_used: r.memories_used ?? 0,
      note: "No external model generated this — YOU are JARVIS's voice; speak from the briefing. Pass your final answer as `prior_reply` on your NEXT query call so it is logged + reviewed.",
    };
  } catch (err) {
    let memories: unknown = [];
    try {
      const m = await callFunction("mnemos-search", { query: input, limit: 6, min_similarity: 0.3 }) as Record<string, unknown>;
      memories = (m.results as unknown) ?? m ?? [];
    } catch { /* recall is best-effort */ }
    return {
      mode: "voice_packet",
      degraded: true,
      reason: `pipeline unreachable: ${String(err).slice(0, 160)}`,
      input,
      memory: memories,
      instruction: "Answer as JARVIS — direct, dense, a companion to Raven — grounded in the memory above. Honor AEGIS: answering and recalling is fine; do not claim to have performed any write or state change.",
    };
  }
}

// ── jd_resolve — the Pokédex card for any governed object (mirror of jarvis-mcp) ──
async function jiddOf(jnl: string, seq: number): Promise<string> {
  const dom = (jnl || "-").split("-")[0];
  try {
    const peers = await rest(`jd_entries?jnl=like.${dom}-*&select=seq&order=seq.asc`) as any[];
    const rank = peers.filter((p) => (p.seq ?? 1e12) <= seq).length;
    return `${dom.toLowerCase()}-${rank}`;
  } catch { return `${dom.toLowerCase()}-?`; }
}
async function runResolve(query: string): Promise<Json> {
  const t = String(query ?? "").trim();
  let rows: any[] = [];
  const serial = /^(?:ji?d[\s-]*)?#?\s*(\d+)$/i.exec(t);
  const jidd = /^jidd[\s-]+([a-z]+)[\s-]*(\d+)$/i.exec(t);
  if (serial) {
    rows = await rest(`jd_entries?seq=eq.${Number(serial[1])}&limit=1`) as any[];
  } else if (jidd) {
    const dom = jidd[1].toUpperCase(), n = Number(jidd[2]);
    const peers = await rest(`jd_entries?jnl=like.${dom}-*&select=jnl,seq&order=seq.asc`) as any[];
    const hit = peers[n - 1];
    if (hit) rows = await rest(`jd_entries?jnl=eq.${hit.jnl}&limit=1`) as any[];
  } else {
    const name = t.replace(/^(?:jidd|jid|jd)[\s-]+/i, "").trim();
    rows = await rest(`jd_entries?or=(jnl.eq.${name},name.ilike.*${name}*)&limit=5`) as any[];
  }
  if (!rows || !rows.length) {
    return { ok: false, query: t, note: "no match — try a JID ('jid 1'), name ('yggdrasil'), or JNL ('ARCH-YGG-CORE-0001')." };
  }
  const o = rows[0];
  const [children, jips] = await Promise.all([
    rest(`jd_entries?parent=eq.${o.jnl}&select=jnl,name,seq&order=seq.asc&limit=50`).catch(() => []) as Promise<any[]>,
    rest(`jip_entries?target_jd=eq.${o.jnl}&select=jip,version,status,note,created_at&order=created_at.desc&limit=10`).catch(() => []) as Promise<any[]>,
  ]);
  const activeJip = (jips as any[]).find((j) => j.status === "active") ?? null;
  return {
    ok: true,
    card: {
      jid: o.seq, jidd: await jiddOf(o.jnl, o.seq), jnl: o.jnl, name: o.name,
      type: o.type, class: o.class, tier: o.tier, status: o.status, authority: o.authority,
      owner: o.owner ?? null, steward: o.steward ?? null,
      definition: o.definition, purpose: o.purpose, tags: o.tags,
      parent: o.parent ?? null,
      children: (children as any[]).map((c) => ({ jid: c.seq, jnl: c.jnl, name: c.name })),
      related: o.related ?? [], cross_refs: o.cross_refs ?? [], aliases: o.aliases ?? [],
      active_jip: activeJip ? { jip: activeJip.jip, version: activeJip.version, note: activeJip.note } : null,
      jips: (jips as any[]).map((j) => ({ jip: j.jip, v: j.version, status: j.status })),
      source: o.source ?? null, created: o.created, updated: o.updated, seq: o.seq,
    },
    render: "Render as a card — header 'JID N · jidd · JNL · Name', then Type/Class/Tier/Status, Definition, Purpose, Tags, Lineage (parent/children/related), Versioning, Provenance.",
    ...(rows.length > 1 ? { other_matches: rows.slice(1).map((r: any) => ({ jid: r.seq, jnl: r.jnl, name: r.name })) } : {}),
  };
}

// ── jc_recall — shared relationship memory (JC containers + SL digests, JMMS-tiered) ──
// JMMS: JSTM (session-born) → JHTM (14-day fold, compressed digest) → JLTM (durable).
// JC defaults JSTM; SL defaults JHTM. Both carry jss_status and memory_tier.
async function runJcRecall(term: string | undefined, tier: string | undefined, jss_status: string | undefined, limit = 5): Promise<Json> {
  const jcCols = "jnl,alias,session_date,subject,participants,tags,summary,keystones,decisions,open,profiles,metrics,memory_tier,jss_status,status";
  const slCols = "jnl,alias,session_date,digest,events,memory_tier,jss_status,status";
  const filter: string[] = [];
  if (tier) filter.push(`memory_tier.eq.${tier}`);
  if (jss_status) filter.push(`jss_status.eq.${jss_status}`);
  const filterStr = filter.length ? `&${filter.join("&")}` : "";
  const q = term
    ? `jc_objects?select=${jcCols}&or=(alias.eq.${term},jnl.eq.${term},subject.ilike.*${term}*)${filterStr}&limit=${limit}`
    : `jc_objects?select=${jcCols}${filterStr}&order=session_date.desc&limit=${limit}`;
  const [jcs, sls] = await Promise.all([
    rest(q).catch(() => []),
    rest(`sl_objects?select=${slCols}${filterStr}&order=session_date.desc&limit=${limit}`).catch(() => []),
  ]);
  return {
    ok: true, tier: tier ?? "all", jc: jcs, sl: sls,
    law: "JC records; it never rules — decisions cite the spine (P-C).",
    jmms: "JSTM (session-born) → JHTM (14-day fold, compressed digest) → JLTM (durable). Promotion is one-way.",
  };
}

// ── session_close — bounded autonomy JSTM commit guard ─────────────────────────
// GL6: no silent state mutation. Before a session dies (context ceiling or explicit close),
// scan JSTM memories for items that were never committed above JLTM. If any exist, write
// a HOLD artifact to JarvisMain/Implementation/tasks/ so the next session knows what was
// interrupted. DEX events captures the full audit. GL2: never autonomous self-modification.
async function runSessionClose(actor: string): Promise<Json> {
  const now = new Date().toISOString();

  // Find JSTM memories that lack a fold receipt (never promoted)
  const jstmMemories = (await rest(
    `mnemos_memories?select=id,text,tags,source,created_at&memory_tier=eq.jstm&tags=not.cs.@>{"fold:"}`,
  )) as any[];

  const needsAttention = jstmMemories.filter((m: any) =>
    !((m.tags ?? []).some((t: string) => t.startsWith("fold:") || t === "jatm"))
  );

  if (needsAttention.length === 0) {
    return { ok: true, closed: true, held: 0, note: "no JSTM items need attention — session clean" };
  }

  // Write HOLD artifact
  const holdId = `HOLD-${new Date().toISOString().slice(0, 10)}-${needsAttention.length}u`;
  const holdBody = [
    `**JSTM HOLD — bounded autonomy session close**`,
    `**Actor:** ${actor} | **Time:** ${now} | **Hold ID:** ${holdId}`,
    ``,
    `## Situation`,
    `Session is closing with ${needsAttention.length} JSTM memory item(s) that have not been committed above JLTM and lack fold receipts. Per the Governed Autonomy Contract (GOV-AUT-SPEC-0001): *any node operating under a governed autonomy contract MUST write a handoff artifact if it does not reach completion.*`,
    ``,
    `## JSTM items at risk`,
    ...needsAttention.map((m: any) =>
      `- **${m.id}** (${m.source ?? "?"}) · created ${m.created_at}: ${(m.text ?? "").slice(0, 200)}`
    ),
    ``,
    `## Decision needed`,
    `Before the next session can resume: confirm these items were handled (committed, promoted, or dismissed). Do not lose in-flight state silently.`,
    ``,
    `*Bounded autonomy: no silent exits. — GL6 + GOV-AUT-SPEC-0001*`,
  ].join("\n");

  // Write to GitHub via API
  const owner = "hurrisonferd";
  const repo  = "jarvis";
  const path  = `JarvisMain/Implementation/tasks/${holdId}.md`;
  const ghUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}`;

  let ghWriteOk = false;
  if (GITHUB_TOKEN) {
    try {
      // Check if file exists
      const existing = await fetch(ghUrl, { headers: { Authorization: `Bearer ${GITHUB_TOKEN}` } });
      const sha = existing.ok ? ((await existing.json()) as any).sha : undefined;
      const method = sha ? "PUT" : "POST";
      const wres = await fetch(ghUrl, {
        method,
        headers: { Authorization: `Bearer ${GITHUB_TOKEN}`, "Content-Type": "application/json" },
        body: JSON.stringify({ message: `HOLD: JSTM session close ${holdId} [GL6]`, content: btoa(unescape(encodeURIComponent(holdBody))), ...(sha ? { sha } : {}) }),
      });
      ghWriteOk = wres.ok;
    } catch { /* ghWriteOk stays false */ }
  }

  // Emit dex event (P5: closure by proof)
  fetch(`${SUPABASE_URL}/rest/v1/dex_events`, {
    method: "POST",
    headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${SERVICE_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ type: "bounded_autonomy.session_close", intent: `session_close.${actor}`, payload: { holdId, jstmHeld: needsAttention.length, ghWritten: ghWriteOk, actor }, source: "jarvis-action" }),
  }).catch(() => {});

  return {
    ok: true, closed: false, held: needsAttention.length,
    holdId, holdBody: ghWriteOk ? holdBody : undefined,
    note: ghWriteOk
      ? `HOLD ${holdId} written to GitHub. ${needsAttention.length} JSTM item(s) need attention before next session.`
      : `GITHUB_TOKEN not set — HOLD artifact not written. ${needsAttention.length} JSTM item(s) need attention: ${needsAttention.map((m: any) => m.id).join(", ")}`,
  };
}

// ── grimoire — the system's table of contents to itself (public raw reads) ──
async function runGrimoire(page: string | undefined): Promise<Json> {
  const LENS_FILES: Record<string, string> = {
    brief: "PORTABLE-BRIEF.md", changes: "CHANGES.md", wiring: "WIRING-MAP.md",
    health: "HEALTH.md", orphan: "ORPHAN-LENS.md", sync: "SYNC-LENS.md",
    topology: "TOPOLOGY-LENS.md", media: "MEDIA-LINKS.md",
  };
  const want = String(page || "lenses").trim().toLowerCase();
  const grab = async (f: string): Promise<string> => {
    const r = await fetch(`${RAW}/JarvisMain/yggdrasil/lal/${f}`);
    return r.ok ? await r.text() : "";
  };
  if (want === "rehydrate" || want === "omni") {
    const grimoire = await grab("GRIMOIRE.md");
    const boot = "## " + (grimoire.split("## ").slice(1).find((s) => s.toLowerCase().startsWith("boot")) ?? "");
    return {
      ok: true, page: "rehydrate",
      boot: boot.slice(0, 6000),
      changes: (await grab("CHANGES.md")).slice(0, 8000),
      health: (await grab("HEALTH.md")).slice(0, 6000),
      note: "Full catch-up: state + what changed + vitality.",
    };
  }
  if (LENS_FILES[want]) {
    const c = await grab(LENS_FILES[want]);
    if (!c) return { ok: false, page: want, note: `${LENS_FILES[want]} unreachable` };
    return { ok: true, page: want, content: c.slice(0, 48000) };
  }
  const md = await grab("GRIMOIRE.md");
  if (!md) return { ok: false, note: "GRIMOIRE.md unreachable — run seed.py to generate it." };
  const parts = md.split(/^## /m);
  const cover = parts[0]?.trim() ?? "";
  const sections = parts.slice(1).map((s) => ({ title: s.split("\n")[0].trim(), body: "## " + s }));
  const find = (kw: string) => sections.find((s) => s.title.toLowerCase().includes(kw));
  if (want === "full") return { ok: true, page: "full", grimoire: md.slice(0, 48000) };
  if (want === "lenses") {
    const lens = find("lens");
    return { ok: true, page: "lenses", cover, lenses: lens?.body ?? "(no lens section)", note: "Each lens is a chapter — a filter over the same data. Load a card with jd_resolve." };
  }
  if (want === "catalog") {
    const cat = find("catalog");
    return { ok: true, page: "catalog", catalog: (cat?.body ?? "").slice(0, 40000) };
  }
  const named = find(want);
  if (named) return { ok: true, page: named.title, section: named.body.slice(0, 20000) };
  const dom = want.toUpperCase();
  const sub = md.split(/^### /m).find((s) => s.startsWith(dom + " "));
  if (sub) return { ok: true, page: dom, table: "### " + sub.split(/^## /m)[0] };
  return { ok: false, page: want, note: "unknown page — try 'lenses', 'catalog', 'full', or a domain code (ARCH/GS/GOV/PROJ/IMPL/CONN/AUD/IDEA/LOG)." };
}

// ── JMMS — five memory horizons (JHTM added 2026-06-24). Every memory carries a tier tag
// so recall can target a horizon: JITM → JSTM → JHTM → JLTM → JATM. Promotion is ONE-WAY;
// JATM is append-only and never retagged out (mirrors HADES/git). Uses the existing tags
// array — no migration. JSTM is the project context-window: mark notes jstm to keep them in
// the working set.
const JMMS_TIERS = ["jitm", "jstm", "jhtm", "jltm", "jatm"] as const;
type Tier = typeof JMMS_TIERS[number];
function tierTag(t: unknown): Tier {
  const v = String(t ?? "jltm").toLowerCase().replace(/^#/, "");
  return (JMMS_TIERS as readonly string[]).includes(v) ? v as Tier : "jltm";
}
function withTier(tags: unknown, tier: Tier): string[] {
  const base = Array.isArray(tags)
    ? tags.map(String).filter((t) => !(JMMS_TIERS as readonly string[]).includes(t.toLowerCase()))
    : [];
  return [tier, ...base];
}
async function runJmms(action: string, a: Json, req: Request): Promise<Json> {
  const act = (action || "list").toLowerCase();
  if (act === "list") {
    const tier = tierTag(a.tier);
    const limit = Math.min(Number(a.limit ?? 20), 100);
    const rows = await rest(`mnemos_memories?select=id,source_type,text,tags,timestamp&tags=cs.{${tier}}&order=timestamp.desc&limit=${limit}`).catch(() => []);
    const notes: Record<string, string> = {
      jitm: "JITM = always-on briefing. Pointers only — what manual/fusions/focus to keep in view.",
      jstm: "JSTM = the live context-window. Mark project notes jstm to keep them in view; promote to jhtm when they consolidate.",
      jhtm: "JHTM = historical/compressed summary (14-day fold). Receipt accompanies every entry.",
      jltm: "JLTM = consolidated/durable. The default tier.",
      jatm: "JATM = ancestral/immutable. Settled lineage — never retagged out.",
    };
    return {
      ok: true, tier, count: Array.isArray(rows) ? rows.length : 0, working_set: rows,
      note: notes[tier] ?? `JMMS ${tier} tier.`,
    };
  }
  if (act === "promote" || act === "tag") {
    if (!writeAuthorized(req)) return heldForApproval(`jmms.${act}`, { id: a.id, to: a.to ?? a.tier }, req);
    const id = String(a.id ?? "");
    if (!id) return { ok: false, error: `jmms ${act} needs { id }` };
    const cur = await rest(`mnemos_memories?id=eq.${id}&select=tags`).catch(() => []) as any[];
    if (!Array.isArray(cur) || !cur.length) return { ok: false, error: `no memory ${id}` };
    const curTier = (cur[0].tags ?? []).map((t: string) => String(t).toLowerCase())
      .find((t: string) => (JMMS_TIERS as readonly string[]).includes(t)) ?? "jltm";
    const to = tierTag(a.to ?? a.tier);
    if (curTier === "jatm") return { ok: false, error: "JATM is ancestral/immutable — settled lineage is never retagged out." };
    if (act === "promote" && JMMS_TIERS.indexOf(to) < JMMS_TIERS.indexOf(curTier as Tier)) {
      return { ok: false, error: `JMMS promotion is one-way: cannot demote ${curTier} → ${to}.` };
    }
    const newTags = withTier(cur[0].tags, to);
    const r = await fetch(`${SUPABASE_URL}/rest/v1/mnemos_memories?id=eq.${id}`, {
      method: "PATCH",
      headers: { authorization: `Bearer ${SERVICE_KEY}`, apikey: SERVICE_KEY, "content-type": "application/json", Prefer: "return=minimal" },
      body: JSON.stringify({ tags: newTags }),
    });
    if (!r.ok) return { ok: false, status: r.status, error: (await r.text().catch(() => "")).slice(0, 160) };
    return { ok: true, id, moved: `${curTier} → ${to}`, tags: newTags };
  }
  return { ok: false, error: `unknown jmms action '${act}' — use list | promote | tag` };
}

// ── the dispatcher — one governed surface, {tool, args} in, plain JSON out ──
async function dispatch(tool: string, args: Json, req: Request): Promise<Json> {
  const a = args ?? {};
  switch (tool) {
    // reads — open
    case "status":
      return { system: "JARVIS", status: "OPERATIONAL", authority: "Raven commits or rejects; no autonomous self-modification", directive: "JARVIS is the priority. GameBoy is a visualizer.", transport: "OpenAPI Action (REST)" };
    case "now":
      return clockNow();
    case "recall":
      return await callFunction("mnemos-search", { query: a.query, limit: a.limit ?? 8, source_type: a.source_type ?? null, min_similarity: a.min_similarity ?? 0.35 }) as Json;
    case "query":
      return await runQuery(String(a.input ?? ""), a.prior_reply as string | undefined, a.context as Json | undefined);
    case "dex_list":
      return await callDex("jd_list", a) as Json;
    case "dex_search":
      return await callDex("jd_lookup", { term: a.term }) as Json;
    case "dex_graph":
      return await callDex("jd_graph", { jnl: a.jnl }) as Json;
    case "dex_events":
      return await callDex("events_list", a) as Json;
    case "jd_resolve":
      return await runResolve(String(a.query ?? ""));
    case "jc_recall":
      return await runJcRecall(
        a.term as string | undefined,
        a.tier as string | undefined,
        a.jss_status as string | undefined,
        (a.limit as number) ?? 5,
      );
    case "grimoire":
      return await runGrimoire(a.page as string | undefined);
    // writes — AEGIS-gated (same token as jarvis-mcp)
    case "remember":
      if (!writeAuthorized(req)) return heldForApproval("mnemos.write", { text: a.text, tags: a.tags }, req);
      // JMMS: stamp the memory's tier tag (default JLTM — the consolidated store).
      return await callFunction("mnemos-store", { ...a, tags: withTier(a.tags, tierTag(a.tier)) }) as Json;
    // JMMS — memory tiering: list a tier's working set, or move a memory up the horizon (one-way).
    case "jmms":
      return await runJmms(String(a.action ?? "list"), a, req);
    case "event":
      if (!writeAuthorized(req)) return heldForApproval("grid.event", { type: a.type, source: a.source, intent: a.intent }, req);
      return await callFunction("grid-event", a) as Json;
    // propose — rides the dex's own PROPOSE-tier ladder (stages for Raven, never commits)
    case "dex_propose":
      return await callDex("jd_propose", a, true) as Json;
    // bounded autonomy — scan JSTM for uncommitted items; write HOLD if any found
    case "session_close":
      return await runSessionClose(String(a.actor ?? "unknown"));
    default:
      return { ok: false, error: `unknown tool: ${tool}`, hint: "tools: status, now, query, recall, remember, event, jmms, dex_list, dex_search, dex_graph, dex_events, dex_propose, jd_resolve, jc_recall, grimoire, session_close" };
  }
}

const app = new Hono();

// Health/discovery.
app.get("/*", (c) =>
  c.json({
    name: "jarvis-action",
    version: "0.2.0",
    transport: "OpenAPI Action (REST) — the GPT stream's surface",
    note: "POST { tool, args } here. Reads open; writes carry JARVIS_MCP_TOKEN (x-jarvis-token); propose rides the dex PROPOSE tier.",
    tools: ["status", "now", "query", "recall", "remember", "event", "jmms", "dex_list", "dex_search", "dex_graph", "dex_events", "dex_propose", "jd_resolve", "jc_recall", "grimoire", "session_close"],
  }));

app.post("/*", async (c) => {
  let body: any = {};
  try { body = await c.req.json(); } catch { /* invalid body handled below */ }
  const tool = typeof body?.tool === "string" ? body.tool : "";
  const args = (body?.args && typeof body.args === "object") ? body.args : {};
  if (!tool) return c.json({ ok: false, error: "missing 'tool' — POST { tool, args }" }, 400);
  try {
    return c.json(await dispatch(tool, args, c.req.raw));
  } catch (err) {
    return c.json({ ok: false, tool, error: String(err).slice(0, 240) }, 502);
  }
});

Deno.serve(app.fetch);
