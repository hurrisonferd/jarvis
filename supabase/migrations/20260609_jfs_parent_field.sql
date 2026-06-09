-- JFS parent field: containment/ownership hierarchy (family tree).
-- "JFS-compliant" = JFS + every descendant. Mirrors the parent: field in JD entries
-- and the LAL address-registry. Empty string = root / no parent.
alter table public.jnl_registry add column if not exists parent text not null default '';
alter table public.jd_entries  add column if not exists parent text not null default '';
