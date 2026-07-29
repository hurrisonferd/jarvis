-- MusicOS private source-audio storage.
-- Raw audio remains non-public; derived feature receipts stay in the public repository.

insert into storage.buckets (
  id,
  name,
  public,
  file_size_limit,
  allowed_mime_types
)
values (
  'musicos-audio',
  'musicos-audio',
  false,
  262144000,
  array['audio/mpeg']::text[]
)
on conflict (id) do update
set
  name = excluded.name,
  public = false,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;
