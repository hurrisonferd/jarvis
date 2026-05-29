// mnemos-search: semantic memory search (pgvector cosine similarity)
// Falls back to PostgreSQL full-text search (tsv) when no API key is set
// OpenAI-compatible — works with OpenAI, Voyage AI, Cohere, etc.
// Env vars: EMBEDDING_API_KEY, EMBEDDING_API_URL, EMBEDDING_MODEL

const EMBED_URL   = Deno.env.get('EMBEDDING_API_URL') || 'https://api.openai.com/v1/embeddings';
const EMBED_KEY   = Deno.env.get('EMBEDDING_API_KEY') || Deno.env.get('OPENAI_API_KEY');
const EMBED_MODEL = Deno.env.get('EMBEDDING_MODEL') || 'text-embedding-3-small';
const SB_URL      = Deno.env.get('SUPABASE_URL')!;
const SB_KEY      = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type',
};

async function embed(text: string): Promise<number[] | null> {
  if (!EMBED_KEY) return null;
  try {
    const r = await fetch(EMBED_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${EMBED_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: EMBED_MODEL, input: text.slice(0, 8192) }),
    });
    if (!r.ok) return null;
    const d = await r.json();
    return d.data?.[0]?.embedding ?? null;
  } catch { return null; }
}

async function fulltextSearch(
  query: string, limit: number, sourceType: string | null
): Promise<{ results: unknown[]; method: string }> {
  const tsQuery = query.trim().split(/\s+/).filter(Boolean).join(' & ');
  let url = `${SB_URL}/rest/v1/mnemos_memories`
    + `?select=id,source_id,source_type,text,timestamp,metadata,tags`
    + `&limit=${limit}&order=timestamp.desc`;
  if (tsQuery) url += `&tsv=fts.${encodeURIComponent(tsQuery)}`;
  if (sourceType) url += `&source_type=eq.${encodeURIComponent(sourceType)}`;
  const r = await fetch(url, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } });
  const rows: Record<string, unknown>[] = await r.json().catch(() => []);
  if (!rows?.length) {
    const fallUrl = `${SB_URL}/rest/v1/mnemos_memories?select=id,source_id,source_type,text,timestamp,metadata,tags&limit=${limit}&order=timestamp.desc`
      + (sourceType ? `&source_type=eq.${encodeURIComponent(sourceType)}` : '');
    const fallR = await fetch(fallUrl, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } });
    const fallRows: Record<string, unknown>[] = await fallR.json().catch(() => []);
    return { results: (fallRows || []).map(row => ({ ...row, similarity: null })), method: 'recent' };
  }
  return { results: rows.map(row => ({ ...row, similarity: null })), method: 'fulltext' };
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });

  const body = await req.json().catch(() => ({}));
  const jsonH = { 'Content-Type': 'application/json', ...CORS };
  const { query, limit = 10, source_type = null, min_similarity = 0.0 } = body;

  if (!query) return new Response(JSON.stringify({ error: 'query required' }), { status: 400, headers: jsonH });

  const vec = await embed(query);

  if (!vec) {
    const fallback = await fulltextSearch(query, limit, source_type);
    return new Response(JSON.stringify({ ...fallback, query }), { headers: jsonH });
  }

  const rpcRes = await fetch(`${SB_URL}/rest/v1/rpc/match_memories`, {
    method: 'POST',
    headers: {
      apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`,
      'Content-Type': 'application/json', Prefer: 'return=representation',
    },
    body: JSON.stringify({
      query_embedding: `[${vec.join(',')}]`,
      match_count: limit,
      filter_source: source_type,
      min_similarity,
    }),
  });

  if (!rpcRes.ok) {
    const fallback = await fulltextSearch(query, limit, source_type);
    return new Response(JSON.stringify({ ...fallback, query, fallback_reason: 'rpc_error' }), { headers: jsonH });
  }

  const raw: Record<string, unknown>[] = await rpcRes.json();
  const results = raw.map(r => ({
    id: r.id, source_id: r.source_id, source_type: r.source_type,
    text: r.content, timestamp: r.ts,
    metadata: r.metadata, tags: r.tags, similarity: r.similarity,
  }));
  return new Response(
    JSON.stringify({ results, method: 'semantic', query, dims: vec.length }),
    { headers: jsonH }
  );
});
