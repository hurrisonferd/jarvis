-- dex_events: add type column for event classification + write policy for MCP service key.
-- GL5: every state-changing action emits an event. The MCP's jarvis_dex_log tool is
-- the canonical write path for OpenHands sessions, AEGIS gates, and ERIS challenges.

-- 1. Add type column (nullable, defaults to 'dex_log' in code)
alter table public.dex_events
  add column if not exists type text not null default 'dex_log';

comment on column public.dex_events.type is
  'Event type — e.g. bifrost.session_close, aegis.gate, eris.challenge, jd_propose, jd_approve';

-- 2. RLS policy: MCP service key (service_role) can insert; anon can read.
-- The MCP has SUPABASE_SERVICE_KEY so its writes pass through.
drop policy if exists dex_events_insert_mcp on public.dex_events;
create policy dex_events_insert_mcp on public.dex_events for insert
  with check (true);  -- service role bypasses RLS; anon key cannot POST anyway

-- Verify: select check SQL
-- select sql from pg_policies where tablename = 'dex_events';
