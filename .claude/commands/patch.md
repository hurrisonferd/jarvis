Run this command in bash and display the results to Raven:

```bash
python3 scripts/jarvis-patch.py $ARGUMENTS
```

The one consistent patch register. A patch is any unit of change worth tracing.
It gets a monotonic ID in chronological order the moment it is OPENED, then keeps
BUILDING (every change appends a dated entry) until it is EXECUTED.

Source of truth: `audit/patch_ledger.json` (this tool is the only writer).

Usage:
- `/patch` or `/patch list` — open + building + pending patches
- `/patch open "Grid inbox attribution (TOFU)" high` — open the next chronological patch
- `/patch add P35 "wired the verifier, tests green"` — append a build entry
- `/patch add P35 "deployed v0.9.14" 99c2954` — append an entry tied to a commit
- `/patch exec P35 "shipped" 99c2954` — mark executed + stamp deploy date
- `/patch defer P35 "blocked on Raven sign-off"` — hold (not rejected)
- `/patch show P35` — full patch with its dated entry trail

Lifecycle: open → executed (or partial / deferred). Open patches surface in the
session brief so a building patch is never lost between sessions.
