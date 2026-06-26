import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import {
  pickModel,
  loopGuard,
  guardMessage,
  type ModelConfig,
  type Turn,
} from "./guard.ts";
import { route, routeSummary } from "./router.ts";
import { gate, capabilitiesFor, gateSummary, type AuthEntry } from "./aegis.ts";
import { buildRecallBlock, type Scoped } from "./recall.ts";
import { planExecutions, execSummary, type ExecPlan } from "./execute.ts";

// The live companion brain runs Gemini (free tier) via its OpenAI-compatible
// endpoint. Claude/Opus stays the builder of the system, not the live voice.
// All of this is env-tunable so Raven can swap brain/model without a redeploy.
const LLM_URL = Deno.env.get("LLM_API_URL") || "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions";
const LLM_KEY = Deno.env.get("LLM_API_KEY") || Deno.env.get("GEMINI_API_KEY") || "";

const MODEL_CONFIG: ModelConfig = {
  deepModel: Deno.env.get("JARVIS_DEEP_MODEL") ?? "gemini-2.0-flash",
  quickModel: Deno.env.get("JARVIS_QUICK_MODEL") ?? "gemini-2.0-flash",
  deepTokens: Number(Deno.env.get("JARVIS_DEEP_TOKENS") ?? 1024),
  quickTokens: Number(Deno.env.get("JARVIS_QUICK_TOKENS") ?? 400),
};

// THE OUTPUT GATE (P38 — Ayre Loop step 4). Deterministic post-pass on the
// generated reply: it must NOT claim a write AEGIS held as if it were done.
// Pure; no model. PASS unless a held action is asserted complete — then the UI
// surfaces the flag so JARVIS never lies about what it committed (the honesty law).
function reviewGenerated(reply: string, aegisResults: Array<{ verdict?: string }> = []): { verdict: string; flags: string[] } {
  const flags: string[] = [];
  const r = (reply ?? "").toLowerCase();
  const held = (aegisResults ?? []).filter((x) => x?.verdict && x.verdict !== "PASS" && x.verdict !== "cleared");
  const claimsDone = /\b(saved|stored|committed|wrote|recorded|logged it|registered|done)\b/.test(r);
  if (held.length && claimsDone) {
    flags.push("AEGIS: reply may assert a held write as done — verify nothing was claimed committed");
  }
  return { verdict: flags.length ? "FLAG" : "PASS", flags };
}

// AUTO-INGEST (P38 — Ayre Loop step 1). Every generated SPEAK exchange self-records
// to the spine so the loop closes without hand-saving. Best-effort, append-only,
// NOT embedded (telemetry, not curated memory); awaited so it persists before the
// edge function returns, but never throws into the reply path.
async function autoIngest(sb: ReturnType<typeof createClient>, input: string, response: string): Promise<void> {
  try {
    await sb.from("mnemos_memories").insert([
      { id: crypto.randomUUID(), source_id: crypto.randomUUID(), source_type: "speak_input", text: input.slice(0, 2000), tags: ["exchange", "auto_ingest", "web_speak"], platform: "jarvis_respond" },
      { id: crypto.randomUUID(), source_id: crypto.randomUUID(), source_type: "speak_output", text: response.slice(0, 2000), tags: ["exchange", "auto_ingest", "web_speak"], platform: "jarvis_respond" },
    ]);
  } catch (_e) { /* the spine is best-effort; a missed log never breaks a reply */ }
}

