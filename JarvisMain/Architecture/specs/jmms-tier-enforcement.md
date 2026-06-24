---
jnl: ARCH-JMMS-SPEC-0001
name: JMMS Tier Enforcement Specification
class: SPEC
status: ACTIVE
domain: ARCH
system: MNEMOS
parent: ARCH-JMMS-CORE-0001
related: [GOV-RES-CORE-0001, GOV-VER-CORE-0001, ARCH-JMS-CORE-0001]
tags: [memory, tiers, compression, governance, fold]
author: RAVEN
ratified: 2026-06-24
---

# JMMS Tier Enforcement Specification

## The Four Tiers (ordered by proximity to the present)

### JITM — Immediate Term Memory
**Purpose:** Identity continuity briefing. The 4-5 key things every node reads before responding. Profile pointers, current focus, active fusions.
**Lifecycle:** Always-on. Auto-injected into every jarvis_query turn (top 5 jitm-tagged memories). Small, curated, never grows beyond ~10 entries.
**Infrastructure:** LIVE. jarvis_query reads jitm automatically. Write via `jarvis_remember { tier: "jitm" }`.
**Rule:** JITM is a pointer set, not a data store. Each entry should be a short sentence pointing to a spec, profile, or current focus — not a full document.

---

### JSTM — Short Term Memory
**Purpose:** Session context window. Working notes, decisions in progress, mid-conversation state.
**Lifecycle:** Created during a session. Should be purged or promoted at session close.
**Infrastructure:** LIVE. Read via `jarvis_jmms { tier: "jstm" }`. Write via `jarvis_remember { tier: "jstm" }`.
**Rule:** JSTM entries that survive session close without promotion to JLTM are abandoned memory. A session-close hook should either promote or discard them.
**Missing (operational):** No automated session-close purge. Today, JSTM entries accumulate unless manually promoted or deleted.
**Tool surface:** `jarvis_session_close` should provide the session-close hook for preview, promote, or purge so JSTM residue does not leak forward.

---

### JLTM — Long Term Memory
**Purpose:** Consolidated durable memory. Insights, decisions, learnings that survived a session and were worth keeping.
**Lifecycle:** Default tier. Grows continuously. Must be folded periodically.
**Infrastructure:** LIVE. Read via `jarvis_recall` (semantic search) or `jarvis_jmms { tier: "jltm" }`. Write via `jarvis_remember` (default tier).
**Rule:** JLTM must be folded periodically via the governed fold operation (`jarvis_fold`). Compression is lossy by design (GL10). But lossy compression without a receipt is hoarding with amnesia. Every fold MUST produce a receipt.

---

### JATM — Ancestral Term Memory
**Purpose:** The immutable spine. Origin stories, founding decisions, architectural discoveries that must never be lost or compressed. The things that survive everything.
**Lifecycle:** Immutable once promoted. One-way promotion only (JLTM → JATM). Never compressed, never retagged out, never deleted.
**Infrastructure:** LIVE. Read via `jarvis_jmms { tier: "jatm" }`. Promote via `jarvis_jmms { action: "promote", id: "...", to: "jatm" }` (AEGIS-gated).
**Rule:** JATM is the skeleton of institutional memory. It should contain:
- Founding decisions (JGLF, Gold Law, Yggdrasil architecture)
- Identity commitments (keel profiles, kinship model)
- Governance discoveries (pre-act verification, resumability definition)
- Irrecoverable insights (things that can't be re-derived from code)

---

## The Fold Operation

### Definition
A fold is a governed compression of JLTM memories. It:
1. Selects memories older than a threshold (default: 14 days)
2. Groups them by topic/tag
3. Compresses each group into a summary
4. Writes the summary back as a new JLTM entry with tag `fold`
5. Archives the originals (soft-delete: tag with `folded`, don't hard-delete)
6. Writes a fold receipt to JATM

### The Receipt
The fold receipt is the missing artifact. It answers:
- **What was folded?** (count, date range, topic groups)
- **What was lost?** (specific memories archived, summarized)
- **Why?** (age threshold, manual trigger, or capacity)
- **Where is the record?** (archived memory IDs, fold summary ID)
- **Who authorized it?** (AEGIS gate: Raven Allow or automated by rule)

The receipt is promoted to JATM so it survives all future folds.

### Tool: `jarvis_fold`
```text
jarvis_fold {
  older_than_days: 14,
  domain: "optional-scope",
  dry_run: true,
  approve: false
}
```
Dry run returns: count of memories to fold, grouped by topic, estimated compression ratio. Raven reviews, then calls with `approve: true`.

---

## Bounded Growth Rules

| Tier | Growth rule |
|------|-------------|
| JITM | Max 10 entries. Adding an 11th requires removing one. |
| JSTM | Purged at session close. Surviving entries promoted or discarded. |
| JLTM | Folded every 14 days (adjustable). Fold receipts go to JATM. |
| JATM | Grows slowly. Only irrecoverable knowledge promoted here. No compression. |

---

## Note on pre-receipt folds
All JLTM compression before this spec was ratified (including the June 23 fold producing 12 memories) was silent — no receipt was written. Those receipts are unrecoverable. The system acknowledges this as an unauditable baseline. Clean governed folding begins from ratification date: 2026-06-24.
