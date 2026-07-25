-- P42: the consolidation/fold (the loop's COMPRESS step) is now driven on a schedule
-- by KRONOS (.github/workflows/jarvis-consolidate.yml, service role). Close the hole the
-- audit found: fold_identity() + guard_identity() were SECURITY DEFINER with PUBLIC +
-- anon EXECUTE, so any anon caller could force or spam a re-fold of JARVIS's identity
-- (GL5/GL6). Revoke from everyone; grant to service_role only. The scheduled job is the
-- sole path that can trigger a re-fold. Applied + verified live 2026-06-04
-- (acl -> postgres=X | service_role=X only).
revoke execute on function public.fold_identity() from public, anon, authenticated;
revoke execute on function public.guard_identity() from public, anon, authenticated;
grant execute on function public.fold_identity() to service_role;
grant execute on function public.guard_identity() to service_role;
