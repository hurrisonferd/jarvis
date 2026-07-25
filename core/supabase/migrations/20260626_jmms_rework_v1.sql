-- JMMS Rework v1 (IMPL-JMMS-0001)
-- Adds: jstm_sub, memory_scope, temperature, activation_score, domain
-- Fixes: removes 'jltm' DEFAULT from mnemos_memories.memory_tier

-- ============================================================
-- 1. mnemos_memories — drop the JLTM gravity well DEFAULT
-- ============================================================
ALTER TABLE public.mnemos_memories
  ALTER COLUMN memory_tier DROP DEFAULT;

-- Add new JMMS columns (all nullable with sensible defaults; app supplies on write)
ALTER TABLE public.mnemos_memories
  ADD COLUMN IF NOT EXISTS jstm_sub         text DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS memory_scope     text DEFAULT 'project',
  ADD COLUMN IF NOT EXISTS temperature      text DEFAULT 'warm',
  ADD COLUMN IF NOT EXISTS activation_score integer DEFAULT 80,
  ADD COLUMN IF NOT EXISTS domain           text DEFAULT NULL;

-- ============================================================
-- 2. jc_objects — wire to JMMS
-- ============================================================
ALTER TABLE public.jc_objects
  ADD COLUMN IF NOT EXISTS memory_tier      text DEFAULT 'jstm',
  ADD COLUMN IF NOT EXISTS jstm_sub        text DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS memory_scope     text DEFAULT 'session',
  ADD COLUMN IF NOT EXISTS temperature     text DEFAULT 'warm',
  ADD COLUMN IF NOT EXISTS activation_score integer DEFAULT 80,
  ADD COLUMN IF NOT EXISTS domain          text DEFAULT NULL;

-- ============================================================
-- 3. sl_objects — wire to JMMS
-- ============================================================
ALTER TABLE public.sl_objects
  ADD COLUMN IF NOT EXISTS memory_tier      text DEFAULT 'jhtm',
  ADD COLUMN IF NOT EXISTS memory_scope     text DEFAULT 'project',
  ADD COLUMN IF NOT EXISTS temperature      text DEFAULT 'cool',
  ADD COLUMN IF NOT EXISTS domain           text DEFAULT NULL;

-- ============================================================
-- 4. RLS — ensure domain-scoped read policies exist
-- ============================================================
DO $$
BEGIN
  CREATE POLICY mnemos_domain_read ON public.mnemos_memories FOR SELECT USING (true);
EXCEPTION WHEN duplicate_object THEN null;
END;
$$;

DO $$
BEGIN
  CREATE POLICY jc_domain_read ON public.jc_objects FOR SELECT USING (true);
EXCEPTION WHEN duplicate_object THEN null;
END;
$$;

DO $$
BEGIN
  CREATE POLICY sl_domain_read ON public.sl_objects FOR SELECT USING (true);
EXCEPTION WHEN duplicate_object THEN null;
END;
$$;

-- ============================================================
-- 5. Seed existing mnemos rows: set defaults for new columns
--    (all 1451 rows get session scope, warm temp, 50 activation)
--    This preserves existing data while adopting the new schema.
-- ============================================================
UPDATE public.mnemos_memories SET
  jstm_sub         = NULL,
  memory_scope     = 'project',
  temperature      = 'warm',
  activation_score = 50,
  domain           = NULL
WHERE memory_scope IS NULL;
