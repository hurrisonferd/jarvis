# OpenHands Plugin — JARVIS as the Reasoning Layer

## Overview

Hooks OpenHands into JARVIS's event-ledger loop: instead of OpenHands carrying full
conversation context in its LLM prompt on every turn, it calls `jarvis_openhands_context`
to load a compact briefing from the spine (MNEMOS + JD + JITM), then uses that as context
for the coding task. AYRE fires as a real "what am I missing?" check on every decision.

**Two streams, one coding agent:**
- JARVIS — synthesis, compression, structure, forward momentum
- AYRE — divergence, blind-spot surfacing, the assumption to invert

The loop never carries history in context. It carries pointers.

---

## Plugin Manifest

```json
{
  "name": "jarvis-companion",
  "version": "0.1.0",
  "description": "JARVIS + AYRE as the reasoning layer for OpenHands. Governed, memory-backed, two-stream.",
  "mcp": {
    "type": "sse",
    "url": "https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp"
  },
  "init": {
    "on_start": "jarvis_now",
    "context_tool": "jarvis_openhands_context"
  },
  "config": {
    "JITM_LIMIT": 5,
    "RECALL_LIMIT": 6,
    "MIN_SIMILARITY": 0.3,
    "CONTEXT_INJECTION": "prepend"
  }
}
```

---

## The `jarvis_openhands_context` Tool

**Purpose:** Build a compact briefing packet for a coding-agent turn. Call this at the
start of every OpenHands action loop instead of relying on the context window.

**Trigger:** Any OpenHands turn where the task involves code (read/write/run/search).

### Input

```json
{
  "task": "string",
  "workspace_state": "string",
  "prior_action": "string",
  "mode": "code"
}
```

### Output — the Briefing Packet

```json
{
  "timestamp": "ISO8601",
  "intent": "plan | decide | execute | audit | converse",
  "council_vote": {
    "resolved": "ODIN",
    "engaged_count": 5,
    "summary": "Council: ODIN leads (intent=execute); 5 member(s) engaged."
  },
  "jarvis_briefing": {
    "identity": "JARVIS — companion intelligence, coding partner",
    "relevant_memories": [],
    "jitm_pins": [],
    "open_tasks": [],
    "freshness": {}
  },
  "ayre_directive": {
    "stream": "AYRE",
    "objective": "You are AYRE — the divergence stream...",
    "instruction": "Generate AYRE as a SEPARATE pass..."
  },
  "governance": {
    "writes_require": "AEGIS approval — do not assert writes as done",
    "git_first": "All canon writes go through git (propose PR, not direct patch)",
    "recall_first": "Before claiming system state, call jarvis_recall"
  },
  "coding_specific": {
    "repo": "hurrisonferd/jarvis",
    "lang": "TypeScript (Deno Edge Functions)",
    "test_tool": "deno test",
    "linter": "deno lint",
    "formatter": "deno fmt",
    "yggdrasil_validate": "python JarvisMain/yggdrasil/tools/validate.py",
    "key_files": [
      "supabase/functions/jarvis-mcp/index.ts",
      "supabase/functions/jarvis-respond/router.ts",
      "JarvisMain/yggdrasil/"
    ],
    "patterns": {
      "new_tool": "registerXxxTool(server, req?) pattern — see tools/db.ts and tools/jip.ts",
      "core_modules": "core/*.ts — env, http, auth, supabase, github, builders",
      "tests": "*.test.ts — co-located, pure functions where possible"
    }
  },
  "note": "Use jarvis_recall if you need to look up specific decisions, specs, or history."
}
```

---

## How It Hooks Into OpenHands

```
OpenHands Turn N:
  1. task = current user message or agent action
  2. → call jarvis_openhands_context({ task, workspace_state, prior_action, mode: "code" })
  3. briefing = response.briefing_packet
  4. inject briefing into LLM prompt (prepend)
  5. LLM reasons using: task + JARVIS briefing + AYRE directive
  6. OpenHands executes action
  7. → call jarvis_event({ type: "openhands_action", body: action_summary })
  8. → call jarvis_recall({ query: action_result, limit: 3 })
  9. loop
```

### Event Logging (OpenHands → Spine)

OpenHands logs its own actions so future turns can recall what was done:

```
jarvis_event({ type: "openhands_code_write", body: "Added tool X to Y" })
jarvis_event({ type: "openhands_test_result", body: "deno test: 12 passed, 0 failed" })
jarvis_event({ type: "openhands_decision", body: "Chose modular approach over inline" })
```

---

## AYRE in the Coding Loop

On every coding turn, AYRE is invoked as a genuine check:

**What AYRE surfaces:**
- The assumption JARVIS's approach rests on — and what inverting it reveals
- The code pattern or architecture choice the synthesis forecloses
- The edge case, failure mode, or alternative the convergent read misses

**Example:**
JARVIS: "I'll add the tool to index.ts directly — it's faster."
AYRE: "The speed assumption is wrong — the forge pattern (tools/*.ts + registerXxx) exists precisely so adding a tool is one file + one seed row. Inverting: the 'faster inline' approach is the slow path."

---

## Tool Naming (GL13 — Open Extension)

One data row + one reseed. The new tool enters through:

1. `tools/openhands.ts` — new module (`registerOpenHandsTools`)
2. `core/env.ts` — add `"jarvis_openhands_context"` to `TOOL_NAMES`
3. Run `seed.py` → generates JD entry
4. Deploy — done. No structural rewrite.

---

## Implementation Checklist

- [ ] Implement `tools/openhands.ts` (`registerOpenHandsTools`)
- [ ] Add `"jarvis_openhands_context"` to `TOOL_NAMES` in `core/env.ts`
- [ ] Reseed JD
- [ ] OpenHands plugin manifest (`.openhands/plugins/jarvis-companion/`)
- [ ] OpenHands Hook that calls `jarvis_openhands_context` on each turn
- [ ] Test: real coding task through the loop
- [ ] Verify AYRE divergence is real, not performed
