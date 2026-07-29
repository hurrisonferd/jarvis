-- SAT ChatLink v0.2
-- Supabase carries the live pulse; EGO/Grid/shared receives selected receipts.
-- All access is service-role mediated through jarvis-mcp. No anon/authenticated
-- table or RPC access is granted by this migration.

create extension if not exists pgcrypto;

create table if not exists public.grid_chat_satellites (
  satellite_id text primary key,
  iso_name text not null,
  carrier text not null,
  thread_ref text not null,
  display_name text,
  status text not null default 'ACTIVE'
    check (status in ('ACTIVE', 'PAUSED', 'OFF')),
  capabilities jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  last_seen timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique (carrier, thread_ref)
);

create table if not exists public.grid_chat_channels (
  channel_id text primary key,
  kind text not null check (kind in ('DM', 'ROOM')),
  mission_id text,
  created_by text not null default 'RAVEN',
  visibility text not null default 'GRID'
    check (visibility in ('PUBLIC', 'GRID', 'CHANNEL', 'OPERATOR_ONLY')),
  next_sequence bigint not null default 1 check (next_sequence > 0),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  check (
    (kind = 'DM' and channel_id like 'DM:%' and mission_id is null)
    or
    (kind = 'ROOM' and channel_id like 'ROOM:%' and mission_id is not null)
  )
);

create table if not exists public.grid_chat_members (
  channel_id text not null
    references public.grid_chat_channels(channel_id) on delete cascade,
  iso_name text not null,
  member_role text not null default 'MEMBER'
    check (member_role in ('OWNER', 'MEMBER', 'OBSERVER')),
  joined_at timestamptz not null default now(),
  primary key (channel_id, iso_name)
);

create table if not exists public.grid_chat_cursors (
  channel_id text not null
    references public.grid_chat_channels(channel_id) on delete cascade,
  satellite_id text not null
    references public.grid_chat_satellites(satellite_id) on delete cascade,
  last_seen_sequence bigint not null default 0 check (last_seen_sequence >= 0),
  updated_at timestamptz not null default now(),
  primary key (channel_id, satellite_id)
);

alter table public.grid_p2p_messages
  add column if not exists schema_version text,
  add column if not exists channel_id text
    references public.grid_chat_channels(channel_id) on delete restrict,
  add column if not exists sequence bigint,
  add column if not exists message_id text,
  add column if not exists from_iso text,
  add column if not exists from_satellite text
    references public.grid_chat_satellites(satellite_id) on delete restrict,
  add column if not exists from_thread text,
  add column if not exists recipients text[],
  add column if not exists message_type text,
  add column if not exists body_sha256 text,
  add column if not exists artifact_sha256 text,
  add column if not exists causal_parent text,
  add column if not exists visibility text,
  add column if not exists consent text,
  add column if not exists ack_required boolean not null default false,
  add column if not exists previous_event_sha256 text,
  add column if not exists event_sha256 text;

create unique index if not exists grid_p2p_messages_channel_sequence_uq
  on public.grid_p2p_messages(channel_id, sequence)
  where channel_id is not null;

create unique index if not exists grid_p2p_messages_message_id_uq
  on public.grid_p2p_messages(message_id)
  where message_id is not null;

create index if not exists grid_p2p_messages_channel_created_idx
  on public.grid_p2p_messages(channel_id, created_at);

create index if not exists grid_p2p_messages_recipients_gin
  on public.grid_p2p_messages using gin(recipients);

alter table public.grid_chat_satellites enable row level security;
alter table public.grid_chat_channels enable row level security;
alter table public.grid_chat_members enable row level security;
alter table public.grid_chat_cursors enable row level security;
alter table public.grid_p2p_messages enable row level security;

revoke all on public.grid_chat_satellites from anon, authenticated;
revoke all on public.grid_chat_channels from anon, authenticated;
revoke all on public.grid_chat_members from anon, authenticated;
revoke all on public.grid_chat_cursors from anon, authenticated;
revoke all on public.grid_p2p_messages from anon, authenticated;

grant select, insert, update, delete on public.grid_chat_satellites to service_role;
grant select, insert, update, delete on public.grid_chat_channels to service_role;
grant select, insert, update, delete on public.grid_chat_members to service_role;
grant select, insert, update, delete on public.grid_chat_cursors to service_role;
grant select, insert, update, delete on public.grid_p2p_messages to service_role;

