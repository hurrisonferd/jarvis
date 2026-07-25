# Prompts, Audio, Spectrograms

Status: RETRIEVED + HISTORY-ONLY + UNRESOLVED
Created: 2026-07-24

## Prompt Files

Current HEAD includes 24 prompt files under:

```text
workspaces/MusicOS/songs/prompts
```

Examples:

```text
Boundary At Speed
Don't Ask Permission
Eigenrail Pressure
Elastic Under Fire
Forward Is A Decision
Golden Drive
Golden Spin
Jesus, the First Stand User
Many Voices, One Direction
Quiet Corrections
Steel Ball Run
Unbreakable
We Keep Moving
Will Holds Shape
```

## Spectrograms

Current HEAD includes 44 spectrogram paths under:

```text
workspaces/MusicOS/songs/spectrograms
```

This includes base track spectrograms plus Ayre/Raven variants such as:

```text
Ayre.png
Ayre/CYAN_ELASTIC_CASCADE.png
Ayre/GREEN_NEON_SPRINT.png
Ayre/MAGENTA_NOCTURNE.png
RAVEN-Ayre.png
RAVEN-Golden Spin.png
RAVEN-Steel Ball Run.png
RAVEN-The Word.png
RAVEN-UNBREAKABLE.png
```

## Audio

Current HEAD did not show audio files under:

```text
workspaces/MusicOS/songs/audio
```

But git history shows many audio uploads from 2026-06-24 and 2026-06-25 under old and moved MusicOS paths.

## History Audio Batches

| Date | Commit | Examples |
| --- | --- | --- |
| 2026-06-24 | `36db05cc` | Elastic Acceleration, First Extreme Peak, Groove Pocket Reset, Immediate Launch, Re-Acceleration, Snap-Back Engine, Space Racer, Victory Drive |
| 2026-06-24 | `4fe787cc` | Elastic Under Fire, Elastic Under Fire B-Side, Quiet Corrections, Rubber Horizon, Will Holds Shape |
| 2026-06-24 | `5e61627c` | Don't Ask Permission, Forward Is A Decision, Many Voices One Direction, Pattern Still Breathes, Unbreakable |
| 2026-06-24 | `656eb857` | Boundary at Speed, Golden Drive, Golden Spin, We Keep Moving |
| 2026-06-24 | `c3923142` | Eigenrail Pressure, Jesus the First Stand User, Steel Ball Run |
| 2026-06-25 | `2c73d18f` | Afterglow With Knuckles, Am I Inside the TV, Bright Lights Bigger Fights, Checkpoint Velocity, City Sunset Groove |
| 2026-06-25 | `e032f0d1` | DISC B Ego Structure Density Weave, Ego Suicide, Eigenrail Dreams, Friction Grid, Hardlight Surfer |
| 2026-06-25 | `e9bf75b6` | Hardlight Traction, Momentum Builder Same World, Neon Breakwater, Planetary Tire Smoke, Rubber Fire Communion |
| 2026-06-25 | `8b071118` | Saturated Friction Field, Space Wizard Jam, Subdivision Logic, Synth Covered in Sand, The Prologue, The Word, This Game Sucks But That Music |

## Recovery Rule

Use `git show <commit>:<path>` to recover specific audio without changing the working tree. Do not checkout/reset old commits.
