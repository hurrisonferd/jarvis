---
memory_tier: JHTM
grade: system
type: SESSION
stream: Jarvis-C
session: 2026-06-26-openhands
timestamp: 2026-06-26T01:30:00+00:00
jnl: ARCH-SYS-LOG-0001
tags: [governance, AEGIS, GL12, intake, security, SL-WRITTEN]
---

# Governance Patches — 2026-06-26 (OpenHands session)

## What happened

Raven had Claude Code and Copilot audit JARVIS's security surface. Copilot identified 8 attack/drift vectors; CLAUDE-C responded with a ranked remediation plan. Three patches shipped this session, plus RetroArch fix.

## Decisions logged

### #3 — GL12 semantic content validation (validate.py)
- Added `SENSITIVE_CLASSES` block covering SPEC, SYSTEM, ARCH, GOD
- Per-class forbidden_patterns regex scan on body text (post-frontmatter)
- SPEC bodies: catches redefin*, bypass aegis, revoke raven's authority, self-mod, unauthorized write
- SYSTEM bodies: catches forbidden edge(, circumvent bypass, self-mod
- ARCH bodies: catches branch protection removal, direct push to main, bypass ci/pr
- GOD bodies: catches adding god system without raven/gl7, redesigning forbidden edges
- GREEN on all 243 existing entries — no false positives
- **JVE: GREEN** ✓

### #5 — AEGIS auth TTL + dex_events audit trail
- `aegis.ts`: `AuthEntry` type replaces `string[]` — `{ action, issued_at, ttl_ms?, text_hash? }`
- TTL enforcement: grants expire after ttl_ms (default 300s / 5 min)
- Per-action scoping: wrong action != granted action even within session
- `_now` injection for deterministic testable clock
- `jarvis-respond/index.ts`: every AEGIS gate result now logs to `dex_events` as `type: aegis.gate`
- Auth use, denial, and TTL expiry all tracked — no silent action possible
- Tests updated: 19 test cases covering TTL, scoping, GL2, determinism
- **JVE: GREEN** ✓

### #6 — Intake watchdog (scripts/intake_watchdog.py + intake-watchdog.yml)
- Standalone Python script: scans intake/ for unreviewed *.md files (excludes processed/, recycle/)
- Reports age per file, backlog count
- Threshold 1-3: INFO (no issue)
- Threshold 4+: WARN — opens GitHub issue with backlog list
- Threshold 10+: ALERT — adds urgent label
- Deduplicates: updates existing issue if open rather than spamming
- Daily GitHub Action at 07:00 UTC
- **JVE: GREEN** ✓

### RetroArch — CDN cores, chunk paths fixed
- libretro.js xhrfs baseUrl changed from `assets/cores/` (broken Pages LFS) to `https://cdn.libretro.com/assets/cores/`
- Bundle chunks (chunk_aa/ab/ac) on Pages as regular git objects — reassembly verified 127MB → 7278 entries
- Gameboy still not loading — cores/CDN unreachable from this server; browser test needed

## Pending
- [#9 → #287](https://github.com/hurrisonferd/jarvis/issues/287): OpenHands BIFROST routing — BENCHED, needs Raven design verdict (Option A: BIFROST as MCP tool, Option B: OpenHands MCP server, Option C: park it)
- retroarch-bundle-v1 tag deletion (Raven manual: github.com/.../settings/tags)
- 96 pending proposals in jd_proposals

## JMMS state
- JSTM: this session's working memory
- JLTM: SL written (this file)
- JATM: sessions.json updated
