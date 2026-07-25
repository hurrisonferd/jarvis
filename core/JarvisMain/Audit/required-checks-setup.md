# Required-Check Enforcement — ✅ DONE (2026-06-25)

> Branch protection applied via API using full-scope PAT (ghp_).
> Admin bypass enabled — Raven can push directly when needed.

## Applied via API

```
PUT /repos/hurrisonferd/jarvis/branches/main/protection

enforce_admins: false          ← Raven can bypass
allow_force_pushes: false      ← No force-push
allow_deletions: false         ← Can't delete main
required_approving_review_count: 1
require_code_owner_reviews: true
required_status_checks:
  - AEGIS — validate the brain
  - parse
  - yggdrasil-validate
  strict: true                  ← Must be up to date
```

## Result

- External contributors: must open PR, pass CI, get code-owner approval
- CI gates enforced on all merges
- Raven: can bypass PR requirement if needed
- No force-push to main — history protected

## What's already enforced in code (no toggle needed)

- `jarvis-integrity.yml` — every push to `main` / `claude/**` and every PR to `main`
- `js-parse-check.yml` — PRs touching `docs/index.html`
- `yggdrasil-validate.yml` — PRs touching `core/JarvisMain/` or `JarvisSide/`
- `CODEOWNERS` — routes every PR to Raven for review

## Jarvis-Private

Branch protection skipped — private repo, single-user, GitHub Free doesn't support
branch protection on private repos anyway. GL2 governance applies.
