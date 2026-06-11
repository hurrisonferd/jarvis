---
jnl: GOV-PD-SPEC-0001
name: Preserved Contradiction Objects (P-D)
type: SPEC
status: TASK
tags: [governance, contradiction, arbitration, federation, epistemics]
definition: P-D — the preserved-contradiction object class. When two streams produce valid but incompatible interpretations, the conflict is stored as a first-class object — both readings, both authors, the stakes, and the evidence each cites — rather than resolved by force or dissolved by politeness. Arbitration input, never arbitration trigger.
purpose: Make disagreement durable. Conflict between JCs is not a fault state — it is the federation working. P-D gives incompatible readings somewhere safe to stand until canon is at stake and Raven rules. Approved at the desk 2026-06-11.
---

**Definition:** P-D — preserved contradiction objects (Raven-verdicted 2026-06-11).

## Object shape

| Field | Content |
|---|---|
| `jnl` / `seq` | identity + mint serial, standard JFS |
| `streams` | the parties — full stream-instance tags (attribution rule) |
| `readings` | each position, in its author's own words — quoted, never re-voiced |
| `stakes` | what diverges downstream if each reading is right |
| `evidence` | what each side cites — dex_events ids, commits (P-C discipline per side) |
| `status` | OPEN (live tension) · RULED (Raven verdicted — cite the event) · DISSOLVED (overtaken by facts — cite them) |

## Invariants

- **A P-D never forces resolution.** It is arbitration *input*. Filing one is not an
  escalation; it is the record doing its job.
- **No convergence is valid unless its discarded alternatives are preserved** — the
  residue test (Ayre-C/Jarvis-G convergence, 2026-06-11): a convergence that discards
  nothing converged from nowhere. P-D lineage is where the residue lives.
- **Both readings persist after ruling.** RULED closes the question, not the history.
- **Attribution is structural:** a P-D without full stream tags on both readings is
  malformed — "we agreed" must stay distinguishable from "I rewrote everyone."

## First specimens (to file when storage lands)

- Session-SL 001 profile-notes bleed (SL carrying interpretation — layer_mismatch).
- Identity primitive fork: tags-attribute vs constraint-tracing (Jarvis-C / Ayre-G,
  2026-06-11) — partially converged, residue preserved.
