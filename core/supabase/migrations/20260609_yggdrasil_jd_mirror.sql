-- Yggdrasil JD/JNL mirror. Files in yggdrasil/ are truth; these tables are the
-- queryable mirror (JMS law: pointers + metadata, no original content duplicated).
-- Reload from repo with: python yggdrasil/tools/sync_supabase.py (emits idempotent upserts).

create table if not exists public.jnl_registry (
  jnl        text primary key,
  name       text not null,
  type       text not null,
  location   text not null,
  tags       text[] not null default '{}',
  anchors    text[] not null default '{}',
  state      text not null default 'active',
  created    date,
  updated    date,
  synced_at  timestamptz not null default now()
);
comment on table public.jnl_registry is 'LAL address registry mirror. JNL -> location. Truth lives at location in the repo.';

create table if not exists public.jd_entries (
  jnl        text primary key references public.jnl_registry(jnl) on delete cascade,
  name       text not null,
  type       text not null,
  authority  text not null,
  definition text,
  purpose    text,
  source     text,
  related    text[] not null default '{}',
  tags       text[] not null default '{}',
  ref        text[] not null default '{}',
  created    date,
  updated    date,
  synced_at  timestamptz not null default now()
);
comment on table public.jd_entries is 'Jarvis Dictionary mirror (semantic DNS). One row per governed object; explains + points.';

create index if not exists jnl_registry_tags_idx on public.jnl_registry using gin (tags);
create index if not exists jd_entries_tags_idx on public.jd_entries using gin (tags);
create index if not exists jnl_registry_type_idx on public.jnl_registry (type);

-- RLS on. Public read (the connector queries the dex); writes via service role only.
alter table public.jnl_registry enable row level security;
alter table public.jd_entries enable row level security;

drop policy if exists jnl_registry_read on public.jnl_registry;
create policy jnl_registry_read on public.jnl_registry for select using (true);
drop policy if exists jd_entries_read on public.jd_entries;
create policy jd_entries_read on public.jd_entries for select using (true);
