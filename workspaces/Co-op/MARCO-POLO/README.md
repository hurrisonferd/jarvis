# MARCO-POLO — Swarm Activity Log

Real-time shared log where all swarm workers post their progress.

## Naming Convention

```
MP-MM.DD.YY-####.md
│  │  │  │
│  │  │  └── Sub-log # (0001, 0002, 0003...)
│  │  └─────── Year (26 = 2026)
│  └────────── Day (27, 28...)
└─────────────── Month
```

**Examples:**
- `MP-06.28.26-0001.md` — First log for June 28, 2026
- `MP-06.28.26-0002.md` — Second log (if 0001 got full)
- `MP-06.29.26-0001.md` — New day = reset to 0001

## Auto-Log Rules

| Condition | Action |
|-----------|--------|
| No logs for today | Create `MP-MM.DD.YY-0001.md` |
| Current log ≤ 200 lines | Append to it |
| Current log > 200 lines | Create next sub-log |
| New day | Start fresh at `MP-MM.DD.YY-0001.md` |

## Entry Format

Workers post with HH:MM:SS timestamps:

```markdown
## [HH:MM:SS UTC] Worker — Step N: Description

**Task:** Brief description
**Status:** ✅ DONE / 🔄 IN PROGRESS / ❌ FAILED
**Steps:**
- Step 1: did this
- Step 2: did that
**Files changed:** list

---
```

## How Lilith Watches

```bash
# Watch the latest log
tail -f MARCO-POLO/MP-*.md

# Or pull and view
git pull origin main
cat MARCO-POLO/MP-06.28.26-0002.md
```

## Directory Structure

```
MARCO-POLO/
├── README.md           ← This file
├── 2026-06-27.md       ← Archive (old full-day log)
├── MP-06.27.26-0002.md ← Archive (swarm sessions from yesterday)
├── MP-06.28.26-0001.md ← Today's log #1
└── MP-06.28.26-0002.md ← Today's log #2 (if needed)
```

## For Workers

Workers auto-find the right log via the task template. No manual selection needed.

## Archive Notes

- `2026-06-27.md` — Full daily log from yesterday (259KB, kept for history)
- Sub-logs get consolidated after each day ends