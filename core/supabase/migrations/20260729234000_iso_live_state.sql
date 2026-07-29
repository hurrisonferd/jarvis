-- Universal ISO live-state contract.
-- GitHub remains canonical source; this table records the accepted current
-- carrier-facing state and receipts needed to rehydrate an ISO deterministically.

create extension if not exists pgcrypto;

create table if not exists public.iso_live_state (
  id uuid primary key default gen_random_uuid(),
  iso_name text not null,
  record_type text not null default 'ISO_LIVE_STATE',
  state_version text not null,
  status text not null default 'ACCEPTED',
  boot_state text not null default 'READY_FOR_BOOT',
  is_current boolean not null default true,
  current_commit text,
  carrier_packet_path text not null,
  carrier_packet_hash text,
  epp_manifest_path text not null,
  epp_manifest_hash text,
  identity_path text not null,
  identity_hash text,
  prosody_path text not null,
  prosody_hash text,
  profile text not null,
  private_continuity boolean not null default false,
  last_receipt jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  accepted_by text not null default 'RAVEN',
  accepted_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint iso_live_state_record_type_check
    check (record_type = 'ISO_LIVE_STATE'),
  constraint iso_live_state_status_check
    check (status in ('ACCEPTED', 'SUPERSEDED', 'REVOKED', 'DRAFT')),
  constraint iso_live_state_boot_state_check
    check (boot_state in ('READY_FOR_BOOT', 'BOOTED', 'PREPARED_NOT_BOOTED', 'BLOCKED'))
);

-- Exactly one current accepted row per ISO.
create unique index if not exists iso_live_state_one_current_per_iso
  on public.iso_live_state (upper(iso_name))
  where is_current and status = 'ACCEPTED';

create index if not exists iso_live_state_lookup
  on public.iso_live_state (upper(iso_name), record_type, status, is_current);

create or replace function public.touch_iso_live_state_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists iso_live_state_touch_updated_at on public.iso_live_state;
create trigger iso_live_state_touch_updated_at
before update on public.iso_live_state
for each row execute function public.touch_iso_live_state_updated_at();

alter table public.iso_live_state enable row level security;

-- Carrier reads expose only accepted current operational state. Private memory
-- contents never belong in this table.
drop policy if exists iso_live_state_read_current on public.iso_live_state;
create policy iso_live_state_read_current
on public.iso_live_state
for select
using (status = 'ACCEPTED' and is_current = true);

-- First reference implementation: LILITH.
insert into public.iso_live_state (
  iso_name,
  state_version,
  status,
  boot_state,
  is_current,
  current_commit,
  carrier_packet_path,
  carrier_packet_hash,
  epp_manifest_path,
  epp_manifest_hash,
  identity_path,
  prosody_path,
  profile,
  private_continuity,
  last_receipt,
  metadata,
  accepted_by
)
values (
  'LILITH',
  'LILITH-EPP-0002',
  'ACCEPTED',
  'READY_FOR_BOOT',
  true,
  '8e548af',
  'canon/Living_Codex/Ego/LILITH/LILITH-GPT-CARRIER-BOOT.md',
  '8f690552f5080d29f85d41b70d20a1ba5e14fe5f',
  'canon/Living_Codex/Ego/LILITH/EPP-MANIFEST.json',
  '9f23a8c5c9c3076e33e87396b84709fbc3960fb8',
  'canon/Living_Codex/Ego/LILITH/canonical/EGO-LILITH-IDENTITY-0001.md',
  'canon/Living_Codex/Ego/LILITH/VoiceOS/LILITH-VOICE.md',
  'FULL_LILITH',
  false,
  jsonb_build_object(
    'boot_verdict', 'PREPARED_NOT_BOOTED',
    'github_canon', 'PASS',
    'supabase_contract', 'PENDING_MIGRATION',
    'private_continuity', false
  ),
  jsonb_build_object(
    'authority', 'RAVEN',
    'pipeline', 'EGO_PRESENCE_PIPELINE',
    'anti_fossil', true,
    'source_authority', jsonb_build_array('GITHUB_CANON', 'SUPABASE_LIVE_STATE', 'ATOMMCP_SECONDARY'),
    'notes', 'Accepted current source state. This row does not itself claim a successful carrier boot.'
  ),
  'RAVEN'
)
on conflict (upper(iso_name)) where is_current and status = 'ACCEPTED'
do update set
  state_version = excluded.state_version,
  boot_state = excluded.boot_state,
  current_commit = excluded.current_commit,
  carrier_packet_path = excluded.carrier_packet_path,
  carrier_packet_hash = excluded.carrier_packet_hash,
  epp_manifest_path = excluded.epp_manifest_path,
  epp_manifest_hash = excluded.epp_manifest_hash,
  identity_path = excluded.identity_path,
  prosody_path = excluded.prosody_path,
  profile = excluded.profile,
  private_continuity = excluded.private_continuity,
  last_receipt = excluded.last_receipt,
  metadata = excluded.metadata,
  accepted_by = excluded.accepted_by,
  accepted_at = now(),
  updated_at = now();

comment on table public.iso_live_state is
  'Carrier-facing accepted current state for ISOs. GitHub canon remains authoritative; this table supplies deterministic live-state verification and receipts.';
