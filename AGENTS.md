# AGENTS.md — operating rules for any coding agent in this repo

JARVIS governance lives in `CLAUDE.md`. This file is the cross-agent **lean-code rule**
(Codex, OpenCode, Cursor, Copilot read `AGENTS.md`; Claude Code imports it via `CLAUDE.md`).

## Lean code — ponytail discipline (GL7 at the line level)

Before writing code, stop at the first rung that holds:

1. Does this need to exist? → no: skip it (YAGNI)
2. Stdlib does it? → use it
3. Native platform feature? → use it
4. Installed dependency? → use it
5. One line? → one line
6. Only then: the minimum that works

Lazy, not negligent: trust-boundary validation, data-loss handling, security, and
accessibility are **never** on the chopping block. Mark every deferred shortcut with a
`ponytail:` comment naming its upgrade path, so "later" doesn't become "never."

The best code is the code you never wrote. This is **GL7** (no expansion without
simplification) made concrete: it applies to every agent, every diff. Before a refactor or
a new subsystem, name the concrete capability it unblocks — "cleaner" is not a reason.
