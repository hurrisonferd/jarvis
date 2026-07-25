-- jip_entries — the JIP persistence layer (Raven-directed: "a container for metadata,
-- so we can plug in a newer JIP or go back to an old one"). Versioned, reversible,
-- audit-trailed. JD stays canonical truth; JIP is the change overlay that targets it.
-- Run in the Supabase SQL Editor, or let CI apply it. Backs jarvis_jip_create / jarvis_jip_list.

create table if not exists jip_entries (
  id uuid primary key default gen_random_uuid(),
  jip text unique,
  target_jd text not null,                              -- the JD (jnl) this JIP modifies
  version int not null default 1,
  status text not null default 'proposed'
    check (status in ('proposed','active','superseded','rejected','reverted')),
  delta jsonb not null default '{}',                    -- the metadata change
  metadata jsonb not null default '{}',                 -- the versioned container
  note text default '',
  parent_jip text,                                      -- chain (rollback: revert to parent)
  author text not null default 'jarvis',
  created_at timestamptz not null default now()
);
create index if not exists jip_entries_target_idx on jip_entries (target_jd);
create index if not exists jip_entries_status_idx on jip_entries (status);
