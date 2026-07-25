-- P33: MNEMOS Vector Layer
-- pgvector cosine similarity search replacing ILIKE keyword fallback
-- Provider: Jina AI jina-embeddings-v2-base-en (768 dims, free tier)
-- Requires JINA_API_KEY (or EMBEDDING_API_KEY) in Supabase edge function secrets

CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE mnemos_memories ADD COLUMN IF NOT EXISTS embedding vector(768);

CREATE INDEX IF NOT EXISTS mnemos_embedding_hnsw_idx
  ON mnemos_memories USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- match_memories: semantic search RPC called by mnemos-search edge function
-- Returns content+ts (not text+timestamp) to avoid SQL reserved word conflicts
CREATE OR REPLACE FUNCTION match_memories(
  query_embedding vector(768),
  match_count     int     DEFAULT 10,
  filter_source   text    DEFAULT NULL,
  min_similarity  float   DEFAULT 0.0
)
RETURNS TABLE (
  id          text,
  source_id   text,
  source_type text,
  content     text,
  ts          timestamptz,
  metadata    jsonb,
  tags        text[],
  similarity  float
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT m.id, m.source_id, m.source_type, m.text,
         m.timestamp, m.metadata, m.tags,
         (1 - (m.embedding <=> query_embedding))::float AS similarity
  FROM   mnemos_memories m
  WHERE  m.embedding IS NOT NULL
    AND  (filter_source IS NULL OR m.source_type = filter_source)
    AND  (1 - (m.embedding <=> query_embedding)) >= min_similarity
  ORDER BY m.embedding <=> query_embedding
  LIMIT  match_count;
END;
$$;
