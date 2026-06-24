## Purpose
A session handoff artifact is a live work order written to the repo at the end of any session where work remains incomplete. It is not memory. It is not a summary. It is the next node's first instruction.

## Format
```text
# HANDOFF — [DATE] — [SESSION ID or topic]
status: INCOMPLETE
authored_by: [node name e.g. JARVIS/Claude, Antigravity, Codex]
authorized_scope: [link to governed autonomy contract if applicable]

## Done
- [what was completed this session, specific and checkable]

## Remaining
- [what was not finished, in order of priority]

## Next action
[Single sentence: the exact first thing the next node should do]

## Hard stops encountered
[Any AEGIS holds, scope exits, unresolved decisions — or NONE]

## Raven decisions needed
[Explicit questions that require Raven's input before work can continue — or NONE]
```

## Where it lives
`JarvisMain/Implementation/task/HANDOFF-[YYYYMMDD]-[topic].md`

## Lifecycle
When the next session picks up the work and completes it, the handoff file is moved to `JarvisMain/Implementation/Implemented/` with a completion date appended to the filename.

## Rule
Any node operating under a governed autonomy contract MUST write a handoff artifact if it does not reach the completion condition. No silent exits.

## Ratification
`author: RAVEN · ratified: 2026-06-24`
