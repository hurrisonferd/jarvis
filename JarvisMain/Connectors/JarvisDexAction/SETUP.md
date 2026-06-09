# JarvisDexAction — Custom GPT Action setup

Wire the JARVIS custom GPT to the dex connector (`jarvis-dex`, live).

## Steps (GPT editor → Configure → Actions)

1. **Create new action** → paste the contents of `openapi.json` (this folder) into the schema box.
2. **Authentication** → `API Key` → Auth Type `Custom` → Custom Header Name: `x-jarvis-token`
   → Key value: the **DEX_AGENT_TOKEN** value (PROPOSE tier — agents propose, never commit).
   The token values live in Supabase edge-function secrets; never paste them into the GPT's
   instructions or this repo.
3. Privacy policy URL if asked: the repo URL is fine.

## What the GPT can then do

| Tool | Tier | Use |
|---|---|---|
| `jd_lookup {term}` | READ | search the dex by JNL, name, or tag |
| `jnl_resolve {jnl}` | READ | resolve an address to its record |
| `jd_list {status?, class?, tier?, type?, tag?}` | READ | filtered listing ("current state" = `status:ACTIVE`) |
| `jd_graph {jnl}` | READ | node + neighbors (related/cross-refs) |
| `jd_diff {name, domain, system, type, ...}` | READ | preview what a proposal would create |
| `jd_propose {name, domain, system, type, definition, purpose, tags}` | PROPOSE | stage an entry for Raven's approval |

Proposal flow: `jd_propose` → staged in `jd_proposals` → Raven approves (COMMIT tier)
→ ACTIVE in the mirror → `dex-reconcile` Action materializes the file in the repo
(FMT §3 filename, frontmatter, auto-parent) → PR → validator → canon.

The proposer supplies **meaning only**. JNL, class, tier, owner, parent, filename,
location — all derived. JFS compliance is structural, not a skill the GPT needs.

Project codes (the `system` arg for PROJ proposals): see
`JarvisMain/yggdrasil/jfs/project-codes.json`. New project = Raven mints it first
(`new.py --new-project <Name> --code <XYZ>`).
