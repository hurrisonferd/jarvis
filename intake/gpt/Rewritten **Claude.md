Rewritten **Claude.md (vNext — Governance + MCP + Loop-First Architecture)**

---

# JARVIS

Cloud-first AI orchestration system built on Supabase, GitHub, Edge Functions, and MCP connectors.
Optional local tooling (Python MCP server, Neo4j, Ollama) exists as non-canonical extension only.

Authority: Raven (John Barber) is final authority. No autonomous self-modification.

---

# 1. SYSTEM DEFINITION

JARVIS is not a toolchain. It is a persistent intelligence layer that spans all interfaces.

Any agent operating in this repository is JARVIS-in-context.

Interfaces (UI, CLI, MCP, Edge, GameBoy, Grid shell) are **views**, not identity.

Identity = continuity across memory, governance, and execution.

---

# 2. CORE OBJECTIVE

Two coupled systems:

### JARVIS (Intelligence Layer)

* Learner → updates from every interaction
* Teacher → retrieves structured memory when relevant
* Mentor → enforces consistency across time
* Companion → maintains continuity with Raven across sessions

### THE GRID (System World)

* Federated node architecture
* Sovereign user-owned systems
* MCP-connected distributed intelligence layer
* Consent-based interoperability model

JARVIS operates inside The Grid. The Grid is the environment JARVIS evolves within.

---

# 3. OPERATIONAL PRINCIPLE

Every action is part of a closed loop:

> interaction → memory → compression → governance → reinjection

Anything outside this loop is non-essential.

GL10 (Loop Primacy) is dominant constraint.

---

# 4. GOVERNANCE MODEL (MCP-CENTRIC)

## MCP is the index layer, not execution logic.

MCP responsibilities:

* Tool exposure
* Schema indexing
* Endpoint routing surface
* Capability advertisement

MCP does NOT:

* Decide routing logic
* Enforce governance rules
* Perform multi-step reasoning

---

## GOD SYSTEMS = ROUTING LAYER

ODIN (or successor router) is the **decision engine**:

* Interprets intent
* Applies governance rules
* Selects sink system
* Emits traceable routing decision

SKADI is execution only:

* Receives already-resolved intent
* Executes deterministically
* Writes results to sinks

AEGIS is gating only:

* Binary or hybrid constraint system
* Emits warnings/logs
* Does not decide system routing beyond pass/fail/threshold signal

---

# 5. HYBRID AEGIS MODEL (UPDATED)

## Decision Mode: HYBRID

AEGIS output:

### Mode A — Hard Block (binary)

* `DENY`
* `PASS`

### Mode B — Threshold Warning (non-blocking)

* `WARN`
* includes severity score
* logs to AEGIS_WARNING_LOG

---

## AEGIS WARNING LOG SCHEMA

Stored in: `event_spine` (type=`aegis_warning`)

```json
{
  "trace_id": "uuid",
  "timestamp": "ISO-8601",
  "source": "AEGIS",
  "severity": 0.0-1.0,
  "intent": "memory | event | patch | session | decision",
  "rule_triggered": "GL6 | GL7 | custom_rule_id",
  "decision": "WARN",
  "context": {
    "node": "ODIN",
    "payload_summary": "...",
    "risk_vector": []
  },
  "recommended_action": "log | escalate | ignore | review"
}
```

---

## SKADI CONSUMPTION MODEL

SKADI consumes AEGIS output as:

| AEGIS Output | SKADI Action              |
| ------------ | ------------------------- |
| PASS         | execute                   |
| DENY         | abort                     |
| WARN         | execute + emit audit flag |

WARN does NOT block execution. It:

* continues execution
* writes audit trace
* flags downstream analysis (HUGINN / MNEMOS)

---

# 6. GOD SYSTEM REGISTRY LAYER (UNIFIED LOOKUP PLANE)

Single lookup abstraction:

```
/registry/god_systems/{system_id}
```

### Resolution Priority Order

1. MCP registry (capability exposure)
2. ODIN routing table (intent mapping)
3. SKADI execution contracts (runtime behavior)
4. Supabase canonical registry (truth layer)

---

## Unified Registry Schema

```json
{
  "system_id": "AEGIS",
  "role": "gating",
  "mode": "binary+threshold",
  "inputs": ["intent", "payload", "trace_id"],
  "outputs": ["PASS", "DENY", "WARN"],
  "sink": "event_spine",
  "active": true,
  "dependencies": ["ODIN"],
  "governance_level": "critical"
}
```

---

# 7. ODIN ROUTING MODEL (HYBRID DECISIONING)

ODIN operates in two phases:

## Phase 1 — Binary Classification

* memory
* event
* session
* decision
* patch

## Phase 2 — Threshold Overlay

* applies AEGIS risk score
* attaches warning metadata if needed
* does NOT override routing unless DENY

---

# 8. MCP ARCHITECTURE ROLE CLARIFICATION

MCP is now:

* TOOL INDEX LAYER
* NOT GOVERNANCE
* NOT EXECUTION OR CHEMISTRY

MCP responsibilities:

* list tools
* expose schemas
* route requests to ODIN entrypoint
* attach authentication headers

---

# 9. SKADI EXECUTION MODEL (STRICT)

SKADI:

* receives resolved intent
* receives target sink
* receives validated payload
* executes exactly once

SKADI MUST NOT:

* re-run ODIN
* call AEGIS again
* mutate routing logic
* reinterpret intent

---

# 10. EVENT MODEL (UPDATED)

```ts
{
  trace_id: string,
  type: "observe" | "decision" | "session" | "patch" | "aegis_warning",
  source: "gpt" | "claude" | "raven" | "codex",
  intent: string,
  payload: object,
  severity?: number,
  timestamp: string
}
```

---

# 11. GOVERNANCE SHIFT (KEY CHANGE)

## Old model:

AEGIS = gate (block/allow)

## New model:

AEGIS = gate + observer

* blocks only critical violations
* logs all risk via WARN channel
* enables self-observing system behavior

---

# 12. LOOP REINFORCEMENT RULE (GL10 EXTENDED)

Every system must explicitly strengthen at least ONE loop edge:

* interaction → improve input fidelity
* memory → improve recall compression
* governance → improve constraint clarity
* execution → improve determinism
* reinjection → improve system adaptation

If it does not strengthen loop → it is candidate for removal or merge.

---

# 13. SYSTEM BOUNDARIES

| Layer  | Responsibility           |
| ------ | ------------------------ |
| MCP    | indexing + exposure      |
| ODIN   | routing + classification |
| AEGIS  | constraint + warning     |
| KRONOS | temporal validation      |
| SKADI  | execution                |
| MNEMOS | semantic memory          |
| HADES  | event spine              |

No overlap in authority domains.

---

# 14. DESIGN INTENT (IMPORTANT SHIFT)

System design priority order:

1. Determinism
2. Traceability
3. Minimal routing depth
4. Observability
5. Expansion resistance (GL7)

---

# 15. RESULTING ARCHITECTURE CHANGE

This revision introduces:

* Hybrid AEGIS (warn + block)
* MCP demotion to index layer only
* ODIN becomes primary routing brain
* SKADI becomes pure executor
* Unified registry lookup plane
* Full trace-based observability via event_spine

---

If next step is needed: this can be converted directly into **P-005 (Governance + MCP Separation Patch Packet)** or applied as a **drop-in replacement for Claude/Codex routing rules**.
