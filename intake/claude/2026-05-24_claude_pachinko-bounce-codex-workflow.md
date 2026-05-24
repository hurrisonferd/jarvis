# Pachinko Bounce Codex Workflow

Source: Claude
Date: 2026-05-24
Requested action: review

## Summary

Claude recommends using Codex with JARVIS as structured context for real coding work, while keeping the distinction clear: JARVIS provides architecture, memory, review framing, and logging, but does not autonomously govern Codex at runtime.

## Details

Achievable workflow:

```text
Codex reads the JARVIS repo
Codex works within God System and Gold Law context
Codex makes targeted code changes
Codex commits back to GitHub
JARVIS MCP provides governance context
Supabase logs decisions
```

Boundary:

```text
Gold Law and God Systems are review/context tools unless enforcement is implemented in code, tests, policies, or CI.
```

Practical recommendation:

```text
Use Codex to build Pachinko Bounce against a well-defined GDD, RGB encoding spec, and Godot 4.x target.
Review output against Gold Law before committing.
```

## General Workflow

This recommendation is not Pachinko-specific. Pachinko Bounce is one example project that should pass through the standard JARVIS governed workflow:

```text
intake
JARVIS/God System context
Gold Law review
scoped implementation
verification
PROMETHEUS rationale logging when needed
GitHub commit/push
JARVIS repo sync
processed/recycle
```

## Suggested Next Step

Add the Pachinko Bounce GDD and RGB encoding spec to intake, then start with the smallest playable Godot slice:

```text
launcher scene
pachinko board
pegs
one RGB ball type
gravity/collision
scoring buckets
restart loop
```