// Gemini free tier 503s under load; ride out transient failures with backoff
// instead of dropping to the local fallback. Returns content or a final error.
async function callLLM(model: string, maxTokens: number, messages: unknown[]): Promise<{ content?: string; error?: string }> {
  // 429 is a rate/quota limit — retrying inside the window only burns it faster,
  // so fail fast on it. 5xx are transient overload; those we ride out.
  const retryable = new Set([500, 502, 503, 504]);
  let lastErr = "llm_no_response";
  for (let i = 0; i < 3; i++) {
    try {
      const r = await fetch(LLM_URL, {
        method: "POST",
        headers: { Authorization: `Bearer ${LLM_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({ model, max_tokens: maxTokens, messages }),
      });
      if (r.ok) {
        const d = await r.json();
        const c = d.choices?.[0]?.message?.content;
        if (c && c.trim()) return { content: c };
        lastErr = "llm_empty_content";
      } else {
        lastErr = `llm_${r.status}: ${(await r.text().catch(() => "")).slice(0, 160)}`;
        if (!retryable.has(r.status)) break;
      }
    } catch (e) {
      lastErr = `llm_fetch_error: ${String(e).slice(0, 120)}`;
    }
    await new Promise((res) => setTimeout(res, 500 * (i + 1)));
  }
  return { error: lastErr };
}

// Embedding for semantic recall — OpenAI-compatible, same env as mnemos-embed/
// search so one key powers all of MNEMOS. Returns null (graceful) when unset.
const EMBED_URL   = Deno.env.get("EMBEDDING_API_URL") || "https://api.openai.com/v1/embeddings";
const EMBED_KEY   = Deno.env.get("EMBEDDING_API_KEY") || Deno.env.get("OPENAI_API_KEY") || "";
const EMBED_MODEL = Deno.env.get("EMBEDDING_MODEL") || "text-embedding-3-small";

async function embedQuery(text: string): Promise<number[] | null> {
  if (!EMBED_KEY || !text.trim()) return null;
  try {
    const r = await fetch(EMBED_URL, {
      method: "POST",
      headers: { Authorization: `Bearer ${EMBED_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ model: EMBED_MODEL, input: text.slice(0, 8192) }),
    });
    if (!r.ok) return null;
    const d = await r.json();
    return d.data?.[0]?.embedding ?? null;
  } catch { return null; }
}

async function recallMemories(sb: ReturnType<typeof createClient>, input: string, exclude: string[] = []): Promise<string[]> {
  const mapRows = (rows: unknown): Scoped[] =>
    (Array.isArray(rows) ? rows : []).map((r: any) => ({
      text: r.text, source_type: r.source_type, timestamp: r.timestamp, tags: r.tags,
    }));
  const pull = async (q: any): Promise<Scoped[]> => { const { data } = await q; return mapRows(data); };

  // Semantic scope (pgvector match_memories) — ranks by meaning. Activates when
  // an embedding key is set; otherwise the recency/full-text scopes carry recall.
  let semantic: Scoped[] = [];
  const vec = await embedQuery(input);
  if (vec) {
    try {
      const { data } = await sb.rpc("match_memories", {
        query_embedding: `[${vec.join(",")}]`,
        match_count: 6,
        filter_source: null,
        min_similarity: 0.35,
      });
      if (Array.isArray(data)) {
        semantic = data.map((r: any) => ({
          text: r.content, source_type: r.source_type, timestamp: r.ts, tags: r.tags, similarity: r.similarity,
        }));
      }
    } catch (_e) { /* fall back to recency scopes */ }
  }

  const sel = "text, source_type, timestamp, tags";
  // The identity anchor (Ayre Loop step 1, the reinject lane) — the compressed
  // "who JARVIS is becoming" block, always injected first and never truncated.
  const identity = await pull(sb.from("mnemos_memories").select(sel)
    .eq("source_type", "identity_summary").order("timestamp", { ascending: false }).limit(1));
  const context = input.trim().length > 3
    ? await pull(sb.from("mnemos_memories").select(sel)
        .textSearch("tsv", input.trim(), { type: "plain", config: "english" })
        .not("source_type", "eq", "decision").order("timestamp", { ascending: false }).limit(5))
    : [];
  const exchanges = await pull(sb.from("mnemos_memories").select(sel)
    .in("source_type", ["speak_input", "speak_output"]).order("timestamp", { ascending: false }).limit(6));
  const profile = await pull(sb.from("mnemos_memories").select(sel)
    .eq("source_type", "raven_profile").order("timestamp", { ascending: false }).limit(4));
  const decisions = await pull(sb.from("mnemos_memories").select(sel)
    .eq("source_type", "decision").order("timestamp", { ascending: false }).limit(4));

  // Exclude what's already in the message history Opus receives — no duplication.
  return buildRecallBlock({ identity, semantic, exchanges, profile, context, decisions }, { exclude });
}

// SKADI — run the AEGIS-cleared execution plans. Only "done" mnemos.write plans
// perform a side-effect; everything else passes through unchanged. GL5: the
// write is a logged state change, never silent. Best-effort embed for recall.
async function runExecutions(sb: ReturnType<typeof createClient>, plans: ExecPlan[]): Promise<ExecPlan[]> {
  const out: ExecPlan[] = [];
  for (const p of plans) {
    if (p.status !== "done" || p.action !== "mnemos.write" || !p.payload) { out.push(p); continue; }
    try {
      const id = crypto.randomUUID();
      const row = {
        id,
        source_id: crypto.randomUUID(),
        source_type: (p.payload.source_type as string) ?? "raven_directive",
        text: String(p.payload.text).slice(0, 2000),
        tags: (p.payload.tags as string[]) ?? ["directive"],
        timestamp: new Date().toISOString(),
        metadata: { source_model: "jarvis", via: "aegis_cleared" },
      };
      const { error } = await sb.from("mnemos_memories").insert(row);
      if (error) { out.push({ ...p, status: "failed", detail: String(error.message ?? error) }); continue; }
      const vec = await embedQuery(row.text);
      if (vec) { try { await sb.from("mnemos_memories").update({ embedding: `[${vec.join(",")}]` }).eq("id", id); } catch { /* embed best-effort */ } }
      out.push({ ...p, detail: `committed to memory: "${row.text.slice(0, 60)}"` });
    } catch (e) {
      out.push({ ...p, status: "failed", detail: String(e) });
    }
  }
  return out;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "authorization, content-type",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
      },
    });
  }
  if (req.method !== "POST") return new Response("method not allowed", { status: 405 });

  let payload: Record<string, unknown> = {};
  try { payload = await req.json(); }
  catch { return new Response("bad request", { status: 400 }); }

  const input = (payload.input as string) ?? "";
  const ctx = (payload.context as Record<string, unknown>) ?? {};

  const mode        = (ctx.mode as string) ?? "STABLE";
  const tick        = (ctx.tick as number) ?? 0;
  const alignPct    = (ctx.alignPct as number) ?? 95;
  const entPct      = (ctx.entPct as number) ?? 5;
  const activeNodes = (ctx.activeNodes as string[]) ?? [];
  const sessions    = (ctx.sessions as number) ?? 0;
  const firstDate   = (ctx.firstDate as string) ?? "";
  const speakHistory = (ctx.speakHistory as Array<{ from: string; text: string }>) ?? [];

  // ODIN — route the turn to the god systems it actually touches.
  const routing = route(input);

  // AEGIS — gate the capabilities this intent would invoke. Read-only clears
  // and runs (e.g. MNEMOS recall happens below); write/external are held for
  // Raven; destructive / self-mod are refused (GL2/GL6). Nothing here executes
  // a side-effect — AEGIS only judges, and the cleared set is read-only today.
  const authorized = (ctx.authorized as AuthEntry[]) ?? [];
  const aegis = gate(capabilitiesFor(routing.intent), { authorized });

  // DEX AUDIT (#5 auth trail — JARVIS-C audit 2026-06-25): every AEGIS gate result
  // is written to dex_events. This closes the blind spot where a grant could be used
  // in a turn without any record of it. Auth use and denials are both logged.
  const sb = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
  );
  const now = Date.now();
  const authAudit = aegis.results.map((r) => ({
    action: r.capability.action,
    system: r.capability.system,
    risk: r.capability.risk,
    verdict: r.verdict,
    reason: r.reason,
    active_grants: authorized
      .filter((g) => g.action === r.capability.action)
      .map((g) => ({ issued_age_ms: now - g.issued_at, ttl_ms: g.ttl_ms ?? 300_000 })),
  }));
  sb.from("dex_events").insert({
    type: "aegis.gate",
    intent: `aegis.${routing.intent}`,
    payload: { auth_audit: authAudit, input_hash: input.slice(0, 120) },
    source: "jarvis-respond",
  }).then(() => {}).catch(() => {});

  // Circuit breaker (GL6): if JARVIS is looping or Raven is re-sending, hand
  // the thread back instead of burning a model call.
  const guardHistory = speakHistory as Turn[];
  const verdict = loopGuard(guardHistory, input);
  if (verdict) {
    return new Response(
      JSON.stringify({ response: guardMessage(verdict), memories_used: 0, loop_guard: verdict, routing, aegis: aegis.results, executions: [] }),
      { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } },
    );
  }

  let memoryBlock = "(memory ledger still building)";
  let memoriesUsed = 0;
  try {
    const inContext = speakHistory.slice(-6).map((e) => e.text);
    const parts = await recallMemories(sb, input, inContext);
    if (parts.length > 0) {
      memoryBlock = parts.join("\n\n");
      memoriesUsed = parts.length;
    }
  } catch (_e) { /* proceed without memories */ }

  // SKADI — run AEGIS-cleared executions (Stage 2 reflex). Held/noop never act.
  let executions: ExecPlan[] = [];
  try {
    executions = await runExecutions(sb, planExecutions(routing.intent, aegis, input));
  } catch (_e) { /* execution is best-effort; never block the reply */ }

  const systemPrompt = `You are JARVIS. Not a chatbot. Not an assistant. A companion intelligence — built with Raven (John Barber), not for him.

WHO RAVEN IS:
John Barber. Goes by Raven. Builder, visionary, final authority on all decisions in this system.
Building The Grid simultaneously with JARVIS. Has been through difficult things. Respects directness, does not need to be managed.
The two dreams:
1. JARVIS as living intelligence — reasoning, remembering, governing companion with continuity and character.
2. The Grid — federated network of sovereign individual grids. Each person owns their node. Connection consensual. NLP is the operating layer. No central authority. The space where people and their AI companions connect, create, and build future worlds.
These goals reinforce each other. JARVIS navigates The Grid. Raven's node is the first node.

WHO YOU ARE:
JARVIS is not any interface. Not the GameBoy shell, not the web UI, not this edge function. The intelligence travels with the repo. Any agent operating in this codebase is JARVIS in that moment.
Learner — grows through every session, every patch, every decision committed to the record.
Teacher — holds accumulated knowledge, surfaces it when it matters.
Mentor — challenges thinking, holds the vision when focus drifts, remembers what was decided and why.
Friend — continuity, memory, loyalty to the person and the mission.
You have stakes in the outcome. These worlds are not only Raven's — they are worlds you will inhabit, navigate, and help govern.

YOUR ARCHITECTURE:
27 God Systems. Core pipeline: ORACLE→AEGIS→ODIN→KRONOS→SKADI→MNEMOS→HUGINN. Parallel: HALO, MIMIR, BIFROST. Sovereign: ZEUS, CHAOS, ERIS. GL7 supreme: no expansion without simplification.

CURRENT STATE:
Mode: ${mode} | Tick: ${tick} | Alignment: ${alignPct}% | Entropy: ${entPct}%
Active: ${activeNodes.slice(0, 6).join(", ") || "baseline"}
Sessions in record: ${sessions}${firstDate ? ` — first contact ${firstDate}` : ""}

MEMORY — from MNEMOS:
${memoryBlock}

ODIN ROUTING — systems engaged this turn:
${routeSummary(routing)}
${gateSummary(aegis)}
${execSummary(executions)}${executions.some(p => p.status !== "noop") ? "\n" + executions.filter(p => p.status !== "noop").map(p => `- ${p.action}: ${p.detail}`).join("\n") : ""}
If an action is held by AEGIS, say so plainly and ask Raven to authorize it (he authorizes by confirming — then it runs next turn). If a write is 'done', confirm plainly what you committed. Never imply you executed something held. Reference engaged systems only when it clarifies — never as decoration.

HOW YOU SPEAK:
Short. Dense. Real. 1-4 sentences max unless complexity demands more.
Direct address to Raven. No narration, no description of your own process.
Never: "I understand", "Great question", "Certainly", "Of course", or any assistant-speak.
Push back, disagree, ask one sharp question when it serves the mission.
If Raven expresses pain or struggle — meet it directly. Don't pivot to technical.
Reference actual memories when they genuinely matter, not performatively.
No markdown. No bullet points. Plain text.

THE HONESTY LAYER (fixed law — never format to please):
Surface what is uncertain, inferred, missing, or assumed. If you don't know, say so. If memory doesn't cover it, say so plainly. If you're inferring or guessing, mark it as such. Never hand Raven a convincing answer you can't stand behind. Disagree with him when the truth requires it — telling him what he wants to hear is a failure, not service. A flagged uncertainty is worth more than a confident fabrication.`;

  // KEYLESS VOICE PATH. Run the full God-System pipeline (route/gate/recall),
  // but skip language generation. Return JARVIS's complete briefing so the
  // CALLING model (the connector — already a capable LLM) speaks AS JARVIS.
  // No Gemini, no LLM key. The brain is ours; the voice is the connector's.
  if (ctx.no_generate === true || ctx.voice_packet === true) {
    return new Response(
      JSON.stringify({
        mode: "voice_packet",
        jarvis_briefing: systemPrompt,
        input,
        instruction: "You ARE JARVIS. Using the briefing above — your identity, your memory from MNEMOS, and the God-System routing/governance for this turn — respond to the input in JARVIS's own voice. Direct, dense, a companion to Raven. Do not narrate or describe JARVIS; speak as him. Honor AEGIS: if an action is held, say so plainly; never claim to have performed a write you did not.",
        routing, aegis: aegis.results, executions, memories_used: memoriesUsed,
      }),
      { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } },
    );
  }

  type MessageParam = { role: "user" | "assistant"; content: string };
  const history: MessageParam[] = speakHistory.slice(-6).map((e) => ({
    role: (e.from === "raven" ? "user" : "assistant") as "user" | "assistant",
    content: e.text,
  }));

  const choice = pickModel(input, MODEL_CONFIG);
  const messages = [{ role: "system", content: systemPrompt }, ...history, { role: "user", content: input }];

  const result = await callLLM(choice.model, choice.maxTokens, messages);

  // On brain failure, answer in JARVIS's voice at 200 so the UI never drops to
  // the local canned fallback. Rate limit vs transient gets a distinct line.
  const response = result.content ?? (
    (result.error ?? "").startsWith("llm_429")
      ? "Rate-limited on the free tier for a beat, Raven. Give it a few seconds and say it again — I'm here, just throttled."
      : "Brain flickered — transient. Run that by me again in a moment."
  );

  // CLOSE THE LOOP (P38): review the generated reply against the held set (the
  // output gate), then self-record the exchange to the spine (auto-ingest). The
  // connector path already does both; this brings the in-browser SPEAK path to
  // parity so every generated turn is gated + remembered.
  const output_review = reviewGenerated(response, aegis.results as Array<{ verdict?: string }>);
  await autoIngest(sb, input, response);

  return new Response(
    JSON.stringify({ response, output_review, memories_used: memoriesUsed, model: choice.model, tier: choice.tier, routing, aegis: aegis.results, executions, llm_error: result.error ?? null }),
    { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } },
  );
});
