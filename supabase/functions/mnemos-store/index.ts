import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

type VocabRow = { tag: string; patterns: string[]; priority: number };

// P33+: vocab loaded from mnemos_vocab table at runtime — no deploy needed to add tags
let vocabCache: VocabRow[] | null = null;
let vocabCacheTs = 0;
const VOCAB_TTL_MS = 5 * 60 * 1000; // refresh every 5 minutes

async function getVocab(sb: ReturnType<typeof createClient>): Promise<VocabRow[]> {
  const now = Date.now();
  if (vocabCache && now - vocabCacheTs < VOCAB_TTL_MS) return vocabCache;
  const { data } = await sb
    .from('mnemos_vocab')
    .select('tag, patterns, priority')
    .eq('enabled', true)
    .order('priority', { ascending: true });
  vocabCache = (data ?? []) as VocabRow[];
  vocabCacheTs = now;
  return vocabCache;
}

function tagText(text: string, vocab: VocabRow[]): string[] {
  const lower = text.toLowerCase();
  const tags: string[] = [];
  for (const { tag, patterns } of vocab) {
    if (patterns.some(p => lower.includes(p.toLowerCase()))) tags.push(tag);
  }
  return tags;
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, content-type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
      },
    });
  }
  if (req.method !== 'POST') return new Response('method not allowed', { status: 405 });

  let payload: Record<string, unknown> = {};
  try { payload = await req.json(); } catch { return new Response('bad request', { status: 400 }); }

  const text = ((payload.text as string) ?? '').trim();
  if (!text) return new Response(JSON.stringify({ error: 'text required' }), {
    status: 400, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
  });

  const sb = createClient(Deno.env.get('SUPABASE_URL') ?? '', Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '');

  const vocab = await getVocab(sb);
  const autoTags = tagText(text, vocab);
  const callerTags = (payload.tags as string[]) ?? [];
  const tags = [...new Set([...autoTags, ...callerTags])];

  const row = {
    id: crypto.randomUUID(),
    source_id: crypto.randomUUID(),
    source_type: (payload.source_type as string) ?? 'speak_input',
    text: text.slice(0, 2000),
    entropy: (payload.entropy as number) ?? 0.05,
    platform: (payload.platform as string) ?? 'claude_code_cli',
    metadata: (payload.metadata as Record<string, unknown>) ?? {},
    timestamp: (payload.timestamp as string) ?? new Date().toISOString(),
    tags,
  };

  try {
    const { error } = await sb.from('mnemos_memories').insert(row);
    if (error) throw error;
    return new Response(JSON.stringify({ ok: true, id: row.id, tags }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  }
});
