# Rooms

`rooms/` is the simple top-level holder for things that should not crowd the repo doorway.

## Rooms

| Room | Purpose |
| --- | --- |
| `repos/` | Local repo checkouts, mirrors, and recovery worktrees. |
| `shelf/` | Parked placeholders that are not active source today. |

## Repo Names

| Path | Meaning |
| --- | --- |
| `repos/private/` | `hurrisonferd/Jarvis-Private` local shell; no valid checked-out HEAD right now. |
| `repos/private-repair/` | Private repair/ghost-tree recovery checkout. |
| `repos/private-work/` | Private work git shell on `main`; no working files checked out right now. |
| `repos/public-main/` | Public `hurrisonferd/jarvis` mirror/snapshot. |

## Rule

```text
Simple names.
Clear rooms.
No panic labels.
```
