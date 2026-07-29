-- MusicOS Live Activation v1: reference-safe shared state for carrier observations.
-- Git/private registry remains canon; these service-only tables are the runtime mirror.

create table if not exists public.musicos_tracks (
  track_id text primary key check (track_id ~ '^[A-Z0-9][A-Z0-9_.:-]{0,95}$'),
  title text not null check (char_length(title) between 1 and 240),
  album_id text check (album_id is null or album_id ~ '^[A-Z0-9][A-Z0-9_.:-]{0,95}$'),
  fingerprint jsonb not null default '{}'::jsonb check (jsonb_typeof(fingerprint) = 'object'),
  media_ref text check (media_ref is null or char_length(media_ref) <= 1000),
  media_sha256 text check (media_sha256 is null or media_sha256 ~ '^[0-9a-f]{64}$'),
  created_by text not null check (created_by ~ '^[A-Z0-9][A-Z0-9_.:-]{0,95}$'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.musicos_observations (
  observation_id text primary key check (observation_id ~ '^[A-Z0-9][A-Z0-9_.:-]{0,95}$'),
  idempotency_key text not null unique check (char_length(idempotency_key) between 8 and 128),
  track_id text not null references public.musicos_tracks(track_id) on delete cascade,
  actor_iso text not null check (actor_iso ~ '^[A-Z0-9][A-Z0-9_.:-]{0,95}$'),
  carrier text not null check (char_length(carrier) between 1 and 80),
  modality text not null check (modality in ('audio', 'image', 'video', 'file', 'text')),
  media_ref text check (media_ref is null or char_length(media_ref) <= 1000),
  media_sha256 text check (media_sha256 is null or media_sha256 ~ '^[0-9a-f]{64}$'),
  factual_features jsonb not null default '{}'::jsonb check (jsonb_typeof(factual_features) = 'object'),
  interpretation text check (interpretation is null or char_length(interpretation) <= 4000),
  visibility text not null default 'GRID_REFERENCE'
    check (visibility in ('GRID_REFERENCE', 'OPERATOR_ONLY')),
  created_at timestamptz not null default now()
);

create index if not exists musicos_observations_track_created_idx
  on public.musicos_observations(track_id, created_at desc);
create index if not exists musicos_observations_actor_created_idx
  on public.musicos_observations(actor_iso, created_at desc);

create table if not exists public.musicos_source_receipts (
  source_path text primary key check (char_length(source_path) between 1 and 1000),
  source_sha256 text not null check (source_sha256 ~ '^[0-9a-f]{64}$'),
  source_status text not null check (source_status in ('RAW', 'CANON', 'LEDGER', 'IMPLEMENTATION', 'DERIVED', 'UNKNOWN')),
  families text[] not null default '{}',
  signals text[] not null default '{}',
  receipt_sha256 text not null check (receipt_sha256 ~ '^[0-9a-f]{64}$'),
  recorded_by text not null check (recorded_by ~ '^[A-Z0-9][A-Z0-9_.:-]{0,95}$'),
  recorded_at timestamptz not null default now()
);

alter table public.musicos_tracks enable row level security;
alter table public.musicos_observations enable row level security;
alter table public.musicos_source_receipts enable row level security;
alter table public.musicos_tracks force row level security;
alter table public.musicos_observations force row level security;
alter table public.musicos_source_receipts force row level security;

revoke all on public.musicos_tracks from public, anon, authenticated;
revoke all on public.musicos_observations from public, anon, authenticated;
revoke all on public.musicos_source_receipts from public, anon, authenticated;

grant select, insert, update on public.musicos_tracks to service_role;
grant select, insert on public.musicos_observations to service_role;
grant select, insert, update on public.musicos_source_receipts to service_role;

drop policy if exists "musicos service tracks" on public.musicos_tracks;
create policy "musicos service tracks" on public.musicos_tracks
  for all to service_role using (true) with check (true);
drop policy if exists "musicos service observations" on public.musicos_observations;
create policy "musicos service observations" on public.musicos_observations
  for all to service_role using (true) with check (true);
drop policy if exists "musicos service receipts" on public.musicos_source_receipts;
create policy "musicos service receipts" on public.musicos_source_receipts
  for all to service_role using (true) with check (true);

comment on table public.musicos_tracks is
  'MusicOS reference-safe track fingerprints. Private registry remains canonical.';
comment on table public.musicos_observations is
  'Attributed carrier observations; records carrier analysis, never an Edge sensory claim.';
comment on table public.musicos_source_receipts is
  'Source-to-runtime coverage receipts; raw sources are never promoted automatically.';