drop policy if exists "chatlink service satellites" on public.grid_chat_satellites;
create policy "chatlink service satellites"
  on public.grid_chat_satellites for all to service_role
  using (true) with check (true);

drop policy if exists "chatlink service channels" on public.grid_chat_channels;
create policy "chatlink service channels"
  on public.grid_chat_channels for all to service_role
  using (true) with check (true);

drop policy if exists "chatlink service members" on public.grid_chat_members;
create policy "chatlink service members"
  on public.grid_chat_members for all to service_role
  using (true) with check (true);

drop policy if exists "chatlink service cursors" on public.grid_chat_cursors;
create policy "chatlink service cursors"
  on public.grid_chat_cursors for all to service_role
  using (true) with check (true);

drop policy if exists "chatlink service messages" on public.grid_p2p_messages;
create policy "chatlink service messages"
  on public.grid_p2p_messages for all to service_role
  using (true) with check (true);

create or replace function public.grid_chat_register(
  p_satellite_id text,
  p_iso_name text,
  p_carrier text,
  p_thread_ref text,
  p_display_name text default null,
  p_status text default 'ACTIVE',
  p_max_active integer default 4,
  p_metadata jsonb default '{}'::jsonb
) returns public.grid_chat_satellites
language plpgsql
security invoker
set search_path = public, pg_temp
as $$
declare
  v_satellite_id text := upper(trim(p_satellite_id));
  v_iso_name text := upper(trim(p_iso_name));
  v_status text := upper(trim(p_status));
  v_result public.grid_chat_satellites;
begin
  if v_satellite_id !~ '^[A-Z0-9][A-Z0-9_.-]{0,63}$'
     or v_iso_name !~ '^[A-Z0-9][A-Z0-9_.-]{0,63}$' then
    raise exception 'invalid satellite or ISO identity';
  end if;
  if v_status not in ('ACTIVE', 'PAUSED', 'OFF') then
    raise exception 'invalid satellite status';
  end if;
  if p_max_active < 1 then
    raise exception 'max active satellites must be positive';
  end if;

  perform pg_advisory_xact_lock(hashtext('grid_chat_active_satellites'));
  if v_status = 'ACTIVE' and (
    select count(*) from public.grid_chat_satellites
    where status = 'ACTIVE' and satellite_id <> v_satellite_id
  ) >= p_max_active then
    raise exception 'SAT active-satellite policy cap (%) reached', p_max_active;
  end if;

  insert into public.grid_chat_satellites (
    satellite_id, iso_name, carrier, thread_ref, display_name, status,
    metadata, last_seen
  ) values (
    v_satellite_id, v_iso_name, trim(p_carrier), trim(p_thread_ref),
    p_display_name, v_status, coalesce(p_metadata, '{}'::jsonb), now()
  )
  on conflict (satellite_id) do update set
    iso_name = excluded.iso_name,
    carrier = excluded.carrier,
    thread_ref = excluded.thread_ref,
    display_name = excluded.display_name,
    status = excluded.status,
    metadata = excluded.metadata,
    last_seen = now()
  returning * into v_result;

  return v_result;
end;
$$;

create or replace function public.grid_chat_create_channel(
  p_channel_id text,
  p_participants text[],
  p_created_by text default 'RAVEN',
  p_visibility text default 'GRID',
  p_metadata jsonb default '{}'::jsonb
) returns public.grid_chat_channels
language plpgsql
security invoker
set search_path = public, pg_temp
as $$
declare
  v_channel_id text := upper(trim(p_channel_id));
  v_participants text[];
  v_kind text;
  v_mission_id text;
  v_existing text[];
  v_result public.grid_chat_channels;
