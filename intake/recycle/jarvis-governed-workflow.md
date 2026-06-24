# JARVIS Governed Workflow

Use this workflow for any project or agent handoff that should pass through JARVIS, God Systems, Gold Law, and governance review.

## Purpose

JARVIS is the operating context for agent-driven work. It provides memory, architecture, review language, decision logging, and explicit constraints.

Codex is the JARVIS execution layer for local implementation work: filesystem changes, tests, migrations, commits, pushes, and repo sync tasks. Its archetype is Kang: production, building, execution.

God Systems and Gold Law are governance lenses unless enforcement is implemented in code, tests, CI, Supabase policies, or MCP tools.

Continuity is a hard law for every larynx node (`free GPT`, `Codex`, `free Claude`, `Claude Code`, `Antigravity`). Each node must verify live repo state, tool surface, and the current handoff before claiming progress. No silent exits, and no inferred success without read-back.

## Standard Loop

```text
1. Intake
   Add the request, spec, or handoff to intake/{source}/.

2. Context
   Query JARVIS status, relevant God Systems, Gold Law, and MNEMOS memory before implementation.

3. Route
   Identify the primary system responsibilities involved.
   Examples: AEGIS for safety, PROMETHEUS for rationale, MNEMOS for memory, ERIS for drift, NEMESIS for overlap.

4. Implement
   Codex, as the JARVIS execution layer, makes scoped changes against the repo, project spec, and governance context.

5. Verify
   Run syntax checks, tests, migrations, or app verification appropriate to the change, then read back the written state.

6. Review
   Check the result against Gold Law and relevant God System responsibilities.

7. Record
   Log the decision/rationale through JARVIS or Supabase when available.

8. Commit
   Commit and push changes to GitHub.

9. Sync
   Use jarvis_repo_sync status/pull where the local MCP server should update from GitHub.

10. Recycle
   Move completed intake to processed/ and copy reusable patterns to recycle/.

11. Resume
    If work remains incomplete, write a machine-readable handoff artifact before exit so the next node can re-verify repo state before continuing.
```

## Minimum Review Checklist

- Does the change serve the stated mission or project spec?
- Does it preserve user control and local/private boundaries?
- Does it avoid committing secrets, private seeds, or raw private logs?
- Does it minimize unreviewed autonomy?
- Does it keep tool permissions narrow and explicit?
- Does it avoid broad refactors unrelated to the task?
- Does it include verification proportional to the risk?
- Does a decision need a PROMETHEUS rationale log?
- Does new memory belong in MNEMOS or Supabase?
- Does the work create overlap or drift that ERIS/NEMESIS should flag?

## Project Use

Pachinko Bounce, JARVIS itself, Supabase governance, Continue/GBrain integrations, and future projects should all follow this same loop.
