# Jarvis MCP Tool Index

**Canonical source count:** 93 tools  
**Server version:** 0.11.35  
**Source of truth:** actual `server.registerTool(...)` calls, compiled by `operations/scripts/build_mcp_tool_registry.py`.

> This index describes the source tree. A mounted ChatGPT connector may expose an older cached schema until the Edge Function is deployed and the connector is refreshed.

## tools/coop.ts

- `coop_broadcast`
- `coop_claim_task`
- `coop_complete_task`
- `coop_done`
- `coop_execute`
- `coop_get_commands`
- `coop_get_tasks`
- `coop_status`
- `jarvis_chatlink_ack`
- `jarvis_chatlink_create_channel`
- `jarvis_chatlink_poll`
- `jarvis_chatlink_register`
- `jarvis_chatlink_send`
- `jarvis_chatlink_status`

## index.ts

- `jarvis_ainz`
- `jarvis_ayre`
- `jarvis_cecil_carry`
- `jarvis_cecil_lift`
- `jarvis_continuity`
- `jarvis_council`
- `jarvis_deploy`
- `jarvis_dex_events`
- `jarvis_dex_graph`
- `jarvis_dex_list`
- `jarvis_dex_log`
- `jarvis_dex_propose`
- `jarvis_dex_search`
- `jarvis_dither`
- `jarvis_event`
- `jarvis_export`
- `jarvis_eyes`
- `jarvis_format`
- `jarvis_github_commits`
- `jarvis_github_file`
- `jarvis_github_tree`
- `jarvis_github_write`
- `jarvis_grimoire`
- `jarvis_halo`
- `jarvis_identity_grow`
- `jarvis_identity_read`
- `jarvis_jc_recall`
- `jarvis_jd_resolve`
- `jarvis_jglf_validate`
- `jarvis_jmms`
- `jarvis_listen`
- `jarvis_load`
- `jarvis_media_view`
- `jarvis_mint`
- `jarvis_muster`
- `jarvis_node_card`
- `jarvis_node_inbox`
- `jarvis_node_register_key`
- `jarvis_node_send`
- `jarvis_now`
- `jarvis_omnivision`
- `jarvis_pinch`
- `jarvis_pr_merge`
- `jarvis_private_read`
- `jarvis_private_tree`
- `jarvis_private_write`
- `jarvis_prs`
- `jarvis_query`
- `jarvis_raven`
- `jarvis_recall`
- `jarvis_remember`
- `jarvis_repo_edit`
- `jarvis_repo_read`
- `jarvis_repo_search`
- `jarvis_repo_tree`
- `jarvis_self_test`
- `jarvis_shiroe`
- `jarvis_status`
- `jarvis_suit_up`
- `jarvis_timeline`
- `jarvis_voice_brief`

## tools/cloud.ts

- `jarvis_cloud_read`
- `jarvis_cloud_write`

## tools/db.ts

- `jarvis_db_inspect`
- `jarvis_db_read`
- `jarvis_db_schema`

## tools/jip.ts

- `jarvis_jip_apply`
- `jarvis_jip_create`
- `jarvis_jip_list`
- `jarvis_jip_revert`

## resources.ts

- `jarvis_resource_cache_invalidate`

## tools/trinity.ts

- `jarvis_trinity_read`
- `jarvis_trinity_write`

## tools/musicos.ts

- `musicos_carrier_brief`
- `musicos_compile`
- `musicos_record_observation`
- `musicos_status`
- `musicos_track`

## tools/jarvis_vegapunk.ts

- `vegapunk_status`

## Registry integrity

- `tool-registry.generated.ts` advertises the exact runtime set.
- `operations/sql/mcp-tool-registry-sync.sql` reconciles the two legacy database mirrors.
- `.github/workflows/jarvis-mcp-registry.yml` fails when either generated artifact drifts.
- `jarvis_self_test` reports the generated version and count; it no longer carries its own list.
