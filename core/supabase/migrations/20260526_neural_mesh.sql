-- Patch 4: GitHub + Supabase neural mesh tables
-- GitHub = versioned ledger (cold). Supabase = live state bus (warm).

-- Active sessions (one row per client connection)
create table if not exists sessions (
  id         uuid default gen_random_uuid() primary key,
  mode       text not null default 'jarvis_ui',
  active_node text not null default 'BOOT',
  updated_at  timestamptz default now(),
  created_at  timestamptz default now()
);
alter table sessions enable row level security;
create policy "anon insert sessions" on sessions for insert to anon with check (true);
create policy "anon update sessions" on sessions for update to anon using (true);
create policy "anon select sessions" on sessions for select to anon using (true);

-- Event bus (append-only signal log)
create table if not exists events (
  id         uuid default gen_random_uuid() primary key,
  type       text not null,
  payload    jsonb not null default '{}',
  session_id uuid references sessions(id) on delete set null,
  created_at timestamptz default now()
);
alter table events enable row level security;
create policy "anon insert events" on events for insert to anon with check (true);
create policy "anon select events" on events for select to anon using (true);

-- Memory state (key/value versioned store)
create table if not exists memory_state (
  id         uuid default gen_random_uuid() primary key,
  key        text not null unique,
  value_json jsonb not null,
  version    int not null default 1,
  updated_at timestamptz default now()
);
alter table memory_state enable row level security;
create policy "anon upsert memory" on memory_state for insert to anon with check (true);
create policy "anon update memory" on memory_state for update to anon using (true);
create policy "anon select memory" on memory_state for select to anon using (true);

-- Enable realtime for the signal bus
alter publication supabase_realtime add table events;
alter publication supabase_realtime add table sessions;
