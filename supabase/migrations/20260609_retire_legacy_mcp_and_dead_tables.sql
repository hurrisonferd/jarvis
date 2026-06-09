-- GL7: retire the legacy `mcp` connector's tables (superseded by jarvis-mcp v50)
-- and dead 0-row tables superseded by MNEMOS + the repo record.
-- mcp_tools rows preserved in this record:
--   Emulator Load  — Load ROM into SKADI emulator node
--   GRID Snapshot  — Capture current L0-L5 GRID state
--   GRID Tick      — Advance GRID simulation one tick (KRONOS)
--   Trace Write    — Write event to execution_trace with full tags
-- live_log intentionally KEPT (TRON frontend subscribes to it).
drop table if exists public.mcp_results;
drop table if exists public.mcp_calls;
drop table if exists public.mcp_tools;
drop table if exists public.chaos_seed;
drop table if exists public.session_log;
drop table if exists public.memory_state;
