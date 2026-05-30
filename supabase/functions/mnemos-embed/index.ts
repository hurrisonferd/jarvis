// mnemos-embed: store embedding vectors for memories
// OpenAI-compatible API — works with OpenAI, Voyage AI, Cohere, etc.
// Env vars: EMBEDDING_API_KEY (required), EMBEDDING_API_URL (optional), EMBEDDING_MODEL (optional)

const EMBED_URL   = Deno.env.get('EMBEDDING_API_URL') || 'https://api.openai.com/v1/embeddings';
const EMBED_KEY   = Deno.env.get('EMBEDDING_API_KEY') || Deno.env.get('OPENAI_API_KEY');
const EMBED_MODEL = Deno.env.get('EMBEDDING_MODEL') || 'text-embedding-3-small';
const SB_URL      = Deno.env.get('SUPABASE_URL')!;
const SB_KEY      = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type',
};

// Surfaced to the caller so a failed embed says *why* (e.g. OpenAI 429/401),
// instead of silently returning embedded:0.
let lastEmbedError: string | null = null;

export async function embed(text: string): Promise<number[] | null> {
  if (!EMBED_KEY) { lastEmbedError = 'no_api_key'; return null; }
  try {
    const r = await fetch(EMBED_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${EMBED_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: EMBED_MODEL, input: text.slice(0, 8192) }),
    });
    if (!r.ok) {
      const detail = (await r.text().catch(() => '')).slice(0, 200);
      lastEmbedError = `http_${r.status}: ${detail}`;
      return null;
    }
    const d = await r.json();
    const vec = d.data?.[0]?.embedding ?? null;
    if (!vec) lastEmbedError = 'no_embedding_in_response';
    return vec;
  } catch (e) { lastEmbedError = `fetch_error: ${String(e).slice(0, 160)}`; return null; }
}

async function patchRow(id: string, vec: number[]): Promise<void> {
  await fetch(`${SB_URL}/rest/v1/mnemos_memories?id=eq.${encodeURIComponent(id)}`, {
    method: 'PATCH',
    headers: {
      apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`,
      'Content-Type': 'application/json', Prefer: 'return=minimal',
    },
    body: JSON.stringify({ embedding: `[${vec.join(',')}]` }),
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });

  const body = await req.json().catch(() => ({}));
  const jsonH = { 'Content-Type': 'application/json', ...CORS };

  if (body.backfill) {
    if (!EMBED_KEY) return new Response(JSON.stringify({ embedded: 0, reason: 'no_api_key' }), { headers: jsonH });
    const listRes = await fetch(
      `${SB_URL}/rest/v1/mnemos_memories?select=id,text&embedding=is.null&limit=50`,
      { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } }
    );
    const rows: { id: string; text: string }[] = await listRes.json();
    let count = 0;
    lastEmbedError = null;
    for (const row of rows) {
      const vec = await embed(row.text);
      if (!vec) break;
      await patchRow(row.id, vec);
      count++;
    }
    return new Response(JSON.stringify({ embedded: count, backfill: true, total: rows.length, error: count === 0 ? lastEmbedError : null }), { headers: jsonH });
  }

  const { memory_id, text } = body;
  if (!memory_id || !text) {
    return new Response(JSON.stringify({ error: 'memory_id and text required' }), { status: 400, headers: jsonH });
  }
  const vec = await embed(text);
  if (!vec) return new Response(JSON.stringify({ embedded: false, reason: 'no_api_key_or_error' }), { headers: jsonH });
  await patchRow(memory_id, vec);
  return new Response(JSON.stringify({ embedded: true, memory_id, dims: vec.length }), { headers: jsonH });
});
