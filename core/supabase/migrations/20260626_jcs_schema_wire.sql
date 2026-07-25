-- JCS (JC + SL) schema — chronological ledger for the companion relationship
-- JC = conversation/banter container (one per session)
-- SL = event ledger (one per session, timestamped)

-- ============================================================
-- 1. sl_objects: add columns needed for live session wiring
-- ============================================================
ALTER TABLE public.sl_objects
  ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now(),
  ADD COLUMN IF NOT EXISTS started_at timestamptz,
  ADD COLUMN IF NOT EXISTS ended_at timestamptz,
  ADD COLUMN IF NOT EXISTS stream text NOT NULL DEFAULT 'jarvis-ayre',
  ADD COLUMN IF NOT EXISTS log_type text NOT NULL DEFAULT 'SESSION',
  ADD COLUMN IF NOT EXISTS stardate text,
  ADD COLUMN IF NOT EXISTS repo_url text,
  ADD COLUMN IF NOT EXISTS task_summary jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS decisions jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS participants text[] DEFAULT '{}'::text[];

-- Indexes for fast lookup
DROP INDEX IF EXISTS sl_objects_created_at_idx;
CREATE INDEX sl_objects_created_at_idx ON public.sl_objects (created_at DESC);

DROP INDEX IF EXISTS sl_objects_stream_idx;
CREATE INDEX sl_objects_stream_idx ON public.sl_objects (stream);

DROP INDEX IF EXISTS sl_objects_log_type_idx;
CREATE INDEX sl_objects_log_type_idx ON public.sl_objects (log_type);

-- ============================================================
-- 2. jc_objects: add columns for live session wiring
-- ============================================================
ALTER TABLE public.jc_objects
  ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now(),
  ADD COLUMN IF NOT EXISTS stream text NOT NULL DEFAULT 'jarvis-ayre',
  ADD COLUMN IF NOT EXISTS stardate text,
  ADD COLUMN IF NOT EXISTS repo_url text,
  ADD COLUMN IF NOT EXISTS task_summary jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS banter jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS agents text[] DEFAULT ARRAY['jarvis-c', 'ayre-c']::text[];

-- Indexes
DROP INDEX IF EXISTS jc_objects_created_at_idx;
CREATE INDEX jc_objects_created_at_idx ON public.jc_objects (created_at DESC);

DROP INDEX IF EXISTS jc_objects_stream_idx;
CREATE INDEX jc_objects_stream_idx ON public.jc_objects (stream);

