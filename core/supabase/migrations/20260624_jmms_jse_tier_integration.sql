-- 20260624_jmms_jse_tier_integration.sql
-- JMMS (5 tiers) + JSE compliance for jc_objects / sl_objects / jip_entries.
-- Raven-directed 2026-06-24: JHTM added to runtime; JSE objects need memory_tier
-- and JSS status. Git-first: this is the canonical record; Supabase syncs on merge.
--
-- Changes:
--   jc_objects:   +memory_tier +jss_status +idx
--   sl_objects:    +memory_tier +jss_status +idx
--   jip_entries:   +memory_tier +jss_status +jnl (derived: JIP-{target_jd}-{v})
--   jd_entries:    +memory_tier (not a table column — handled by seed.py + JVE)
--
-- Defaults:
--   JC/SL: memory_tier=JSTM  (session-born, high churn)
--   JIP:  memory_tier=JLTM  (consolidated once created)
--   JC/SL: jss_status=ACTIVE (new sessions live; fold/dismiss changes this)
--   JIP:  jss_status=derived from status column (proposed→DRAFT, active→ACTIVE, etc.)

-- ── jc_objects ──────────────────────────────────────────────────────────────────
alter table public.jc_objects add column if not exists memory_tier text not null default 'jstm';
alter table public.jc_objects add column if not exists jss_status text not null default 'ACTIVE';

create index if not exists jc_objects_memory_tier_idx on public.jc_objects (memory_tier);
create index if not exists jc_objects_jss_status_idx  on public.jc_objects (jss_status);
create index if not exists jc_objects_session_date_idx on public.jc_objects (session_date desc);

-- ── sl_objects ─────────────────────────────────────────────────────────────────
alter table public.sl_objects add column if not exists memory_tier text not null default 'jhtm';
alter table public.sl_objects add column if not exists jss_status text not null default 'ACTIVE';

create index if not exists sl_objects_memory_tier_idx on public.sl_objects (memory_tier);
create index if not exists sl_objects_jss_status_idx  on public.sl_objects (jss_status);
create index if not exists sl_objects_session_date_idx on public.sl_objects (session_date desc);

-- ── jip_entries ───────────────────────────────────────────────────────────────
alter table public.jip_entries add column if not exists memory_tier text not null default 'jltm';

-- jnl: derived address = JIP-{target_jd}-{v:03d}
alter table public.jip_entries add column if not exists jnl text;
update public.jip_entries set jnl = format('JIP-%s-%03d', target_jd, version) where jnl is null;
alter table public.jip_entries alter column jnl set not null;

-- jss_status derived from status: proposed=DRAFT, active=ACTIVE, superseded=ARCHIVED, rejected=DEPRECATED, reverted=DEPRECATED
alter table public.jip_entries add column if not exists jss_status text;
update public.jip_entries set jss_status = case
  when status = 'proposed'  then 'DRAFT'
  when status = 'active'    then 'ACTIVE'
  when status = 'superseded' then 'ARCHIVED'
  when status = 'rejected' then 'DEPRECATED'
  when status = 'reverted'  then 'DEPRECATED'
  else 'ACTIVE'
end where jss_status is null;
alter table public.jip_entries alter column jss_status set not null;

create index if not exists jip_entries_memory_tier_idx on public.jip_entries (memory_tier);
create index if not exists jip_entries_jss_status_idx  on public.jip_entries (jss_status);
create index if not exists jip_entries_jnl_idx          on public.jip_entries (jnl);
create unique index if not exists jip_entries_jnl_unique on public.jip_entries (jnl) where jnl is not null;
