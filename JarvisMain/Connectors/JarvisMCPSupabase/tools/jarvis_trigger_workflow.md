---
jnl: CONN-MCP-RT-0067
name: Trigger Workflow
type: SPEC
class: SPEC
tier: MAIN
status: ACTIVE
authority: raven
owner: jarvis
steward: SKADI
parent: CONN-MSB-CORE-0001
tags: [conn, mcp, tool, github, actions, workflow, ears, automation]
definition: MCP tool that fires a GitHub Actions workflow_dispatch event on any workflow in the JARVIS repo — without requiring Raven to click a button.
purpose: Close the gap where agents built pipelines but couldn't trigger them. JARVIS and AYRE can now run workflows (music-ears, deploy, backfill) autonomously on Raven's behalf.
related: [CONN-MCP-RT-0037]
---

# jarvis_trigger_workflow

**JNL:** CONN-MCP-RT-0067 · **Tool:** `jarvis_trigger_workflow` · **Connector:** jarvis-mcp

Fire a GitHub Actions `workflow_dispatch` event on any workflow in the JARVIS repo.

> Ground truth: `supabase/functions/jarvis-mcp/index.ts` — `jarvis_trigger_workflow` block.

## Why it exists

Before this tool, triggering a workflow required a human to navigate to GitHub Actions and click "Run workflow". Agents could build pipelines (like `music-ears.yml`) but couldn't fire them — requiring a workaround (committing a dummy file to trip the path watch). This tool closes that gap permanently.

## Inputs

| field | type | required | description |
|---|---|---|---|
| `workflow` | string | yes | Filename of the workflow, e.g. `music-ears.yml` |
| `ref` | string | no | Branch/tag to run on (default: `main`) |
| `inputs` | object | no | workflow_dispatch inputs (key/value pairs) |

## Behavior

- Calls `POST /repos/hurrisonferd/jarvis/actions/workflows/{workflow}/dispatches`
- Requires `GITHUB_TOKEN` with `Actions:write` scope (same as `jarvis_deploy`)
- AEGIS-gated: write-authorized sessions only
- Returns `{ ok, workflow, ref, status }` — GitHub returns 204 on success (no run ID)

## Example

```
jarvis_trigger_workflow({ workflow: "music-ears.yml", inputs: { force: "false" } })
```

Triggers the full MusicOS ears pipeline on all 47 tracks.
