-- JIP-DEX-0001: staging table for autonomous JD proposals (PROPOSE tier).
-- Proposals never touch canon (jd_entries) until Raven approves (COMMIT tier).

create table if not exists public.jd_proposals (
  id          bigint generated always as identity primary key,
  jnl         text not null,
  name        text not null,
  type        text not null,
  class       text not null,
  tier        text not null,
  owner       text,
  definition  text,
  purpose     text,
  source      text,
  related     text[] not null default '{}',
  tags        text[] not null default '{}',
  status      text not null default 'TASK'
              check (status in ('TASK','EXPANSION')),
  proposer    text not null default 'agent',
  decision    text not null default 'pending'
              check (decision in ('pending','approved','rejected')),
  decided_by  text,
  decided_at  timestamptz,
  created_at  timestamptz not null default now()
);
comment on table public.jd_proposals is 'Staged JD proposals (JIP-DEX-0001). Promoted to jd_entries only on COMMIT-tier approval.';

create index if not exists jd_proposals_decision_idx on public.jd_proposals (decision);
create index if not exists jd_proposals_jnl_idx on public.jd_proposals (jnl);

-- RLS: public read of pending proposals (transparency); writes via service role only (the connector).
alter table public.jd_proposals enable row level security;
drop policy if exists jd_proposals_read on public.jd_proposals;
create policy jd_proposals_read on public.jd_proposals for select using (true);

-- Append-only governance event log for the dex connector (GL5).
create table if not exists public.dex_events (
  id          bigint generated always as identity primary key,
  tool        text not null,
  tier        text not null,
  jnl         text,
  actor       text,
  detail      jsonb,
  created_at  timestamptz not null default now()
);
comment on table public.dex_events is 'Append-only event log for jarvis-dex actions (GL5).';
alter table public.dex_events enable row level security;
drop policy if exists dex_events_read on public.dex_events;
create policy dex_events_read on public.dex_events for select using (true);
