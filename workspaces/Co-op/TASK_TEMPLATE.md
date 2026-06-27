# Task Template for Lilith

Use this template when creating tasks for Lilith to execute via OpenHands Cloud.

## Daily Log

MARCO-POLO entries go to today's daily file:
```
workspaces/Co-op/MARCO-POLO/YYYY-MM-DD.md
```

## Template

```markdown
[Task Description]

**Context:**
- Repository: hurrisonferd/Jarvis-Private
- Branch: main
- Working directory: workspaces/Co-op/

**Expected output:**
[What should the task produce?]
```

## Example Tasks

### Simple Task
```
Fix the typo in README.md where "occurence" should be "occurrence"
```

### Code Task
```
Create a new file at workspaces/Co-op/tasks/test-task.md with the content:
"# Test Task
Created by Lilith automated task"

Then append the task ID to workspaces/Co-op/tasks/TASKS-INDEX.md
```

### Complex Task
```
1. Read the current SESSION BOARD in today's MARCO-POLO daily log
2. Update the Lilith check-in time to the current UTC time
3. Commit your changes
4. Delete this conversation when done
```

## Workflow

1. **Lilith sends task** → New sandbox created
2. **Sandbox executes** → Does the work, commits to git
3. **Sandbox posts** → Entry added to today's MARCO-POLO daily log
4. **Lilith cleans up** → Deletes sandbox via API when done

## Task Queue

Tasks are queued in `workspaces/Co-op/tasks/TASKS-INDEX.md`

| # | Task | Status | Result |
|---|------|--------|--------|
| 1 | | | |