# Required-Check Enforcement — one-time setup (Raven only)

CODEOWNERS and the CI workflows are committed. Two things require repo-admin
rights I don't have through any tool — same class as adding a repo secret. Flip
these once in the GitHub UI and the governance spine becomes mandatory, not
advisory.

## GitHub → Settings → Branches → Add branch protection rule

Branch name pattern: `main`

Enable:
- [x] **Require a pull request before merging**
  - [x] Require approvals (1) — CODEOWNERS routes this to you
  - [x] Require review from Code Owners
- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date
  - Add these checks:
    - `AEGIS — validate the brain` (jarvis-integrity)
    - `parse` (js-parse-check)
- [x] **Do not allow bypassing the above settings** (optional — stricter)

## Result

After this: nothing merges to `main` red, and nothing merges without your
review. The Opus 4.8 brain (guard / router / aegis), the server smoke test, the
god-system canon, and the const-bug guard all become merge-blocking. The record
stays clean by construction.

## What's already enforced in code (no toggle needed)

- `jarvis-integrity.yml` runs on every push to `main` and `claude/**` and on
  every PR to `main`.
- `js-parse-check.yml` runs on PRs touching `docs/index.html`.
- `CODEOWNERS` requests your review on every PR automatically.
