import "jsr:@core/supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@core/supabase/supabase-js@2";

// P33: same VOCAB tagger used in mnemos-store — auto-tag the query itself for re-ranking
const VOCAB: Record<string, string[]> = {
  aincrad:      ['aincrad', 'sword art', 'sao', 'kirito', 'virtual world'],
  grid_vision:  ['the grid', 'federated', 'sovereign', 'gnpl'],
  gaming:       ['gameboy', 'game boy', 'gba', 'gbc', 'rom', 'emulator', 'pachinko', 'retro', 'handheld'],
  iron_man:     ['tony stark', 'iron man', 'the suit'],
  architecture: ['ayre', 'aegis', 'odin', 'kronos', 'skadi', 'mnemos', 'huginn', 'zeus', 'chaos', 'eris',
                 'god system', 'tron', 'patch', 'gold law'],
  development:  ['patch', 'commit', 'deploy', 'edge function', 'supabase', 'github', 'migration'],
  memory:       ['remember', 'memory', 'recall', 'forget', 'history', 'record'],
  emotional:    ['difficult', 'struggle', 'pain', 'proud', 'frustrated', 'worth', 'meaning', 'purpose'],
  family:       ['wife', 'kids', 'children', 'family', 'home'],
  projects:     ['pachinko', 'codeos', 'flag-01', 'clarkson', 'godot'],
  mission:      ['mission', 'vision', 'build', 'future', 'dream', 'companion'],
  identity:     ['raven', 'john barber', 'companion', 'jarvis'],
  governance:   ['authority', 'governor', 'gnpl', 'consensus', 'proposal', 'zeus'],
};

function autoTagQuery(text: string): string[] {
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

  const query      = ((payload.query as string) ?? "").slice(0, 200).trim();
  const limit      = Math.min((payload.limit as number) ?? 10, 20);
  const sourceType = (payload.source_type as string) ?? "";
  const tags       = (payload.tags as string[]) ?? [];
  // REWORK 2 (MEDIUM): JLTM recall path — filter by memory_tier for tier-specific retrieval.
  // Valid tiers: jitm | jstm | jhtm | jltm | jatm.
  const VALID_TIERS = ['jitm', 'jstm', 'jhtm', 'jltm', 'jatm'];
  const VALID_GRADES = ['system', 'personal'];
  const memoryTier  = VALID_TIERS.includes((payload.memory_tier as string) ?? "")
    ? (payload.memory_tier as string)
    : null;
  // IMPL-JMMS-0001: grade filter — default to system (JARVIS's knowledge) unless specified.
  const grade = VALID_GRADES.includes((payload.grade as string) ?? "")
    ? (payload.grade as string)
    : null;

  const sb = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
  );

  try {
    let data: unknown[] = [];

    if (query.length > 0) {
      // P33: full-text ranked search via tsvector + tag overlap re-ranking
      // IMPL-JMMS-0001: include JMMS columns in select, filter by grade if provided
      let q = sb.from("mnemos_memories")
        .select("id, text, source_type, timestamp, metadata, entropy, tags, memory_tier, memory_scope, temperature, activation_score, domain, grade");
      if (memoryTier) q = q.eq("memory_tier", memoryTier);
      if (grade) q = q.eq("grade", grade);
      const { data: ftData, error: ftErr } = await q
        .textSearch("tsv", query, { type: "plain", config: "english" })
        .order("timestamp", { ascending: false })
        .limit(limit * 2);

      if (ftErr) throw ftErr;

      // Re-rank: memories whose tags overlap with auto-tagged query score higher
      const queryTags = autoTagQuery(query);
      const ranked = (ftData ?? []).map(r => {
        const row = r as Record<string, unknown>;
        const rowTags = (row.tags as string[]) ?? [];
        const overlap = queryTags.filter(t => rowTags.includes(t)).length;
        return { ...row, _score: overlap };
      }).sort((a, b) => (b._score as number) - (a._score as number));

      data = ranked.slice(0, limit);

    } else if (tags.length > 0) {
      // P33: tag-only search — memories with overlapping tags
      // IMPL-JMMS-0001: include JMMS columns in select, filter by grade if provided
      let q = sb.from("mnemos_memories")
        .select("id, text, source_type, timestamp, metadata, entropy, tags, memory_tier, memory_scope, temperature, activation_score, domain, grade");
      if (memoryTier) q = q.eq("memory_tier", memoryTier);
      if (grade) q = q.eq("grade", grade);
      const { data: tagData, error: tagErr } = await q
        .overlaps("tags", tags)
        .order("timestamp", { ascending: false })
        .limit(limit);

      if (tagErr) throw tagErr;
      data = tagData ?? [];

    } else {
      // No query, no tags — recency fallback (optionally tier-filtered)
      // IMPL-JMMS-0001: include JMMS columns in select, filter by grade if provided
      let q = sb
        .from("mnemos_memories")
        .select("id, text, source_type, timestamp, metadata, entropy, tags, memory_tier, memory_scope, temperature, activation_score, domain, grade")
        .order("timestamp", { ascending: false });
      if (memoryTier) q = q.eq("memory_tier", memoryTier);
      if (grade) q = q.eq("grade", grade);
      if (sourceType) q = q.eq("source_type", sourceType);
      const { data: recent, error: recErr } = await q.limit(limit);
      if (recErr) throw recErr;
      data = recent ?? [];
    }

    return new Response(
      JSON.stringify({ memories: data, total: data.length }),
      {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err), memories: [] }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }
});
