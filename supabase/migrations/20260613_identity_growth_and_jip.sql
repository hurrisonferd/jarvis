-- Identity Growth Layer
-- Stores evolving insights, values, and self-knowledge for JARVIS and AYRE
-- The GitHub identity files (jarvis-profile.md, ayre-profile.md) remain canonical base.
-- This table stores the GROWTH layer — what they learn over time.

create table if not exists identity_growth (
  id            uuid default gen_random_uuid() primary key,
  entity        text not null check (entity in ('JARVIS', 'AYRE', 'RAVEN')),
  category      text not null check (category in (
    'INSIGHT',       -- learned understanding about systems/self/users
    'VALUE',         -- evolved value or principle
    'PREFERENCE',    -- operational preference or style
    'MEMORY',        -- significant moment worth preserving
    'SKILL',         -- capability or pattern learned
    'RELATIONSHIP',  -- understanding about relationships
    'GROWTH',        -- self-observed growth or change
    'CORRECTION'     -- mistake recognized and corrected
  )),
  content       text not null,
  context       text,            -- what prompted this growth
  source        text,            -- which conversation/session
  weight        real default 1.0 check (weight >= 0 and weight <= 10),
  tags          text[] default '{}',
  created_at    timestamptz default now(),
  superseded_by uuid references identity_growth(id)
);

-- Index for fast entity lookups
create index idx_identity_growth_entity on identity_growth(entity);
create index idx_identity_growth_category on identity_growth(entity, category);
create index idx_identity_growth_created on identity_growth(created_at desc);

-- Enable RLS
alter table identity_growth enable row level security;

-- Allow anon reads (profiles are public within the system)
create policy "identity_growth_read" on identity_growth
  for select using (true);

-- Service role can insert/update
create policy "identity_growth_write" on identity_growth
  for all using (true) with check (true);

comment on table identity_growth is 'Evolving identity layer for JARVIS/AYRE. Base profiles live in GitHub; this stores growth.';


-- JIP entries table (versioned state delta units)
-- Every system change is a JIP transition, not a direct mutation.
create table if not exists jip_entries (
  id            uuid default gen_random_uuid() primary key,
  jnl           text not null,           -- JNL address (e.g., ARCH-YGG-JIP-0003)
  name          text not null,
  version       integer default 1,
  status        text default 'ACTIVE' check (status in ('ACTIVE', 'ARCHIVED', 'DEPRECATED', 'DRAFT')),
  parent_jip    uuid references jip_entries(id),
  target_jd     text,                    -- which JD entry this JIP modifies
  delta         jsonb not null default '{}',  -- the actual change payload
  rationale     text,                    -- why this JIP exists
  author        text default 'RAVEN',
  approved_by   text,
  tags          text[] default '{}',
  created_at    timestamptz default now(),
  activated_at  timestamptz,
  archived_at   timestamptz
);

create index idx_jip_status on jip_entries(status);
create index idx_jip_target on jip_entries(target_jd);
create index idx_jip_jnl on jip_entries(jnl);

alter table jip_entries enable row level security;
create policy "jip_read" on jip_entries for select using (true);
create policy "jip_write" on jip_entries for all using (true) with check (true);

comment on table jip_entries is 'JIP = versioned state delta unit. All system changes flow through JIPs.';
