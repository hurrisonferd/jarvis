-- JMMS Rework v2 — Grade axis (IMPL-JMMS-0001)
-- Adds grade (system | personal) to all memory tables.
-- Seeds all existing rows as system grade.

-- ============================================================
-- 1. mnemos_memories — add grade
-- ============================================================
ALTER TABLE public.mnemos_memories
  ADD COLUMN IF NOT EXISTS grade text DEFAULT 'system';

-- ============================================================
-- 2. jc_objects — add grade
-- ============================================================
ALTER TABLE public.jc_objects
  ADD COLUMN IF NOT EXISTS grade text DEFAULT 'system';

-- ============================================================
-- 3. sl_objects — add grade
-- ============================================================
ALTER TABLE public.sl_objects
  ADD COLUMN IF NOT EXISTS grade text DEFAULT 'system';

-- ============================================================
-- 4. Seed existing rows: all 1451 mnemos rows are system grade
--    (they live in hurrisonferd/jarvis, which is the system repo)
-- ============================================================
UPDATE public.mnemos_memories SET grade = 'system' WHERE grade IS NULL;
UPDATE public.jc_objects SET grade = 'system' WHERE grade IS NULL;
UPDATE public.sl_objects SET grade = 'system' WHERE grade IS NULL;

-- ============================================================
-- 5. Index for grade filtering (query performance)
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_mnemos_grade ON public.mnemos_memories (grade);
CREATE INDEX IF NOT EXISTS idx_jc_grade     ON public.jc_objects (grade);
CREATE INDEX IF NOT EXISTS idx_sl_grade    ON public.sl_objects (grade);

-- Composite indexes for the context stack loader
CREATE INDEX IF NOT EXISTS idx_mnemos_tier_grade
  ON public.mnemos_memories (memory_tier, grade);
CREATE INDEX IF NOT EXISTS idx_mnemos_tier_grade_sub
  ON public.mnemos_memories (memory_tier, grade, jstm_sub, activation_score DESC);
CREATE INDEX IF NOT EXISTS idx_mnemos_tier_grade_domain
  ON public.mnemos_memories (memory_tier, grade, domain, activation_score DESC);
