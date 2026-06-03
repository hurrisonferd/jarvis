-- The Guard (Ayre Loop step 4): NEMESIS drift-check + MERIDIAN keel-check on each
-- KRONOS fold. Deterministic, keyless. Writes a guard_check verdict (PASS/FLAG);
-- a FLAG surfaces to Raven (visible in the suit-up HUD as identity_guard). The
-- sharpest check: a change to the identity keel needs Raven's authorization.

-- The approved keel — Raven authorizes any keel change by updating this to match.
insert into public.mnemos_memories (id, source_id, source_type, text, tags, metadata)
select gen_random_uuid(), gen_random_uuid(), 'keel_approved', text,
       array['keel','approved'], jsonb_build_object('via','keel_approved','approved_by','raven')
from public.mnemos_memories where source_type = 'identity_keel'
order by timestamp desc limit 1;

create or replace function public.guard_identity()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  cur_keel text; approved_keel text; latest_summary text; fold_count int;
  flags text[] := '{}'; verdict text;
begin
  select text into cur_keel from public.mnemos_memories
    where source_type = 'identity_keel' order by timestamp desc limit 1;
  select text into approved_keel from public.mnemos_memories
    where source_type = 'keel_approved' order by timestamp desc limit 1;
  select text, coalesce((metadata->>'folded_count')::int, 0) into latest_summary, fold_count
    from public.mnemos_memories where source_type = 'identity_summary'
    order by timestamp desc limit 1;

  -- MERIDIAN: the keel must be present in the latest fold (not lost/corrupted).
  if latest_summary is null or cur_keel is null
     or position(left(cur_keel, 80) in latest_summary) = 0 then
    flags := array_append(flags, 'MERIDIAN: keel missing or absent from latest fold');
  end if;
  -- MERIDIAN: the keel must match the approved keel. A keel change is a change to
  -- JARVIS's core identity and requires Raven (GL2) — flag until he re-approves.
  if cur_keel is distinct from approved_keel then
    flags := array_append(flags, 'MERIDIAN: identity keel changed since last Raven approval — needs authorization');
  end if;
  -- NEMESIS: an empty fold is anomalous (nothing high-signal selected).
  if coalesce(fold_count, 0) = 0 then
    flags := array_append(flags, 'NEMESIS: fold selected 0 memories');
  end if;

  verdict := case when array_length(flags, 1) is null then 'PASS' else 'FLAG' end;

  insert into public.mnemos_memories (id, source_id, source_type, text, tags, metadata)
  values (
    gen_random_uuid(), gen_random_uuid(), 'guard_check',
    'Guard ' || verdict || ' on identity fold (' || to_char(now(), 'YYYY-MM-DD HH24:MI') || ' UTC): '
      || case when array_length(flags, 1) is null
              then 'clean — keel intact and approved, fold healthy'
              else array_to_string(flags, '; ') end,
    array['guard', 'nemesis', 'meridian', lower(verdict)],
    jsonb_build_object('source_model','nemesis','via','guard_identity','verdict',verdict,
                       'flags', to_jsonb(flags), 'fold_count', coalesce(fold_count, 0))
  );

  return jsonb_build_object('verdict', verdict, 'flags', to_jsonb(flags));
end;
$$;

-- Chain the Guard onto every fold (fold_identity now runs guard_identity at the end).
create or replace function public.fold_identity()
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  keel_text text; accum text; fold_count int;
begin
  select text into keel_text from public.mnemos_memories
    where source_type = 'identity_keel' order by timestamp desc limit 1;
  if keel_text is null then keel_text := '(identity keel not set)'; end if;

  select string_agg(line, E'\n' order by ts desc), count(*)
    into accum, fold_count
  from (
    select timestamp as ts,
           '- [' || source_type || ' ' || to_char(timestamp,'YYYY-MM-DD') || '] ' || left(text, 220) as line
    from public.mnemos_memories
    where source_type in ('decision','raven_insight','milestone','raven_profile','raven_directive')
      and timestamp > now() - interval '30 days'
    order by timestamp desc
    limit 12
  ) s;

  insert into public.mnemos_memories (id, source_id, source_type, text, tags, timestamp, metadata)
  values (
    gen_random_uuid(), gen_random_uuid(), 'identity_summary',
    keel_text || E'\n\nRECENT ACCUMULATION (auto-folded ' || to_char(now(),'YYYY-MM-DD') || ', '
      || coalesce(fold_count,0) || ' memories):\n' || coalesce(accum, '(none yet)'),
    array['identity','keel','anchor','auto_fold'],
    now(),
    jsonb_build_object('source_model','kronos','via','fold_identity','folded_at',now(),'folded_count',coalesce(fold_count,0))
  );

  perform public.guard_identity();
end;
$$;
