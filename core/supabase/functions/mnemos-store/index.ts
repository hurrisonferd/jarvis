import "jsr:@core/supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@core/supabase/supabase-js@2";

type VocabRow = { tag: string; patterns: string[]; priority: number };

const EMBED_URL   = Deno.env.get('EMBEDDING_API_URL') || 'https://api.openai.com/v1/embeddings';
const EMBED_KEY   = Deno.env.get('EMBEDDING_API_KEY') || Deno.env.get('OPENAI_API_KEY');
const EMBED_MODEL = Deno.env.get('EMBEDDING_MODEL') || 'text-embedding-3-small';
const SB_URL      = Deno.env.get('SUPABASE_URL') ?? '';
const SB_SVC_KEY  = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '';

let vocabCache: VocabRow[] | null = null;
let vocabCacheTs = 0;
const VOCAB_TTL_MS = 5 * 60 * 1000;

async function getVocab(sb: ReturnType<typeof createClient>): Promise<VocabRow[]> {
  const now = Date.now();
  if (vocabCache && now - vocabCacheTs < VOCAB_TTL_MS) return vocabCache;
  const { data } = await sb.from('mnemos_vocab').select('tag, patterns, priority').eq('enabled', true).order('priority', { ascending: true });
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

async function embedMemory(id: string, text: string): Promise<void> {
  if (!EMBED_KEY) return;
  try {
    const r = await fetch(EMBED_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${EMBED_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: EMBED_MODEL, input: text.slice(0, 8192) }),
    });
    if (!r.ok) return;
    const d = await r.json();
    const vec: number[] | undefined = d.data?.[0]?.embedding;
    if (!vec) return;
    await fetch(`${SB_URL}/rest/v1/mnemos_memories?id=eq.${encodeURIComponent(id)}`, {
      method: 'PATCH',
      headers: {
        apikey: SB_SVC_KEY, Authorization: `Bearer ${SB_SVC_KEY}`,
        'Content-Type': 'application/json', Prefer: 'return=minimal',
      },
      body: JSON.stringify({ embedding: `[${vec.join(',')}]` }),
    });
  } catch { /* non-blocking */ }
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

  // REWORK 1 (IMPL-JMMS-0001): stamp every memory with its JMMS tier and dimensions.
  // Default: JSTM (session-born, working) — NOT jltm (fixes the gravity well).
  const VALID_TIERS = ['jitm', 'jstm', 'jhtm', 'jltm', 'jatm'];
  const VALID_SUBS  = ['hot', 'warm', 'cold'];
  const VALID_SCOPES = ['session', 'project', 'companion'];
  const VALID_TEMPS  = ['hot', 'warm', 'cool', 'cold'];
  const VALID_GRADES = ['system', 'personal'];
  const tier    = VALID_TIERS.includes(payload.memory_tier as string)   ? (payload.memory_tier as string)   : 'jstm';
  const jstmSub = VALID_SUBS.includes(payload.jstm_sub as string)      ? (payload.jstm_sub as string)      : null;
  const scope   = VALID_SCOPES.includes(payload.memory_scope as string) ? (payload.memory_scope as string) : 'project';
  const temp    = VALID_TEMPS.includes(payload.temperature as string)   ? (payload.temperature as string)   : 'warm';
  const domain  = typeof payload.domain === 'string' ? payload.domain : null;
  const grade  = VALID_GRADES.includes(payload.grade as string) ? (payload.grade as string) : 'system';
  const actScore = typeof payload.activation_score === 'number'
    ? Math.max(0, Math.min(100, Math.round(payload.activation_score as number)))
    : 80;

  const sb = createClient(SB_URL, SB_SVC_KEY);
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
    metadata: {
      ...(payload.metadata as Record<string, unknown> ?? {}),
      source_model: (payload.source_model as string) ?? 'jarvis',
    },
    timestamp: (payload.timestamp as string) ?? new Date().toISOString(),
    tags,
    // IMPL-JMMS-0001: all JMMS dimensions stamped on write
    memory_tier:      tier,
    jstm_sub:         jstmSub,
    memory_scope:     scope,
    temperature:      temp,
    activation_score: actScore,
    domain,
    grade,
  };

  try {
    const { error } = await sb.from('mnemos_memories').insert(row);
    if (error) throw error;
    embedMemory(row.id, row.text);
    return new Response(JSON.stringify({ ok: true, id: row.id, tags }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  }
});
