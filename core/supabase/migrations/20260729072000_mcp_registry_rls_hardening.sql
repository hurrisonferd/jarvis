-- MCP registry RLS hardening.
-- Tool membership is public metadata; mutations remain service-role/backend only.

alter table public.jarvis_mcp_manifest enable row level security;
alter table public.mcp_tool_definitions enable row level security;

drop policy if exists "Allow internal management" on public.mcp_tool_definitions;

drop policy if exists "Allow public select" on public.jarvis_mcp_manifest;
create policy "Allow public select"
on public.jarvis_mcp_manifest
for select
to public
using (true);