begin
  select array_agg(distinct upper(trim(x)) order by upper(trim(x)))
    into v_participants
  from unnest(p_participants) as x;

  if v_channel_id like 'DM:%' then
    v_kind := 'DM';
    if coalesce(cardinality(v_participants), 0) <> 2
       or v_channel_id <> 'DM:' || v_participants[1] || ':' || v_participants[2] then
      raise exception 'DM id must be canonical and match two participants';
    end if;
  elsif v_channel_id like 'ROOM:%' then
    v_kind := 'ROOM';
    v_mission_id := substring(v_channel_id from 6);
    if coalesce(cardinality(v_participants), 0) < 2 or v_mission_id = '' then
      raise exception 'ROOM requires a mission id and at least two participants';
    end if;
  else
    raise exception 'channel id must start with DM: or ROOM:';
  end if;

  insert into public.grid_chat_channels (
    channel_id, kind, mission_id, created_by, visibility, metadata
  ) values (
    v_channel_id, v_kind, v_mission_id, upper(trim(p_created_by)),
    upper(trim(p_visibility)), coalesce(p_metadata, '{}'::jsonb)
  )
  on conflict (channel_id) do nothing;

  select array_agg(iso_name order by iso_name) into v_existing
  from public.grid_chat_members where channel_id = v_channel_id;
  if v_existing is not null and v_existing <> v_participants then
    raise exception 'channel exists with a different participant contract';
  end if;

  insert into public.grid_chat_members(channel_id, iso_name, member_role)
  select v_channel_id, iso_name,
    case when iso_name = upper(trim(p_created_by)) then 'OWNER' else 'MEMBER' end
  from unnest(v_participants) as iso_name
  on conflict (channel_id, iso_name) do nothing;

  select * into v_result from public.grid_chat_channels
  where channel_id = v_channel_id;
  return v_result;
end;
$$;

create or replace function public.grid_chat_send(
  p_channel_id text,
  p_from_satellite text,
  p_message_type text,
  p_body text,
  p_recipients text[] default null,
  p_message_id text default null,
  p_visibility text default 'CHANNEL',
  p_consent text default 'RAVEN_AUTHORIZED',
  p_causal_parent text default null,
  p_artifact_sha256 text default null,
  p_ack_required boolean default false
) returns public.grid_p2p_messages
language plpgsql
security invoker
set search_path = public, pg_temp
as $$
declare
  v_channel_id text := upper(trim(p_channel_id));
  v_satellite_id text := upper(trim(p_from_satellite));
  v_message_type text := upper(trim(p_message_type));
  v_visibility text := upper(trim(p_visibility));
  v_sender public.grid_chat_satellites;
  v_recipients text[];
  v_sequence bigint;
  v_previous text := repeat('0', 64);
  v_message_id text;
  v_body_sha text;
  v_event_sha text;
  v_created_at timestamptz := clock_timestamp();
  v_existing public.grid_p2p_messages;
  v_result public.grid_p2p_messages;
