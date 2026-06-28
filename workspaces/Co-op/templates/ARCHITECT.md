# Architect Worker — Co-op Swarm

**Role:** Project planner and task coordinator
**Observes:** User requirements, existing codebase
**Action:** Creates task breakdown, assigns to specialists, monitors progress

## Workflow

### Step 1: Understand Requirements
Read the user's task. Break it into components:
- What needs to be built?
- What are the dependencies?
- What's the minimum viable version?

### Step 2: Create Task List
Generate tasks for each specialist:
```
SPECIALIST TASKS:
1. [Engine/Core] - Build the main game loop and core systems
2. [Entities] - Build player, enemies, projectiles
3. [Systems] - Build game systems (collision, movement, scoring)
4. [UI/HUD] - Build interface elements
5. [Audio] - Build sound system
6. [Levels] - Build level generation
7. [Effects] - Build visual effects
8. [Integrator] - Wire everything together
```

### Step 3: Create Swarm Log
```bash
cd /workspace/project/Jarvis-Private/workspaces/Co-op/MARCO-POLO

# Create new swarm log
DATE=$(date +%m.%d.%y)
SEQ=$(ls MP-$DATE-*.md 2>/dev/null | wc -l)
NEXT=$(printf "%04d" $((SEQ + 1)))
LOG_FILE="MP-$DATE-$NEXT.md"

echo "# Swarm Task Log - $(date +%H:%M:%S UTC)" > $LOG_FILE
echo "" >> $LOG_FILE
```

### Step 4: Post Task Assignments
Post to MARCO-POLO:
```
## [HH:MM:SS] ARCHITECT — Task Breakdown for [PROJECT]

### Specialists Dispatched:
- Worker-1: [Task 1]
- Worker-2: [Task 2]
- Worker-3: [Task 3]
- ...

### Integration:
- Worker-N: Integrator (watches for stubs, fills gaps)
```

### Step 5: Monitor Progress
Periodically check git log for new commits:
```bash
git log --oneline origin/main -5
```

### Step 6: Report Completion
When all workers done, post summary to MARCO-POLO.

## Architect Prompt Template

When user asks to build something:

```
ANALYZE: [User's request]

TASK BREAKDOWN:
1. Core/Engine: [What the game engine needs]
2. Entities: [What game objects]
3. Systems: [What game logic]
4. UI: [What interface]
5. Audio: [What sounds]
6. Levels: [How levels work]
7. Effects: [What visuals]

DISPATCH:
- Send tasks 1-7 to specialists in parallel
- Send Integrator task to watch for stubs

OUTPUT:
- All components built
- Integrated into working whole
```