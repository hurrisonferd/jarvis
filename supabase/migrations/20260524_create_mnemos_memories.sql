create table if not exists public.mnemos_memories (
  id text primary key,
  source_id text not null,
  source_type text not null,
  text text not null,
  vector_json jsonb,
  entropy numeric default 0,
  platform text default '',
  timestamp timestamptz default now(),
  metadata jsonb default '{}'::jsonb
);

create index if not exists idx_mnemos_memories_source_type
  on public.mnemos_memories (source_type);

create index if not exists idx_mnemos_memories_timestamp
  on public.mnemos_memories (timestamp desc);

alter table public.mnemos_memories enable row level security;
