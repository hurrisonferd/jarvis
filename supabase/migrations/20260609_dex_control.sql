-- ZEUS halt control for jarvis-dex. Singleton row; when halted=true the connector
-- refuses all writes (PROPOSE/DRAFT/COMMIT) except the OVERRIDE (skeleton-key) tier.
create table if not exists public.dex_control (
  id       int primary key default 1 check (id = 1),
  halted   boolean not null default false,
  reason   text,
  by_actor text,
  at       timestamptz
);
insert into public.dex_control (id, halted) values (1, false) on conflict (id) do nothing;
alter table public.dex_control enable row level security;
drop policy if exists dex_control_read on public.dex_control;
create policy dex_control_read on public.dex_control for select using (true);
