-- P33 fix: change embedding dimension 768 → 1536 (OpenAI text-embedding-3-small)
-- No data loss — column was added but never populated (no API key was set)
DROP INDEX IF EXISTS mnemos_embedding_hnsw_idx;
ALTER TABLE mnemos_memories DROP COLUMN IF EXISTS embedding;
ALTER TABLE mnemos_memories ADD COLUMN embedding vector(1536);

CREATE INDEX mnemos_embedding_hnsw_idx
  ON mnemos_memories USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

CREATE OR REPLACE FUNCTION match_memories(
  query_embedding vector(1536),
  match_count     int   DEFAULT 10,
  filter_source   text  DEFAULT NULL,
  min_similarity  float DEFAULT 0.0
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
