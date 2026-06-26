// mnemos-search: semantic memory search (pgvector cosine similarity)
// Falls back to PostgreSQL full-text search (tsv) when no API key is set
// OpenAI-compatible — works with OpenAI, Voyage AI, Cohere, etc.
// Env vars: EMBEDDING_API_KEY, EMBEDDING_API_URL, EMBEDDING_MODEL

const EMBED_URL   = Deno.env.get('EMBEDDING_API_URL') || 'https://api.openai.com/v1/embeddings';
const EMBED_KEY   = Deno.env.get('EMBEDDING_API_KEY') || Deno.env.get('OPENAI_API_KEY');
const EMBED_MODEL = Deno.env.get('EMBEDDING_MODEL') || 'text-embedding-3-small';
// MUST match the query vector to mnemos_memories.embedding = vector(1024). Keep in
// lockstep with mnemos-embed; a mismatch makes cosine search silently return nothing.
const EMBED_DIM   = Number(Deno.env.get('EMBEDDING_DIM') || '1024');
const SB_URL      = Deno.env.get('SUPABASE_URL')!;
const SB_KEY      = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type',
};

let lastEmbedError: string | null = null;

async function embed(text: string): Promise<number[] | null> {
  if (!EMBED_KEY) { lastEmbedError = 'no_api_key'; return null; }
  try {
    const r = await fetch(EMBED_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${EMBED_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: EMBED_MODEL, input: text.slice(0, 8192), dimensions: EMBED_DIM }),
    });
    if (!r.ok) { lastEmbedError = `http_${r.status}: ${(await r.text().catch(()=>'')).slice(0,180)}`; return null; }
    const d = await r.json();
    const vec = d.data?.[0]?.embedding ?? null;
    if (!vec) { lastEmbedError = `no_embedding (url=${EMBED_URL}, model=${EMBED_MODEL})`; return null; }
    if (vec.length !== EMBED_DIM) { lastEmbedError = `dim_mismatch: model returned ${vec.length}, column is ${EMBED_DIM}`; return null; }
    return vec;
  } catch (e) { lastEmbedError = `fetch_error: ${String(e).slice(0,160)}`; return null; }
}

async function fulltextSearch(
  query: string, limit: number, sourceType: string | null, grade: string | null
): Promise<{ results: unknown[]; method: string }> {
  // IMPL-JMMS-0001: include JMMS columns, filter by grade
  const cols = 'id,source_id,source_type,text,timestamp,metadata,tags,memory_tier,memory_scope,temperature,activation_score,domain,grade';
  const tsQuery = query.trim().split(/\s+/).filter(Boolean).join(' & ');
  let url = `${SB_URL}/rest/v1/mnemos_memories`
    + `?select=${cols}&limit=${limit}&order=timestamp.desc`;
  if (tsQuery) url += `&tsv=fts.${encodeURIComponent(tsQuery)}`;
  if (sourceType) url += `&source_type=eq.${encodeURIComponent(sourceType)}`;
  if (grade) url += `&grade=eq.${encodeURIComponent(grade)}`;
  const r = await fetch(url, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } });
  const rows: Record<string, unknown>[] = await r.json().catch(() => []);
  if (!rows?.length) {
    const fallUrl = `${SB_URL}/rest/v1/mnemos_memories?select=${cols}&limit=${limit}&order=timestamp.desc`
      + (sourceType ? `&source_type=eq.${encodeURIComponent(sourceType)}` : '')
      + (grade ? `&grade=eq.${encodeURIComponent(grade)}` : '');
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
  // IMPL-JMMS-0001: grade param — default system; passed to RPC and fulltext fallback
  const { query, limit = 10, source_type = null, min_similarity = 0.0, grade = null } = body;

  if (!query) return new Response(JSON.stringify({ error: 'query required' }), { status: 400, headers: jsonH });

  lastEmbedError = null;
  const vec = await embed(query);

  // IMPL-JMMS-0001: pass grade to all query paths
  if (!vec) {
    const fallback = await fulltextSearch(query, limit, source_type, grade);
    return new Response(JSON.stringify({ ...fallback, query, embed_error: lastEmbedError }), { headers: jsonH });
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
      // IMPL-JMMS-0001: grade filter — RPC must support this param (graceful if not)
      grade,
    }),
  });

  if (!rpcRes.ok) {
    const fallback = await fulltextSearch(query, limit, source_type, grade);
    return new Response(JSON.stringify({ ...fallback, query, fallback_reason: 'rpc_error' }), { headers: jsonH });
  }

  // IMPL-JMMS-0001: include JMMS columns in result mapping
  const raw: Record<string, unknown>[] = await rpcRes.json();
  const results = raw.map(r => ({
    id: r.id, source_id: r.source_id, source_type: r.source_type,
    text: r.content, timestamp: r.ts,
    metadata: r.metadata, tags: r.tags, similarity: r.similarity,
    // IMPL-JMMS-0001: carry JMMS dimensions from RPC response
    memory_tier: r.memory_tier, memory_scope: r.memory_scope,
    temperature: r.temperature, activation_score: r.activation_score,
    domain: r.domain, grade: r.grade,
  }));
  return new Response(
    JSON.stringify({ results, method: 'semantic', query, dims: vec.length }),
    { headers: jsonH }
  );
});
