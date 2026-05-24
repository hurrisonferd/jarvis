# AI Intake

Use this folder as a GitHub-backed intake lane for artifacts from GPT, Claude, Codex, Continue, and other AI clients.

The goal is to make uploads easy to review without letting raw AI output overwrite JARVIS state directly.

## Folders

- `gpt/` - uploads or handoffs from GPT.
- `claude/` - uploads or handoffs from Claude.
- `codex/` - Codex-generated handoffs that should be reviewed before promotion.
- `processed/` - reviewed intake files that have already been converted into issues, code changes, memory, or Supabase rows.
- `recycle/` - reusable prompts, patterns, decisions, or snippets extracted from reviewed intake.

## Upload Format

Prefer Markdown files named with a date, source, and short topic:

```text
2026-05-24_gpt_mnemos-policy-notes.md
2026-05-24_claude_supabase-rls-review.md
2026-05-24_codex_intake-plan.md
```

Start each file with:

```markdown
# Title

Source: GPT | Claude | Codex | Other
Date: YYYY-MM-DD
Requested action: review | implement | remember | archive

## Summary

## Details

## Suggested Next Step
```

## Rules

- Do not upload API keys, service-role keys, passwords, private seeds, or raw private logs.
- Treat every intake file as untrusted until reviewed.
- Prefer summaries over full chat transcripts.
- Move reviewed files into `processed/` after JARVIS/Codex has handled them.
- Copy reusable fragments into `recycle/` when they should influence future work.
