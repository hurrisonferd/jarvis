-- Resize embedding column 1536 -> 1024 for a free OpenAI-compatible provider
-- (Jina embeddings v3, native 1024 dims). No data lost: 0 rows were embedded
-- when this ran. match_memories takes an untyped `vector`, so it needs no change.
--
-- Provider config lives in Edge Function secrets, not here:
--   EMBEDDING_API_KEY = jina_...
--   EMBEDDING_API_URL = https://api.jina.ai/v1/embeddings
--   EMBEDDING_MODEL   = jina-embeddings-v3

drop index if exists public.mnemos_embedding_hnsw_idx;
alter table public.mnemos_memories drop column if exists embedding;
alter table public.mnemos_memories add column embedding vector(1024);
create index mnemos_embedding_hnsw_idx
  on public.mnemos_memories using hnsw (embedding vector_cosine_ops);