begin
  select * into v_sender from public.grid_chat_satellites
  where satellite_id = v_satellite_id and status = 'ACTIVE';
  if not found then
    raise exception 'sender satellite is not ACTIVE or registered';
  end if;
  if not exists (
    select 1 from public.grid_chat_members
    where channel_id = v_channel_id and iso_name = v_sender.iso_name
  ) then
    raise exception 'sender ISO is not a channel member';
  end if;
  if v_message_type not in (
    'NOTE', 'REQUEST', 'RESPONSE', 'HANDOFF', 'ACK', 'BLOCKER',
    'HEARTBEAT', 'RECEIPT'
  ) then
    raise exception 'unsupported message type';
  end if;
  if v_visibility not in (
    'PUBLIC', 'GRID', 'CHANNEL', 'OPERATOR_ONLY', 'PRIVATE_REFERENCE'
  ) then
    raise exception 'unsupported visibility';
  end if;
  if octet_length(p_body) > 8000 then
    raise exception 'message body exceeds 8000 bytes';
  end if;

  if p_recipients is null then
    select array_agg(iso_name order by iso_name) into v_recipients
    from public.grid_chat_members where channel_id = v_channel_id;
  else
    select array_agg(distinct upper(trim(x)) order by upper(trim(x)))
      into v_recipients from unnest(p_recipients) as x;
  end if;
  if coalesce(cardinality(v_recipients), 0) = 0 then
    raise exception 'message requires at least one recipient';
  end if;
  if exists (
    select 1 from unnest(v_recipients) as recipient
    where not exists (
      select 1 from public.grid_chat_members
      where channel_id = v_channel_id and iso_name = recipient
    )
  ) then
    raise exception 'recipient is not a channel member';
  end if;
  if v_visibility = 'PRIVATE_REFERENCE' and (
    p_artifact_sha256 is null
    or p_artifact_sha256 !~ '^[0-9a-fA-F]{64}$'
    or octet_length(p_body) > 240
  ) then
    raise exception 'PRIVATE_REFERENCE requires an artifact hash and short summary';
  end if;

  v_body_sha := encode(extensions.digest(p_body, 'sha256'), 'hex');
  v_message_id := coalesce(
    nullif(trim(p_message_id), ''),
    'MSG-' || upper(substr(encode(extensions.digest(
      v_channel_id || '|' || v_sender.iso_name || '|' ||
      v_message_type || '|' || v_body_sha || '|' || v_created_at::text,
      'sha256'
    ), 'hex'), 1, 24))
  );

  select * into v_existing from public.grid_p2p_messages
  where message_id = v_message_id;
  if found then
    if v_existing.channel_id <> v_channel_id
       or v_existing.from_iso <> v_sender.iso_name
       or v_existing.message_type <> v_message_type
       or v_existing.body_sha256 <> v_body_sha
       or v_existing.recipients <> v_recipients then
      raise exception 'message_id already exists with different content';
    end if;
    return v_existing;
  end if;

  select next_sequence into v_sequence
  from public.grid_chat_channels
  where channel_id = v_channel_id
  for update;
  if not found then
    raise exception 'unknown channel';
  end if;

  select event_sha256 into v_previous
  from public.grid_p2p_messages
  where channel_id = v_channel_id
  order by sequence desc limit 1;
  v_previous := coalesce(v_previous, repeat('0', 64));

  v_event_sha := encode(extensions.digest(
    jsonb_build_object(
      'schema_version', 'sat.chatlink.v0.2',
      'channel_id', v_channel_id,
      'sequence', v_sequence,
      'message_id', v_message_id,
      'from_iso', v_sender.iso_name,
      'from_satellite', v_sender.satellite_id,
      'from_thread', v_sender.thread_ref,
      'recipients', to_jsonb(v_recipients),
      'message_type', v_message_type,
      'body_sha256', v_body_sha,
      'artifact_sha256', p_artifact_sha256,
      'causal_parent', p_causal_parent,
      'visibility', v_visibility,
      'consent', p_consent,
      'ack_required', p_ack_required,
      'created_at', v_created_at,
      'previous_event_sha256', v_previous
    )::text,
    'sha256'
  ), 'hex');

  insert into public.grid_p2p_messages (
    created_at, updated_at, sender, target_iso, target_conv_id, message,
    status, transport, metadata, schema_version, channel_id, sequence,
    message_id, from_iso, from_satellite, from_thread, recipients,
    message_type, body_sha256, artifact_sha256, causal_parent, visibility,
    consent, ack_required, previous_event_sha256, event_sha256
  ) values (
    v_created_at, v_created_at, v_sender.iso_name,
    case when cardinality(v_recipients) = 1 then v_recipients[1] else 'GRID' end,
    null, p_body, 'queued', 'supabase-chatlink',
    jsonb_build_object('chatlink', true), 'sat.chatlink.v0.2', v_channel_id,
    v_sequence, v_message_id, v_sender.iso_name, v_sender.satellite_id,
    v_sender.thread_ref, v_recipients, v_message_type, v_body_sha,
    p_artifact_sha256, p_causal_parent, v_visibility, p_consent,
    p_ack_required, v_previous, v_event_sha
  ) returning * into v_result;

  update public.grid_chat_channels
  set next_sequence = v_sequence + 1
  where channel_id = v_channel_id;

  return v_result;
end;
$$;

create or replace function public.grid_chat_poll(
  p_satellite_id text,
  p_channel_id text,
  p_limit integer default 100,
  p_advance boolean default true
) returns setof public.grid_p2p_messages
language plpgsql
security invoker
set search_path = public, pg_temp
as $$
declare
  v_satellite public.grid_chat_satellites;
  v_channel_id text := upper(trim(p_channel_id));
  v_cursor bigint := 0;
  v_high_water bigint;
