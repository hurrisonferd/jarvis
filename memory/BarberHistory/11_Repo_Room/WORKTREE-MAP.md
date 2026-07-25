# Worktree Map

Created: 2026-07-24
Status: RETRIEVED

## Short Answer

There are multiple repo-shaped rooms inside `C:\Users\JB\jarvis`.

The mess is partly real project sprawl and partly local recovery/mirror layout.

## Current Workspace

| Path | Remote | Branch / State | Role |
| --- | --- | --- | --- |
| `C:\Users\JB\jarvis` | `https://github.com/hurrisonferd/jarvis.git` | `main` at `d056efee` | Current public working repo. |
| `C:\Users\JB\jarvis\_work_public_main` | `https://github.com/hurrisonferd/jarvis.git` | detached at `648dc91b` | Public source mirror / archaeology snapshot. |
| `C:\Users\JB\jarvis\_work_private_repair` | `https://github.com/hurrisonferd/Jarvis-Private.git` | `main` at `812358e3`; working files absent/deleted | Private repair git object store / recovery ghost tree. |
| `C:\Users\JB\jarvis\Jarvis-Private` | nested `.git` only visible | unknown without recovery | Local private repo shell. |
| `C:\Users\JB\jarvis\Jarvis-Private-work` | nested `.git` only visible | unknown without recovery | Local private work shell. |
| `C:\Users\JB\jarvis\BarberHistory` | untracked in current public repo | active scaffold | Human-readable index over the chaos. |
| `C:\Users\JB\jarvis\.claude` | local folder | untracked in current public repo | Claude command/settings folder; inspect before deciding track vs ignore. |

## File Counts

| Surface | Count | Meaning |
| --- | ---: | --- |
| Current public repo tracked files | 136 | Small checked-out public slice. |
| Public mirror tracked files | 7,861 | Large public source snapshot. |
| Private repair `HEAD` tree files | 4,982 | Recoverable private source tree. |
| Private repair working-tree deletions | 4,982 | Every tracked file is currently absent from the working tree. |

## Clean Model

```text
current repo = workbench
_work_public_main = public archive shelf
_work_private_repair = private archive shelf / ghost tree
BarberHistory = labels, maps, indexes
Jarvis-Private* = do not touch until recovered or identified
```

## Gitignore Decision

The local mirror/recovery folders are now ignored by the current public repo:

```text
_work_public_main/
_work_private_repair/
Jarvis-Private/
Jarvis-Private-work/
```

Reason:

```text
These are repo rooms nested inside the public repo folder.
They should not appear as accidental untracked source files.
```
