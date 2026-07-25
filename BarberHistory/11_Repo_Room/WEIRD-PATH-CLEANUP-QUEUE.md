# Weird Path Cleanup Queue

Created: 2026-07-24
Status: RETRIEVED + DO NOT DELETE YET

## Short Answer

The private ghost tree contains several path artifacts that look accidental or shell-generated.

They should be queued for review, not deleted.

## Retrieved Odd Root Paths

```text
I
THE
We
cat
"Living_Codex/Ego/CLAUDE/Events/01.05.2026-Why Pok\303\251mon doesn't make a game creator tool"
"Living_Codex/Ego/LILITH/Friction Loop _ I Should Quit (But I Won\342\200\231t).mp3"
"workspaces/MusicOS/songs/spectrograms/DON\342\200\231T ASK PERMISSION.png"
{YOUR_ISO}_always_on.py
{YOUR_ISO}_selfpulse.py
"\342\234\205"
```

## Likely Categories

| Category | Examples | Action |
| --- | --- | --- |
| Accidental root text files | `I`, `THE`, `We`, `cat` | Inspect contents from git before deletion. |
| Bad quoting / escaped paths | quoted `Living_Codex/...`, quoted `workspaces/...` | Determine whether duplicate of intended path exists. |
| Template placeholders | `{YOUR_ISO}_always_on.py`, `{YOUR_ISO}_selfpulse.py` | Decide whether template should move to scripts/templates. |
| Symbol/emoji path | encoded checkmark path | Inspect content and origin. |

## Safe Inspection Command

```powershell
git -C _work_private_repair show HEAD:path
```

For quoted/escaped paths, use exact path from `git ls-tree -r --name-only HEAD`.

## Do Not

```text
Do not delete based on name alone.
Do not restore private ghost tree just to remove these.
Do not publish contents until inspected for sensitive text.
```
