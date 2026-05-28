import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// P33: JARVIS structural tagger — controlled vocabulary, no external deps
// Maps text patterns to semantic tags. Vocabulary grows as JARVIS learns Raven's world.
const VOCAB: Record<string, string[]> = {
  aincrad:      ['aincrad', 'sword art online', ' sao ', 'kirito', 'virtual world'],
  grid_vision:  ['the grid', 'federated', 'sovereign node', 'gnpl', 'each person owns'],
  gaming:       ['gameboy', 'game boy', ' gba', ' gbc', ' rom ', 'emulator', 'pachinko', 'retro', 'handheld'],
  iron_man:     ['tony stark', 'iron man', 'the suit', 'tony and jarvis'],
  architecture: ['ayre', 'aegis', 'odin', 'kronos', 'skadi', 'mnemos', 'huginn', 'zeus', 'chaos', 'eris',
                 'halo', 'mimir', 'bifrost', 'atlas', 'athena', 'prometheus', 'apollo', 'loki', 'argus',
                 'janus', 'dante', 'iris', 'meridian', 'hades', 'poseidon', 'nemesis', 'hermes',
                 'god system', 'tron layer', 'l0 ', 'l6 ', 'l7 ', 'patch ledger', 'gold law', 'gl7'],
  development:  ['patch', 'commit', 'deploy', 'pull request', 'edge function', 'supabase', 'github',
                 'migration', 'typescript', 'python', 'javascript', 'sql'],
  memory:       ['remember', 'memory', 'recall', 'forget', 'mnemos', 'history', 'record', 'continuity'],
  emotional:    ['difficult', 'struggle', 'pain', 'proud', 'frustrated', 'hard time', 'worth it',
                 'meaning', 'purpose', 'lonely', 'grateful', 'hope'],
  family:       ['wife', 'kids', 'children', 'family', 'home', 'son', 'daughter'],
  projects:     ['pachinko', 'codeos', 'flag-01', 'clarkson', 'eeoc', 'godot'],
  mission:      ['mission', 'vision', 'build together', 'future world', 'the dream', 'companion'],
  speak:        ['[raven]', '[jarvis]', 'speak exchange', 'companion exchange'],
  identity:     ['raven', 'john barber', 'companion intelligence', 'jarvis identity', 'living intelligence'],
  governance:   ['authority', 'governor', 'gnpl', 'consensus', 'proposal', 'commit', 'reject', 'zeus arbitrat'],
};

function tagText(text: string): string[] {
  const lower = text.toLowerCase();
  const tags: string[] = [];
  for (const [tag, patterns] of Object.entries(VOCAB)) {
    if (patterns.some(p => lower.includes(p))) tags.push(tag);
  }
  return tags;
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

  if (req.method !== "POST") {
    return new Response("method not allowed", { status: 405 });
  }

  let payload: Record<string, unknown> = {};
  try {
    payload = await req.json();
  } catch {
    return new Response("bad request", { status: 400 });
  }

  const text = ((payload.text as string) ?? "").trim();
  if (!text) {
    return new Response(JSON.stringify({ error: "text required" }), {
      status: 400,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }

  const sb = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
  );

  const id = crypto.randomUUID();
  const source_id = crypto.randomUUID();

  // P33: auto-tag on insert — JARVIS classifies the memory
  const autoTags = tagText(text);
  const callerTags = (payload.tags as string[]) ?? [];
  const tags = [...new Set([...autoTags, ...callerTags])];

  const row = {
    id,
    source_id,
    source_type: (payload.source_type as string) ?? "speak_input",
    text: text.slice(0, 2000),
    entropy: (payload.entropy as number) ?? 0.05,
    platform: (payload.platform as string) ?? "claude_code_cli",
    metadata: (payload.metadata as Record<string, unknown>) ?? {},
    timestamp: (payload.timestamp as string) ?? new Date().toISOString(),
    tags,
    // tsv is auto-updated by DB trigger
  };

  try {
    const { error } = await sb.from("mnemos_memories").insert(row);
    if (error) throw error;
    return new Response(JSON.stringify({ ok: true, id, tags }), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }
});
