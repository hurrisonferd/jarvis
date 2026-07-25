-- P06/P08/P09: Emulator infrastructure tables
-- GitHub = structure (what exists), Supabase = behavior (what happened)

-- P06: emulator_state — per-session active emulator context
create table if not exists emulator_state (
  id          uuid default gen_random_uuid() primary key,
  session_id  uuid references sessions(id) on delete set null,
  core        text,
  rom_name    text,
  rom_hash    text,
  status      text not null default 'idle' check (status in ('idle','loading','running','paused','failed')),
  updated_at  timestamptz default now(),
  created_at  timestamptz default now()
);
alter table emulator_state enable row level security;
create policy "anon insert emulator_state" on emulator_state for insert to anon with check (true);
create policy "anon update emulator_state" on emulator_state for update to anon using (true);
create policy "anon select emulator_state" on emulator_state for select to anon using (true);

-- P08: rom_library — catalog of known ROMs
create table if not exists rom_library (
  id          uuid default gen_random_uuid() primary key,
  name        text not null,
  system      text not null check (system in ('gb','gbc','gba')),
  file_hash   text,
  file_size   int,
  source      text not null default 'upload',
  storage_url text,
  metadata    jsonb not null default '{}',
  created_at  timestamptz default now()
);
alter table rom_library enable row level security;
create policy "anon insert rom_library" on rom_library for insert to anon with check (true);
create policy "anon select rom_library" on rom_library for select to anon using (true);

-- P09: save_states — snapshot blobs per ROM per session
create table if not exists save_states (
  id          uuid default gen_random_uuid() primary key,
  rom_hash    text,
  rom_name    text,
  session_id  uuid references sessions(id) on delete set null,
  slot        int not null default 0,
  state_blob  jsonb not null default '{}',
  frame_count int,
  created_at  timestamptz default now()
);
alter table save_states enable row level security;
create policy "anon insert save_states" on save_states for insert to anon with check (true);
create policy "anon select save_states" on save_states for select to anon using (true);
create policy "anon update save_states" on save_states for update to anon using (true);

-- Realtime for emulator status broadcast
alter publication supabase_realtime add table emulator_state;
