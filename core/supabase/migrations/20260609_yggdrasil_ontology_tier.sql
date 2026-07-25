-- Hygiene packet adoptions: ontology class, MAIN/SIDE tier, owner, cross-references.
-- class = SYSTEM/SPEC/MODULE/ENTITY/EVENT/REGISTRY; tier = MAIN/SIDE.

alter table public.jnl_registry add column if not exists class text not null default 'ENTITY';
alter table public.jnl_registry add column if not exists tier  text not null default 'MAIN';
alter table public.jnl_registry add column if not exists owner text;
alter table public.jd_entries   add column if not exists class text not null default 'ENTITY';
alter table public.jd_entries   add column if not exists tier  text not null default 'MAIN';
alter table public.jd_entries   add column if not exists owner text;
alter table public.jd_entries   add column if not exists cross_refs text[] not null default '{}';

alter table public.jnl_registry drop constraint if exists jnl_registry_class_chk;
alter table public.jnl_registry add constraint jnl_registry_class_chk
  check (class in ('SYSTEM','SPEC','MODULE','ENTITY','EVENT','REGISTRY'));
alter table public.jnl_registry drop constraint if exists jnl_registry_tier_chk;
alter table public.jnl_registry add constraint jnl_registry_tier_chk check (tier in ('MAIN','SIDE'));
alter table public.jd_entries drop constraint if exists jd_entries_class_chk;
alter table public.jd_entries add constraint jd_entries_class_chk
  check (class in ('SYSTEM','SPEC','MODULE','ENTITY','EVENT','REGISTRY'));
alter table public.jd_entries drop constraint if exists jd_entries_tier_chk;
alter table public.jd_entries add constraint jd_entries_tier_chk check (tier in ('MAIN','SIDE'));

create index if not exists jnl_registry_tier_idx  on public.jnl_registry (tier);
create index if not exists jnl_registry_class_idx on public.jnl_registry (class);
