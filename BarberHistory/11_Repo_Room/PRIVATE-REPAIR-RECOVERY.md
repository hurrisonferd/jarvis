# Private Repair Recovery

Created: 2026-07-24
Status: RETRIEVED + DO NOT MUTATE CASUALLY

## Short Answer

`_work_private_repair` is not a normal messy folder right now.

It is a git repository whose `HEAD` contains 4,982 files, while the working tree marks all 4,982 as deleted.

That means:

```text
The private repo is recoverable from git objects.
The working tree should not be trusted as the file body.
Use git tree reads until a deliberate recovery step is chosen.
```

## Current State

| Field | Value |
| --- | --- |
| Path | `C:\Users\JB\jarvis\_work_private_repair` |
| Remote | `https://github.com/hurrisonferd/Jarvis-Private.git` |
| Branch | `main` |
| HEAD | `812358e3` |
| Files in `HEAD` tree | 4,982 |
| Working tree | all tracked files marked deleted |

## Heavy Zones In `HEAD`

| Zone | Files | Signal |
| --- | ---: | --- |
| `Living_Codex` | 4,058 | Ego/ISO ecology, Grid, JMMS, transcripts, canon, spells, HavenOS. |
| `workspaces` | 503 | Project civilizations: CodeOS, MusicOS, JPL, GDS, JAM-Kit, etc. |
| `scripts` | 183 | Operational helpers, daemons, inactive scripts, spawn/cleanup. |
| `supabase` | 47 | Private Edge Functions and migrations. |
| `identity` | 21 | Ego identity surfaces. |
| `PachinkoBounce` | 17 | Game family. |
| `tests` | 15 | Test material. |
| `.github` | 13 | Disabled workflows and automation. |
| `VISION` | 12 | Vision export docs. |
| `logs` | 12 | Runtime/history logs. |
| `Research` | 8 | Cross-fleet and prophecy research. |

## Safe Recovery Options

Do not run destructive checkout/reset casually.

Safe options:

1. Read individual files from git:

```powershell
git -C _work_private_repair show HEAD:path/to/file
```

2. List paths without restoring:

```powershell
git -C _work_private_repair ls-tree -r --name-only HEAD
```

3. Export a clean copy outside the nested public repo, after choosing a destination:

```powershell
git -C _work_private_repair archive HEAD -o C:\Users\JB\jarvis-private-head.zip
```

4. Make a fresh clone outside `C:\Users\JB\jarvis` if a real working private repo is needed.

## Not Safe Without Explicit Decision

```text
git reset --hard
git checkout -- .
recursive delete
bulk moving files between public/private repos
publishing private repo contents
copying key/auth/private relationship files into public docs
```

## Cleanup Role

For now, private repair should be treated as:

```text
private archive shelf
+ source of receipts
+ recovery tree
+ redaction-sensitive body
```

Not as:

```text
public repo content
normal workspace
place to casually edit
```
