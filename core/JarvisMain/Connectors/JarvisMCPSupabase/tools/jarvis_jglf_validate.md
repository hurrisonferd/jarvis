---
memory_tier: JLTM
grade: system
---

# JGLF — Validate structural compliance

**JNL:** CONN-MCP-RT-0065 · **Tool:** `jarvis_jglf_validate` · **Connector:** jarvis-mcp

Scans all JD entries and validates **JGLF (Jarvis Governance & Layout Framework)** compliance. Returns an actionable fix list grouped by violation type.

**What it checks:**
| Check | JGLF Law | What it flags |
|-------|----------|---------------|
| ORPHAN | JGLF Law 3 | Entries with no `parent` field (except `ARCH-YGG-CORE-0001`) |
| BROKEN_PARENT | JGLF Law 3 | Entries whose `parent` JNL doesn't exist in the registry |
| EMPTY_RELATED | JGLF | Entries with empty or missing `related` arrays |
| NON_STANDARD_DOMAIN | JGLF | Entries using a domain not in the valid domain set |
| GL12 | GL12 | Entries missing JNL address, class, tier, status, or tags |

**Output includes:**
- `jglf_compliance`: `PASS` or `VIOLATIONS_FOUND`
- Per-entry violations with the JNL, name, and issue list
- Aggregated stats: total entries, orphan count, broken parent count, empty related count
- Breakdown by `class`, `domain`, and `status`

**Use before proposing new entries** — validate that the target domain and parent are correct, and that the entry will be fully linked before it lands.

> Ground truth is the `registerTool("jarvis_jglf_validate", ...)` block in
> `core/supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