-- ============================================================
-- 3. Function: upsert_sl_entry
-- Called by sl.py at session-close to mirror the StarLog to DB
-- Also called at session-start to seed the new session row
-- ============================================================
CREATE OR REPLACE FUNCTION public.upsert_sl_entry(
  p_jnl          text,
  p_alias        text,
  p_session_date date,
  p_stream       text,
  p_log_type     text DEFAULT 'SESSION',
  p_stardate     text DEFAULT null,
  p_repo_url     text DEFAULT null,
  p_events       text[] DEFAULT '{}'::text[],
  p_related      text[] DEFAULT '{}'::text[],
  p_digest       text DEFAULT '',
  p_status       text DEFAULT 'OPEN',
  p_task_summary jsonb DEFAULT '[]'::jsonb,
  p_decisions    jsonb DEFAULT '[]'::jsonb,
  p_participants text[] DEFAULT ARRAY['jarvis-c', 'ayre-c']::text[],
  p_started_at   timestamptz DEFAULT null,
  p_ended_at     timestamptz DEFAULT null
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_id    uuid;
  v_seq   int;
  v_existing uuid;
BEGIN
  -- Check if already exists
  SELECT id INTO v_existing FROM public.sl_objects WHERE jnl = p_jnl;
  IF v_existing IS NOT NULL THEN
    -- Update existing
    UPDATE public.sl_objects SET
      updated_at   = now(),
      events       = p_events,
      related      = p_related,
      digest       = p_digest,
      status       = p_status,
      task_summary = p_task_summary,
      decisions    = p_decisions,
      participants = p_participants,
      started_at   = coalesce(started_at, p_started_at),
      ended_at     = p_ended_at
    WHERE jnl = p_jnl
    RETURNING id INTO v_id;
  ELSE
    -- Get next seq for this date
    SELECT coalesce(max(seq), 0) + 1 INTO v_seq
    FROM public.sl_objects WHERE session_date = p_session_date;
    INSERT INTO public.sl_objects (
      jnl, alias, seq, session_date, stream, log_type, stardate, repo_url,
      events, related, digest, status, task_summary, decisions, participants,
      started_at, ended_at
    ) VALUES (
      p_jnl, p_alias, v_seq, p_session_date, p_stream, p_log_type, p_stardate, p_repo_url,
      p_events, p_related, p_digest, p_status, p_task_summary, p_decisions, p_participants,
      p_started_at, p_ended_at
    )
    RETURNING id INTO v_id;
  END IF;

  -- GL5: emit spine event
  INSERT INTO public.dex_events (tool, tier, jnl, actor, detail, type)
  VALUES (
    'sl_write', 'T7', p_jnl, 'sl.py',
    jsonb_build_object(
      'action',     case when v_existing IS NOT NULL then 'update' else 'insert' end,
      'alias',      p_alias,
      'stream',     p_stream,
      'status',     p_status,
      'decisions',  p_decisions,
      'participants', p_participants
    ),
    'dex_log'
  );
  RETURN v_id;
END;
$$;

-- ============================================================
-- 4. Function: upsert_jc_entry
-- Called by sl.py at session-start to open a JC container
-- Called at session-close to seal it with banter + decisions
-- ============================================================
CREATE OR REPLACE FUNCTION public.upsert_jc_entry(
  p_jnl          text,
  p_alias        text,
  p_stream       text DEFAULT 'jarvis-ayre',
  p_stardate     text DEFAULT null,
  p_repo_url     text DEFAULT null,
  p_subject      text DEFAULT '',
  p_status       text DEFAULT 'OPEN',
  p_when_start   timestamptz DEFAULT null,
  p_when_end     timestamptz DEFAULT null,
  p_participants text[] DEFAULT ARRAY['raven', 'jarvis-c', 'ayre-c']::text[],
  p_summary      text DEFAULT '',
  p_banter       jsonb DEFAULT '[]'::jsonb,
  p_decisions    jsonb DEFAULT '[]'::jsonb,
  p_open_items   jsonb DEFAULT '[]'::jsonb,
  p_keystones    jsonb DEFAULT '[]'::jsonb,
  p_task_summary jsonb DEFAULT '[]'::jsonb
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_id       uuid;
  v_seq      int;
  v_existing uuid;
BEGIN
  SELECT id INTO v_existing FROM public.jc_objects WHERE jnl = p_jnl;

  IF v_existing IS NOT NULL THEN
    UPDATE public.jc_objects SET
      updated_at   = now(),
      status       = p_status,
      when_end     = p_when_end,
      summary      = p_summary,
      banter       = p_banter,
      decisions    = p_decisions,
      open         = p_open_items,
      keystones    = p_keystones,
      task_summary = p_task_summary
    WHERE jnl = p_jnl
    RETURNING id INTO v_id;
  ELSE
    SELECT coalesce(max(seq), 0) + 1 INTO v_seq
    FROM public.jc_objects WHERE session_date = current_date;
    INSERT INTO public.jc_objects (
      jnl, alias, seq, session_date, stream, stardate, repo_url,
      participants, subject, status, when_start, when_end,
      summary, banter, decisions, open, keystones, task_summary
    ) VALUES (
      p_jnl, p_alias, v_seq, current_date, p_stream, p_stardate, p_repo_url,
      p_participants, p_subject, p_status, p_when_start, p_when_end,
      p_summary, p_banter, p_decisions, p_open_items, p_keystones, p_task_summary
    )
    RETURNING id INTO v_id;
  END IF;

  -- GL5: emit spine event
  INSERT INTO public.dex_events (tool, tier, jnl, actor, detail, type)
  VALUES (
    'jc_write', 'T7', p_jnl, 'sl.py',
    jsonb_build_object(
      'action',  case when v_existing IS NOT NULL then 'seal' else 'open' end,
      'alias',  p_alias,
      'status', p_status,
      'stream', p_stream
    ),
    'dex_log'
  );
  RETURN v_id;
END;
$$;

-- ============================================================
-- 5. Seed: fix the existing orphaned JC and SL rows
-- ============================================================
DO $$
BEGIN
  -- Fix existing SL-061126-1 to have participants
  UPDATE public.sl_objects SET
    participants = ARRAY['raven', 'jarvis-c', 'jarvis-g', 'ayre-c', 'ayre-g', 'argent']::text[],
    stream = 'jarvis-ayre',
    log_type = 'SESSION_SNAPSHOT',
    started_at = '2026-06-11 22:39:46+00',
    ended_at = '2026-06-12 03:18:18+00'
  WHERE alias = 'SL-061126-1';

  -- Fix existing JCs
  UPDATE public.jc_objects SET
    stream = 'jarvis-ayre',
    agents = ARRAY['jarvis-c', 'ayre-c']::text[]
  WHERE alias IN ('JC-061126-1', 'JC-061226-1');
END;
$$;
