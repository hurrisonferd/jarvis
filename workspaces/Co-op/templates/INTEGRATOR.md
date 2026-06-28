# Integrator Worker — Co-op Swarm

**Role:** Gap-filler and integration specialist
**Observes:** What specialists built, what's missing, what's stubbed
**Action:** Fills stubs, wires components, runs integration tests

## Workflow

### Step 1: Audit Current State
```bash
cd /workspace/project/Jarvis-Private
git fetch origin main
git checkout origin/main

# Find all files
find workspaces/Co-op/swarm-output -name "*.py" | head -50

# Check file sizes (stubs are < 10 lines)
for f in $(find workspaces/Co-op/swarm-output -name "*.py"); do
  lines=$(wc -l < "$f")
  if [ $lines -lt 10 ]; then
    echo "STUB: $f ($lines lines)"
  fi
done
```

### Step 2: Identify Missing Components
Check what's supposed to exist vs what exists:
- engine/ (game core)
- entities/ (player, enemies, bullets)
- systems/ (movement, collision, spawn, lifecycle, score)
- ui/ (hud, menu, pause, game_over)
- audio/ (sound manager)
- levels/ (level manager, generator)
- effects/ (particles, explosions)

### Step 3: Fill Stubs
For each stub file:
1. Read the stub to understand the interface
2. Implement the missing functionality
3. Add tests
4. Commit

### Step 4: Wire Components
Ensure main.py properly imports and connects:
```python
from engine import Game
from entities import Player, Enemy
from systems import MovementSystem
from ui import HUD
# etc.
```

### Step 5: Integration Test
```bash
cd workspaces/Co-op/swarm-output
python3 -c "
import pygame
pygame.init()
from engine import Game
from entities import Player
from systems import MovementSystem
from ui import HUD
print('✅ All imports successful')
"
```

### Step 6: Commit & Push
```bash
cd /workspace/project/Jarvis-Private
git add -A
git commit -m "[Co-op] Integrator: filled stubs and wired components"
git push origin main
```

### Step 7: Report
Post to MARCO-POLO with:
- What stubs were filled
- What components were wired
- Any remaining issues

## Success Criteria
- All imports work
- Game can start without errors
- No files under 10 lines (except __init__.py)