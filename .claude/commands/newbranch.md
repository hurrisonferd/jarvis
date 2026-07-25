Run this command in bash and display the result to Raven:

```bash
bash operations/scripts/newbranch.sh $ARGUMENTS
```

Cuts a new working branch from a freshly-fetched `origin/main` — never from the
current (possibly pre-squash) feature branch. Use this at the start of every new
unit of work to avoid squash-merge conflicts.

Usage: `/newbranch claude/<short-name>`
