-- JSS — Jarvis Status System: lifecycle status on the JD/JNL mirror.
-- Vocabulary: TASK / EXPANSION / ACTIVE / INACTIVE / ARCHIVED / DEPRECATED.

alter table public.jnl_registry add column if not exists status text not null default 'ACTIVE';
alter table public.jd_entries   add column if not exists status text not null default 'ACTIVE';

alter table public.jnl_registry drop constraint if exists jnl_registry_status_chk;
alter table public.jnl_registry add constraint jnl_registry_status_chk
  check (status in ('TASK','EXPANSION','ACTIVE','INACTIVE','ARCHIVED','DEPRECATED'));
alter table public.jd_entries drop constraint if exists jd_entries_status_chk;
alter table public.jd_entries add constraint jd_entries_status_chk
  check (status in ('TASK','EXPANSION','ACTIVE','INACTIVE','ARCHIVED','DEPRECATED'));

create index if not exists jnl_registry_status_idx on public.jnl_registry (status);