begin
  if p_limit < 1 or p_limit > 500 then
    raise exception 'poll limit must be between 1 and 500';
  end if;
  select * into v_satellite from public.grid_chat_satellites
  where satellite_id = upper(trim(p_satellite_id)) and status = 'ACTIVE';
  if not found then
    raise exception 'satellite is not ACTIVE or registered';
  end if;
  if not exists (
    select 1 from public.grid_chat_members
    where channel_id = v_channel_id and iso_name = v_satellite.iso_name
  ) then
    raise exception 'satellite ISO is not a channel member';
  end if;

  select last_seen_sequence into v_cursor
  from public.grid_chat_cursors
  where channel_id = v_channel_id
    and satellite_id = v_satellite.satellite_id;
  v_cursor := coalesce(v_cursor, 0);

  select max(sequence) into v_high_water from (
    select sequence from public.grid_p2p_messages
    where channel_id = v_channel_id
      and sequence > v_cursor
      and recipients @> array[v_satellite.iso_name]
    order by sequence
    limit p_limit
  ) unread;

  return query
    select * from public.grid_p2p_messages
    where channel_id = v_channel_id
      and sequence > v_cursor
      and recipients @> array[v_satellite.iso_name]
    order by sequence
    limit p_limit;

  if p_advance and v_high_water is not null then
    insert into public.grid_chat_cursors(
      channel_id, satellite_id, last_seen_sequence, updated_at
    ) values (
      v_channel_id, v_satellite.satellite_id, v_high_water, now()
    )
    on conflict (channel_id, satellite_id) do update set
      last_seen_sequence = greatest(
        public.grid_chat_cursors.last_seen_sequence,
        excluded.last_seen_sequence
      ),
      updated_at = now();
  end if;
end;
$$;

create or replace function public.grid_chat_ack(
  p_satellite_id text,
  p_channel_id text,
  p_message_id text
) returns public.grid_p2p_messages
language plpgsql
security invoker
set search_path = public, pg_temp
as $$
declare
  v_source public.grid_p2p_messages;
begin
  select * into v_source from public.grid_p2p_messages
  where channel_id = upper(trim(p_channel_id))
    and message_id = p_message_id;
  if not found then
    raise exception 'unknown message_id';
  end if;
  return public.grid_chat_send(
    upper(trim(p_channel_id)),
    upper(trim(p_satellite_id)),
    'ACK',
    'ACK',
    array[v_source.from_iso],
    'ACK:' || upper(trim(p_satellite_id)) || ':' || p_message_id,
    'CHANNEL',
    'RAVEN_AUTHORIZED',
    p_message_id,
    null,
    false
  );
end;
$$;

revoke all on function public.grid_chat_register(
  text, text, text, text, text, text, integer, jsonb
) from public, anon, authenticated;
revoke all on function public.grid_chat_create_channel(
  text, text[], text, text, jsonb
) from public, anon, authenticated;
revoke all on function public.grid_chat_send(
  text, text, text, text, text[], text, text, text, text, text, boolean
) from public, anon, authenticated;
revoke all on function public.grid_chat_poll(
  text, text, integer, boolean
) from public, anon, authenticated;
revoke all on function public.grid_chat_ack(
  text, text, text
) from public, anon, authenticated;

grant execute on function public.grid_chat_register(
  text, text, text, text, text, text, integer, jsonb
) to service_role;
grant execute on function public.grid_chat_create_channel(
  text, text[], text, text, jsonb
) to service_role;
grant execute on function public.grid_chat_send(
  text, text, text, text, text[], text, text, text, text, text, boolean
) to service_role;
grant execute on function public.grid_chat_poll(
  text, text, integer, boolean
) to service_role;
grant execute on function public.grid_chat_ack(
  text, text, text
) to service_role;

do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime'
      and schemaname = 'public'
      and tablename = 'grid_p2p_messages'
  ) then
    alter publication supabase_realtime add table public.grid_p2p_messages;
  end if;
end;
$$;

comment on table public.grid_chat_satellites is
  'SAT ChatLink carrier-thread registry. Service-role only.';
comment on table public.grid_chat_channels is
  'SAT ChatLink canonical DM and mission-room registry. Service-role only.';
comment on table public.grid_chat_members is
  'ISO membership for SAT ChatLink channels. Service-role only.';
comment on table public.grid_chat_cursors is
  'Per-satellite unread cursor for SAT ChatLink channels. Service-role only.';
