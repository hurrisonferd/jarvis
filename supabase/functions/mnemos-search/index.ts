// mnemos-search: semantic memory search via pgvector cosine similarity
// Falls back to ILIKE keyword search when no API key is present
// Provider: Jina AI jina-embeddings-v2-base-en (768 dims)
// Set JINA_API_KEY (or EMBEDDING_API_KEY) in Supabase edge function secrets

const JINA_KEY = Deno.env.get('JINA_API_KEY') || Deno.env.get('EMBEDDING_API_KEY');
const SB_URL   = Deno.env.get('SUPABASE_URL')!;
const SB_KEY   = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type',
};

async function embed(text: string): Promise<number[] | null> {
  if (!JINA_KEY) return null;
  try {
    const r = await fetch('https://api.jina.ai/v1/embeddings', {
      method: 'POST',
      headers: { Authorization: `Bearer ${JINA_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'jina-embeddings-v2-base-en', input: [text.slice(0, 8192)] }),
    });
    if (!r.ok) return null;
    const d = await r.json();
    return d.data?.[0]?.embedding ?? null;
  } catch { return null; }
}

async function keywordSearch(
  query: string, limit: number, sourceType: string | null
): Promise<{ results: unknown[]; method: string }> {
  const word = query.split(/\s+/).find(w => w.length > 2) || query.slice(0, 20);
  let url = `${SB_URL}/rest/v1/mnemos_memories?select=id,source_id,source_type,text,timestamp,metadata,tags`
    + `&text=ilike.*${encodeURIComponent(word)}*&limit=${limit}&order=timestamp.desc`;
  if (sourceType) url += `&source_type=eq.${encodeURIComponent(sourceType)}`;
  const r = await fetch(url, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } });
  const rows: Record<string, unknown>[] = await r.json();
  return {
    results: (rows || []).map(row => ({ ...row, similarity: null })),
    method: 'keyword',
  };
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });

  const body = await req.json().catch(() => ({}));
  const jsonH = { 'Content-Type': 'application/json', ...CORS };
  const { query, limit = 10, source_type = null, min_similarity = 0.0 } = body;

  if (!query) return new Response(JSON.stringify({ error: 'query required' }), { status: 400, headers: jsonH });

  const vec = await embed(query);

  if (!vec) {
    const fallback = await keywordSearch(query, limit, source_type);
    return new Response(JSON.stringify({ ...fallback, query }), { headers: jsonH });
  }

  const rpcRes = await fetch(`${SB_URL}/rest/v1/rpc/match_memories`, {
    method: 'POST',
    headers: {
      apikey: SB_KEY,
      Authorization: `Bearer ${SB_KEY}`,
      'Content-Type': 'application/json',
      Prefer: 'return=representation',
    },
    body: JSON.stringify({
      query_embedding: `[${vec.join(',')}]`,
      match_count: limit,
      filter_source: source_type,
      min_similarity,
    }),
  });

  if (!rpcRes.ok) {
    const fallback = await keywordSearch(query, limit, source_type);
    return new Response(JSON.stringify({ ...fallback, query, fallback_reason: 'rpc_error' }), { headers: jsonH });
  }

  // Normalize: RPC returns content+ts; map back to text+timestamp for consistent API
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
