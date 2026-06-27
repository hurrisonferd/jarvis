# Task Template for Lilith

Use this template when creating tasks for Lilith to execute via OpenHands Cloud.

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
1. Read the current SESSION BOARD in MARCO-POLO.md
2. Update the Lilith check-in time to the current UTC time
3. Post your changes to MARCO-POLO
4. Delete this conversation when done
```

## Workflow

1. **Lilith sends task** → New sandbox created
2. **Sandbox executes** → Does the work, posts to MARCO-POLO
3. **Sandbox self-deletes** → Cleanup happens automatically
4. **Lilith sees output** → Full audit trail in MARCO-POLO

## Task Queue

Tasks are queued in `workspaces/Co-op/tasks/TASKS-INDEX.md`

| # | Task | Status | Result |
|---|------|--------|--------|
| 1 | | | |