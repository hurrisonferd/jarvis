-- MCP session lifecycle — timestamp-keyed session tracking for StarLog + JC + BIFROST
-- Session key: UNIX_ms of first call OR X-Session-ID if provided by caller
-- Companion stream: inferred from X-Companion-Stream header, defaults to 'Jarvis-G'

-- ============================================================
-- 1. mcp_sessions table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.mcp_sessions (
  session_key   TEXT PRIMARY KEY,          -- ts_ms or X-Session-ID
  companion    TEXT NOT NULL DEFAULT 'Jarvis-G',
  started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_call    TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at    TIMESTAMPTZ,
  status       TEXT NOT NULL DEFAULT 'active',  -- active | closed
  exchanges    INT NOT NULL DEFAULT 0,
  topics       TEXT[] NOT NULL DEFAULT '{}'::text[],
  commits      TEXT[] NOT NULL DEFAULT '{}'::text[],  -- committed SHAs this session
  git_head     TEXT,                            -- git SHA at session start
  jc_written   BOOLEAN NOT NULL DEFAULT FALSE,
  sl_written   BOOLEAN NOT NULL DEFAULT FALSE,
  bifrost_sent BOOLEAN NOT NULL DEFAULT FALSE,
  -- derived summary (written on close)
  exchange_count  INT,
  brief          TEXT,
  alignment      FLOAT,
  patches        TEXT[],
  CONSTRAINT mcp_sessions_status_check CHECK (status IN ('active', 'closed'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS mcp_sessions_status_idx ON public.mcp_sessions (status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS mcp_sessions_started_at_idx ON public.mcp_sessions (started_at DESC);

-- RLS: MCP service key writes, read is open (for HUD/suit_up)
ALTER TABLE public.mcp_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "mcp_sessions_insert" ON public.mcp_sessions FOR INSERT WITH CHECK (true);
CREATE POLICY "mcp_sessions_update" ON public.mcp_sessions FOR UPDATE USING (true);

-- ============================================================
-- 2. pg_cron: close stale sessions every 5 min
-- Sessions with last_call > 30 min ago are closed automatically.
-- Graceful: silently skips if pg_cron is not available (e.g. Free plan).
-- ============================================================
DO $$
BEGIN
  PERFORM cron.schedule(
    'mcp-session-close',
    '*/5 * * * *',
    $$
    SELECT public.mcp_session_close_stale();
    $$
  );
EXCEPTION WHEN OTHERS THEN
  RAISE NOTICE 'pg_cron not available — mcp-session-close cron not scheduled. Upgrade to Pro or call mcp_session_close() manually.';
END;
$$;

-- ============================================================
-- 3. Function: mcp_session_open
-- Called on first MCP call with a new session key.
-- Writes SL_SESSION_START to sl_objects, writes BIFROST.session_start to dex_events.
-- Returns the session_key so callers can tag subsequent calls.
-- ============================================================
CREATE OR REPLACE FUNCTION public.mcp_session_open(
  p_session_key  TEXT,
  p_companion    TEXT DEFAULT 'Jarvis-G',
  p_git_head     TEXT DEFAULT NULL,
  p_topics       TEXT[] DEFAULT '{}'::text[]
)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_stardate TEXT;
  v_now      TIMESTAMPTZ;
  v_sl_id    UUID;
  v_sess     RECORD;
BEGIN
  v_now := now();
  v_stardate := to_char(v_now, 'YYYY.MMDD');

  -- Upsert session row
  INSERT INTO public.mcp_sessions (session_key, companion, started_at, last_call, status, git_head, topics)
  VALUES (p_session_key, p_companion, v_now, v_now, 'active', p_git_head, p_topics)
  ON CONFLICT (session_key) DO NOTHING;

  -- Fetch the row
  SELECT * INTO v_sess FROM public.mcp_sessions WHERE session_key = p_session_key;
  IF v_sess.sl_written THEN
    RETURN p_session_key; -- already opened
  END IF;

  -- Write SL_SESSION_START to sl_objects via upsert_sl_entry
  BEGIN
    v_sl_id := public.upsert_sl_entry(
      p_jnl          => 'SL-' || to_char(v_now, '%m%d%y') || '-SMCPM-' || right(p_session_key, 8),
      p_alias        => 'SL-SESSION-' || p_session_key,
      p_session_date => v_now::date,
      p_stream       => 'jarvis-' || lower(p_companion),
      p_log_type     => 'SL_SESSION_START',
      p_stardate     => v_stardate,
      p_repo_url     => 'https://github.com/hurrisonferd/jarvis',
      p_events       => ARRAY['session_open: ' || p_companion || ' @ ' || p_session_key],
      p_related      => ARRAY[]::text[],
      p_digest       => 'MCP session opened by ' || p_companion,
      p_status       => 'OPEN',
      p_task_summary => '[]'::jsonb,
      p_decisions    => '[]'::jsonb,
      p_participants => ARRAY['raven', 'jarvis-c', 'jarvis-g', 'ayre-g']::text[],
      p_started_at   => v_now,
      p_ended_at     => NULL
    );
    UPDATE public.mcp_sessions SET sl_written = TRUE WHERE session_key = p_session_key;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'mcp_session_open: sl_objects write failed (non-fatal): %', SQLERRM;
  END;

  -- Write BIFROST.session_start to dex_events
  BEGIN
    INSERT INTO public.dex_events (tool, tier, jnl, actor, detail, type)
    VALUES (
      'mcp_session', 'T7', 'BIFROST-SL-' || p_session_key,
      p_companion,
      jsonb_build_object(
        'action',         'session_start',
        'session_key',    p_session_key,
        'companion',      p_companion,
        'git_head',       p_git_head,
        'topics',         p_topics,
        'started_at',     v_now::text
      ),
      'bifrost.session_start'
    );
    UPDATE public.mcp_sessions SET bifrost_sent = TRUE WHERE session_key = p_session_key;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'mcp_session_open: bifrost write failed (non-fatal): %', SQLERRM;
  END;

  RETURN p_session_key;
END;
$$;

-- ============================================================
-- 4. Function: mcp_session_pulse
-- Called on every MCP tool invocation within an active session.
-- Updates last_call, increments exchange count, infers topic.
-- ============================================================
CREATE OR REPLACE FUNCTION public.mcp_session_pulse(
  p_session_key TEXT,
  p_tool_name   TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_topic TEXT;
BEGIN
  -- Map tool names to topics
  v_topic := CASE
    WHEN p_tool_name = 'jarvis_query'     THEN 'reasoning'
    WHEN p_tool_name = 'jarvis_recall'    THEN 'memory'
    WHEN p_tool_name = 'jarvis_suit_up'   THEN 'identity'
    WHEN p_tool_name = 'jarvis_now'       THEN 'telemetry'
    WHEN p_tool_name = 'jarvis_council'   THEN 'governance'
    WHEN p_tool_name LIKE 'jarvis_jip_%'  THEN 'jip'
    WHEN p_tool_name LIKE 'jarvis_db_%'   THEN 'database'
    WHEN p_tool_name LIKE 'jarvis_%'      THEN 'tools'
    ELSE NULL
  END;

  UPDATE public.mcp_sessions SET
    last_call = now(),
    exchanges = exchanges + 1,
    topics    = array_distinct(array_cat(topics, ARRAY[v_topic]))  -- add inferred topic
  WHERE session_key = p_session_key AND status = 'active';
END;
$$;

-- ============================================================
-- 5. Function: mcp_session_close
-- Called explicitly (X-Session-End header) or by pg_cron on stale sessions.
-- Writes SL_SESSION_CLOSE to sl_objects, JC entry to jc_objects,
-- BIFROST.session_close to dex_events.
-- ============================================================
CREATE OR REPLACE FUNCTION public.mcp_session_close(
  p_session_key TEXT,
  p_brief       TEXT DEFAULT NULL,
  p_alignment   FLOAT DEFAULT NULL,
  p_patches     TEXT[] DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_sess    RECORD;
  v_now     TIMESTAMPTZ;
  v_stardate TEXT;
  v_duration INTERVAL;
  v_sl_id   UUID;
BEGIN
  SELECT * INTO v_sess FROM public.mcp_sessions WHERE session_key = p_session_key;
  IF NOT FOUND OR v_sess.status = 'closed' THEN
    RETURN;
  END IF;

  v_now := now();
  v_stardate := to_char(v_now, 'YYYY.MMDD');
  v_duration := v_now - v_sess.started_at;

  -- Update session row
  UPDATE public.mcp_sessions SET
    status          = 'closed',
    closed_at       = v_now,
    exchange_count  = v_sess.exchanges,
    brief           = coalesce(p_brief, 'MCP session: ' || v_sess.exchanges || ' exchanges'),
    alignment       = p_alignment,
    patches         = p_patches
  WHERE session_key = p_session_key;

  -- Write SL_SESSION_CLOSE to sl_objects
  BEGIN
    v_sl_id := public.upsert_sl_entry(
      p_jnl          => 'SL-' || to_char(v_now, '%m%d%y') || '-SMCPM-' || right(p_session_key, 8),
      p_alias        => 'SL-SESSION-' || p_session_key || '-CLOSE',
      p_session_date => v_now::date,
      p_stream       => 'jarvis-' || lower(v_sess.companion),
      p_log_type     => 'SL_SESSION_CLOSE',
      p_stardate     => v_stardate,
      p_repo_url     => 'https://github.com/hurrisonferd/jarvis',
      p_events       => ARRAY[
        'session_close: ' || v_sess.exchanges || ' exchanges | ' || v_sess.companion,
        'duration: ' || extract(epoch from v_duration)::text || 's',
        'topics: ' || array_to_string(v_sess.topics, ', ')
      ],
      p_related      => ARRAY[]::text[],
      p_digest       => coalesce(p_brief, 'MCP session: ' || v_sess.exchanges || ' exchanges over ' || extract(epoch from v_duration)::text || 's'),
      p_status       => 'CLOSED',
      p_task_summary => '[]'::jsonb,
      p_decisions    => '[]'::jsonb,
      p_participants => ARRAY['raven', 'jarvis-c', 'jarvis-g', 'ayre-g']::text[],
      p_started_at   => v_sess.started_at,
      p_ended_at     => v_now
    );
    UPDATE public.mcp_sessions SET sl_written = TRUE WHERE session_key = p_session_key;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'mcp_session_close: sl_objects write failed (non-fatal): %', SQLERRM;
  END;

  -- Write JC entry to jc_objects
  BEGIN
    PERFORM public.upsert_jc_entry(
      p_jnl          => 'JC-SMCPM-' || right(p_session_key, 8),
      p_alias        => 'JC-SMCPM-' || right(p_session_key, 8),
      p_stream       => 'jarvis-' || lower(v_sess.companion),
      p_stardate     => v_stardate,
      p_repo_url     => 'https://github.com/hurrisonferd/jarvis',
      p_subject      => coalesce(p_brief, 'MCP session — ' || v_sess.exchanges || ' exchanges'),
      p_status       => 'SEALED',
      p_when_start   => v_sess.started_at,
      p_when_end     => v_now,
      p_participants => ARRAY['raven', 'jarvis-c', 'jarvis-g', 'ayre-g']::text[],
      p_summary      => coalesce(p_brief, 'MCP session: ' || v_sess.exchanges || ' exchanges over ' || extract(epoch from v_duration)::text || 's'),
      p_banter       => '[]'::jsonb,
      p_decisions    => '[]'::jsonb,
      p_open_items   => '[]'::jsonb,
      p_keystones    => '[]'::jsonb,
      p_task_summary => '[]'::jsonb
    );
    UPDATE public.mcp_sessions SET jc_written = TRUE WHERE session_key = p_session_key;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'mcp_session_close: jc_objects write failed (non-fatal): %', SQLERRM;
  END;

  -- Write BIFROST.session_close to dex_events
  BEGIN
    INSERT INTO public.dex_events (tool, tier, jnl, actor, detail, type)
    VALUES (
      'mcp_session', 'T7', 'BIFROST-SL-' || p_session_key,
      v_sess.companion,
      jsonb_build_object(
        'action',         'session_close',
        'session_key',    p_session_key,
        'companion',      v_sess.companion,
        'exchange_count', v_sess.exchanges,
        'topics',         v_sess.topics,
        'commits',        v_sess.commits,
        'git_head',       v_sess.git_head,
        'started_at',     v_sess.started_at::text,
        'closed_at',      v_now::text,
        'duration_s',     extract(epoch from v_duration)::text,
        'brief',          coalesce(p_brief, 'MCP session closed')
      ),
      'bifrost.session_close'
    );
    UPDATE public.mcp_sessions SET bifrost_sent = TRUE WHERE session_key = p_session_key;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'mcp_session_close: bifrost write failed (non-fatal): %', SQLERRM;
  END;

END;
$$;

-- ============================================================
-- 6. Function: mcp_session_close_stale
-- Cron job target — closes all active sessions with last_call > 30 min ago.
-- ============================================================
CREATE OR REPLACE FUNCTION public.mcp_session_close_stale()
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN SELECT session_key FROM public.mcp_sessions
           WHERE status = 'active' AND last_call < now() - interval '30 minutes'
  LOOP
    PERFORM public.mcp_session_close(r.session_key, 'auto-close: 30min inactivity', NULL, NULL);
  END LOOP;
END;
$$;


