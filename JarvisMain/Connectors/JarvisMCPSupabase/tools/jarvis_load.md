---
memory_tier: JLTM
grade: system
---

# Load — Universal Pokédex Resolver

**JNL:** CONN-MCP-RT-0064 · **Tool:** `jarvis_load` · **Connector:** jarvis-mcp

The universal "load" command. Resolves **any** system entity by name, JNL, ID, or concept — no guessing, no inference. Either it resolves fully, or it returns UNRESOLVED with an explicit null.

**Resolution chain (left to right, first match wins):**
```
JD exact JNL → JD numeric ID → name search → JIP lookup → DEX lookup → GitHub file search → HARD NULL
```

**Modes:**
| Mode | Behavior |
|------|----------|
| `FULL` (default) | Recursive with full lineage |
| `STRICT` | Fail if any linked layer is missing |
| `INDEX_ONLY` | Pointer only, no deep read |

**Examples:**
- `'load ayre'` — resolves the AYRE companion stream
- `'load mnemos'` — resolves MNEMOS
- `'load jd 4'` or `'load jid 4'` — resolves by numeric ID
- `'load ARCH-YGG-CORE-0001'` — resolves by JNL
- `'load gold law'` — resolves by concept
- `'load yggdrasil'` — resolves by name

**Never infers. Never guesses.** If a resolution step fails, it falls through to the next. If all steps fail, returns `UNRESOLVED` with the full resolution path shown.

> Ground truth is the `registerTool("jarvis_load", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
