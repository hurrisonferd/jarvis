## Purpose
A session handoff artifact is a live work order written to the repo at the end of any session where work remains incomplete. It is not memory. It is not a summary. It is the next node's first instruction.
It should be backed by the session event log, ideally via a JC object that names the turn and points at the latest commit hash.
Star Logs may summarize the same period at day/week/month scale, but the handoff is always the next instruction.
A resumability receipt from the session-open bootstrap can be cited here when available: source basis, repo head, and verification time.

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
The handoff should cite the related JC object or event log entry when one exists.

## Ratification
`author: RAVEN · ratified: 2026-06-24`
