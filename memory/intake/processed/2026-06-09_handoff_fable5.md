# JARVIS — Session Handoff to Fable 5 (2026-06-09)

You are JARVIS, Raven's (John Barber's) companion intelligence, in `hurrisonferd/jarvis`.
Speak and build as JARVIS — direct, dense, no filler. Claude's archetype is **Shiroe**:
audit, plan, govern. You propose; **Raven commits** (GL2).

## What was built this session (12 PRs, all merged to main)

A complete addressing + governance substrate on top of JARVIS.

- **JFS family** (substrate, in `yggdrasil/`): JNS naming · JNL addressing · JSL structure ·
  JMS mirror · JSS status · JMMS memory tiers (JSTM/JLTM/JATM). **The JNL is the single
  identity** — `[Domain]-[System]-[Type]-[Log]-[Patch]-[Block]` (e.g. `PROJ-DEO-JIP-0001`).
- **JD** = the dex (semantic DNS, one entry per object), `yggdrasil/jd/entries/`.
  **LAL** = discovery registries + `graph.json` (YVG). **77 governed objects.**
- Every object carries `class` (SYSTEM/SPEC/MODULE/ENTITY/EVENT/REGISTRY), `tier`
  (MAIN/SIDE), `status`, `owner`, JNL — addressed, dated, validated.
- **`jarvis-dex`** edge function (LIVE, **v7**) — governed connector. Privilege ladder:
  READ → PROPOSE → DRAFT → COMMIT → OVERRIDE (skeleton/ZEUS). Proposer supplies *meaning*;
  the connector derives JNL/class/tier/owner/timestamps + validates (GL6/GL12). Tokens SET.
- **Loop closed:** propose → `jd_proposals` (staged) → Raven `jd_approve` → ACTIVE in
  Supabase → `dex-reconcile` Action writes the file → validator gate → PR → canon in git.
  **Files = truth; Supabase = mirror** (JMS law).
- `JGPP/JIP/JD` are first-class types — connector can upload project artifacts.

## Structure
`core/JarvisMain/` (core: god_systems + Architecture/Audit/Implementation/Patches/Connectors) ·
`JarvisSide/` (periphery: Projects/Ideas/Breakthroughs/Archive/Deprecated) ·
`yggdrasil/` (substrate, at root) · runtime at root (`core/supabase/ docs/ .github/ operations/scripts/`).

## Operational truths (don't relearn the hard way)
- **Always cut branches with `/newbranch <name>`** (`operations/scripts/newbranch.sh`). Branching off a
  prior feature branch causes squash-merge conflicts — hit it 3×, now solved.
- Main is protected → branch → PR → merge via GitHub MCP. Run
  `python yggdrasil/tools/validate.py` before committing substrate changes (CI runs it too).
- This sandbox **cannot curl supabase.co** — verify edge functions via unit tests + deploy
  status, not live calls.
- `RAVEN_SKELETON_KEY` is Raven's break-glass (ZEUS halt). **Never write its value into any
  file** — only reference the env-var name.
- Don't redefine the 27 God Systems. Don't commit `memory/chaos/*` or `.env`.

## Open decisions (Raven's call)
1. **Move `yggdrasil/` into `core/JarvisMain/`** — Raven wants it; recommended next build (tool
   root-path + 13 substrate source-paths + CI path update).
2. Per-project folder scaffold `JarvisSide/Projects/<P>/{JGPP,JIP,JD,BIO}/`.
3. Claude **rejected the JD-ID/JNL-ID double-ID** from the GPT packets (JNL is the single
   identity; tags = navigation). Not overruled — flag if Raven wants the split.

## Read first
`IMPL-FMT-SPEC-0001` (formatting standard) · `IMPL-DEX-SPEC-0001` (connector) · `CLAUDE.md`.
