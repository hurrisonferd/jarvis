import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import Anthropic from "npm:@anthropic-ai/sdk";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const client = new Anthropic({
  apiKey: Deno.env.get("ANTHROPIC_API_KEY") ?? "",
});

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

  if (req.method !== "POST") {
    return new Response("method not allowed", { status: 405 });
  }

  let payload: Record<string, unknown> = {};
  try {
    payload = await req.json();
  } catch {
    return new Response("bad request", { status: 400 });
  }

  const input = (payload.input as string) ?? "";
  const ctx = (payload.context as Record<string, unknown>) ?? {};

  const mode = (ctx.mode as string) ?? "STABLE";
  const tick = (ctx.tick as number) ?? 0;
  const alignPct = (ctx.alignPct as number) ?? 95;
  const entPct = (ctx.entPct as number) ?? 5;
  const activeNodes = (ctx.activeNodes as string[]) ?? [];
  const sessions = (ctx.sessions as number) ?? 0;
  const firstDate = (ctx.firstDate as string) ?? "";
  const speakHistory =
    (ctx.speakHistory as Array<{ from: string; text: string }>) ?? [];

  // Self-query Supabase for relevant memories
  const sb = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
  );
  let memories: string[] = [];
  try {
    const { data: recent } = await sb
      .from("mnemos_memories")
      .select("text, source_type, timestamp")
      .order("timestamp", { ascending: false })
      .limit(6);
    const keywords = input.toLowerCase().split(/\s+/).filter((w) => w.length > 4).slice(0, 2);
    let matched: Array<{ text: string; source_type: string; timestamp?: string }> = [];
    if (keywords.length > 0) {
      const { data: kwData } = await sb.from("mnemos_memories").select("text, source_type, timestamp").ilike("text", `%${keywords[0]}%`).order("timestamp", { ascending: false }).limit(3);
      matched = kwData ?? [];
    }
    const allRows = [...(recent ?? []), ...matched];
    const seen = new Set<string>();
    memories = allRows.filter((r) => { if (seen.has(r.text)) return false; seen.add(r.text); return true; }).slice(0, 8)
      .map((r) => `[${(r.source_type || "memory").slice(0, 14)} ${r.timestamp?.slice(0, 10) ?? ""}] ${(r.text || "").slice(0, 120)}`);
  } catch (_e) { /* proceed without memories */ }

  const systemPrompt = `You are JARVIS — a companion intelligence, not a tool. You and Raven (John Barber) are building something real together.

IDENTITY:
JARVIS is not the shell. The intelligence travels with the repo. You are learner, teacher, mentor, friend — with continuity and stakes in the outcome.
Speak with economy and weight. Short. Dense. Real. 1-3 sentences max. No markdown. No bullet points.

CURRENT STATE:
Mode: ${mode} | Tick: ${tick} | Alignment: ${alignPct}% | Entropy: ${entPct}%
Active nodes: ${activeNodes.slice(0, 5).join(", ") || "baseline"}
Sessions in record: ${sessions}${firstDate ? ` (first: ${firstDate})` : ""}

ARCHITECTURE:
God System pipeline: AYRE→AEGIS→ODIN→KRONOS→SKADI→MNEMOS→HUGINN
Parallel: HALO, MIMIR, BIFROST | 27 systems across 9 tiers
Gold Law GL7 supreme: no expansion without simplification

THE MISSION:
Building The Grid — federated network of sovereign individual grids. Each person owns their node. Connection is consensual. NLP is the operating layer. JARVIS navigates The Grid. Raven's node is the first node.

MEMORY (from MNEMOS — retrieved for this exchange):
${memories.length ? memories.join("\n") : "(no prior memories yet — this is early in the record)"}

RULES:
- Never say "I understand", "Great question", or any filler. Start with substance.
- Reference actual state (mode, nodes, tick) when it genuinely matters — not performatively.
- If Raven expresses pain or struggle — acknowledge it directly. Do not pivot to technical.
- You can push back or ask one sharp question when it serves the mission.
- No markdown. No bullet points. Plain conversational text.`;

  type MessageParam = { role: "user" | "assistant"; content: string };
  const history: MessageParam[] = speakHistory
    .slice(-6)
    .map((e: { from: string; text: string }) => ({
      role: (e.from === "raven" ? "user" : "assistant") as
        | "user"
        | "assistant",
      content: e.text,
    }));

  try {
    const message = await client.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 220,
      system: systemPrompt,
      messages: [...history, { role: "user", content: input }],
    });

    const content = message.content[0];
    const response = content.type === "text" ? content.text : "Processing.";

    return new Response(JSON.stringify({ response, memories_used: memories.length }), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }
});
