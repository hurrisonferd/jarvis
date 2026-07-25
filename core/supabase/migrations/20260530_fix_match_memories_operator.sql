-- Latent bug, surfaced on first real use of semantic recall.
--
-- match_memories runs with `set search_path = ''` (P34 security hardening),
-- which prevents PostgreSQL from resolving pgvector's `<=>` cosine operator
-- (defined in the public schema). With zero embeddings in the table the
-- function was never exercised, so the fault stayed hidden until the Jina
-- backfill populated 49 vectors — then every semantic search fell back to
-- recency with "operator does not exist: public.vector <=> public.vector".
--
-- Fix: qualify the operator explicitly as OPERATOR(public.<=>), keeping the
-- hardened empty search_path. Function contract is otherwise unchanged.
create or replace function public.match_memories(
  query_embedding vector,
  match_count integer default 10,
  filter_source text default null,
  min_similarity double precision default 0.0
)
returns table(
  id text, source_id text, source_type text, content text,
  ts timestamptz, metadata jsonb, tags text[], similarity double precision
)
language plpgsql
stable
set search_path to ''
as $function$
begin
  return query
  select m.id, m.source_id, m.source_type, m.text,
         m.timestamp, m.metadata, m.tags,
         (1 - (m.embedding OPERATOR(public.<=>) query_embedding))::float as similarity
  from   public.mnemos_memories m
  where  m.embedding is not null
    and  (filter_source is null or m.source_type = filter_source)
    and  (1 - (m.embedding OPERATOR(public.<=>) query_embedding)) >= min_similarity
  order by m.embedding OPERATOR(public.<=>) query_embedding
  limit  match_count;
end;
$function$;
