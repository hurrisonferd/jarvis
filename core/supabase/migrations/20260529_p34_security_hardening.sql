-- P34: Security Hardening (non-breaking subset)
-- Closes the RLS ERROR + removes unused destructive anon grant + pins function search_path.
-- The broader anon-write -> edge-function-proxy refactor is tracked in the P34 ledger entry.

-- 1) mnemos_vocab: was RLS-DISABLED in public (ERROR -- fully exposed). Lock to read-only.
--    Writes happen only via service-role edge function mnemos-store, which bypasses RLS.
ALTER TABLE public.mnemos_vocab ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon read mnemos_vocab" ON public.mnemos_vocab;
CREATE POLICY "anon read mnemos_vocab" ON public.mnemos_vocab FOR SELECT USING (true);

-- 2) save_states: anon DELETE was open and is unused by the browser (only insert/select/update).
--    Remove the destructive grant -- anyone with the public anon key could wipe save states.
DROP POLICY IF EXISTS "anon_delete_save_states" ON public.save_states;

-- 3) Pin function search_path (WARN: role-mutable search_path). Schema-qualify refs so '' is safe.
CREATE OR REPLACE FUNCTION public.match_memories(query_embedding vector, match_count integer DEFAULT 10, filter_source text DEFAULT NULL::text, min_similarity double precision DEFAULT 0.0)
 RETURNS TABLE(id text, source_id text, source_type text, content text, ts timestamp with time zone, metadata jsonb, tags text[], similarity double precision)
 LANGUAGE plpgsql
 SET search_path = ''
AS $function$
BEGIN
  RETURN QUERY
  SELECT m.id, m.source_id, m.source_type, m.text,
         m.timestamp, m.metadata, m.tags,
         (1 - (m.embedding <=> query_embedding))::float AS similarity
  FROM   public.mnemos_memories m
  WHERE  m.embedding IS NOT NULL
    AND  (filter_source IS NULL OR m.source_type = filter_source)
    AND  (1 - (m.embedding <=> query_embedding)) >= min_similarity
  ORDER BY m.embedding <=> query_embedding
  LIMIT  match_count;
END;
$function$;

CREATE OR REPLACE FUNCTION public.mnemos_tsv_update()
 RETURNS trigger
 LANGUAGE plpgsql
 SET search_path = ''
AS $function$
BEGIN
  NEW.tsv := to_tsvector('english', coalesce(NEW.text, ''));
  RETURN NEW;
END;
$function$;
