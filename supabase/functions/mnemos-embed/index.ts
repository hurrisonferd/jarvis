// mnemos-embed: embed a memory and store its vector, or backfill all unembedded rows
// Provider: Jina AI jina-embeddings-v2-base-en (768 dims, free tier)
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

async function patchRow(id: string, vec: number[]): Promise<void> {
  await fetch(`${SB_URL}/rest/v1/mnemos_memories?id=eq.${encodeURIComponent(id)}`, {
    method: 'PATCH',
    headers: {
      apikey: SB_KEY,
      Authorization: `Bearer ${SB_KEY}`,
      'Content-Type': 'application/json',
      Prefer: 'return=minimal',
    },
    body: JSON.stringify({ embedding: `[${vec.join(',')}]` }),
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });

  const body = await req.json().catch(() => ({}));
  const jsonH = { 'Content-Type': 'application/json', ...CORS };

  // Backfill: embed all rows missing a vector (up to 50 per call)
  if (body.backfill) {
    if (!JINA_KEY) return new Response(JSON.stringify({ embedded: 0, reason: 'no_api_key' }), { headers: jsonH });
    const listRes = await fetch(
      `${SB_URL}/rest/v1/mnemos_memories?select=id,text&embedding=is.null&limit=50`,
      { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } }
    );
    const rows: { id: string; text: string }[] = await listRes.json();
    let count = 0;
    for (const row of rows) {
      const vec = await embed(row.text);
      if (!vec) break;
      await patchRow(row.id, vec);
      count++;
    }
    return new Response(JSON.stringify({ embedded: count, backfill: true, total: rows.length }), { headers: jsonH });
  }

  // Single embed
  const { memory_id, text } = body;
  if (!memory_id || !text) {
    return new Response(JSON.stringify({ error: 'memory_id and text required' }), { status: 400, headers: jsonH });
  }
  const vec = await embed(text);
  if (!vec) return new Response(JSON.stringify({ embedded: false, reason: 'no_api_key_or_error' }), { headers: jsonH });
  await patchRow(memory_id, vec);
  return new Response(JSON.stringify({ embedded: true, memory_id, dims: vec.length }), { headers: jsonH });
});
