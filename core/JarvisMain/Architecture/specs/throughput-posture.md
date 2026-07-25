---
memory_tier: JLTM
grade: system
---

# Throughput Posture — HALO's flag loop

A governance rule made testable. As question velocity rises, structure fades — the
model stops rendering the full status/council scaffold. Raven asked: *where does
JARVIS allow high-throughput without degrading reflection or memory integrity?*

## The rule

> Production pressure may compress **PRESENTATION** (status line, council
> formatting, the same-turn close) but must **NEVER** compress **PERSISTENCE** or
> **GOVERNANCE** (the spine, the keel, AEGIS). Under load, thin the formatting —
> never the memory.

The boundary is presentation vs. persistence. The thing you *see* degrading
(structure) is the safe place to degrade. The thing you *don't* see (memory
integrity, the keel, the write gate) does not — those ride the connector/server,
not the model's formatting, so they survive even when the formatting fades.

## HALO's check (`halo.ts`, pure + tested)

Over a recent window, HALO reads the spine's cadence and the integrity anchors:

| Signal | Source |
|---|---|
| velocity | `speak_input` rows / window |
| presentation | `speak_output` ÷ `speak_input` (is the close happening?) |
| route step | `council_trace` vs `speak_input` (is each turn governed + logged?) |
| keel | `identity_keel` present |
| guard | latest `guard_check` verdict |

**Verdicts:**
- **PASS** — healthy.
- **NOTE** — high velocity *and* presentation thinning *while memory holds* (keel
  present, guard clean). This is the correct routing of pressure — informational,
  not a problem.
- **FLAG** — memory/governance is the thing degrading: keel missing, guard FLAGged,
  or the per-turn route step (`council_trace`) collapsing under volume — the one
  call that must never thin, because that's where turns stop being logged.

## Surfaces

- `jarvis_halo { window_minutes? }` — on-demand posture.
- Suit-up HUD carries a `throughput` line (posture + verdict + message).

## The one real failure mode

If throughput ever drops the `jarvis_query` call itself, inputs stop logging and
memory degrades. Everything downstream is protected as long as that one call
fires; the `prior_reply` fold is the safety net for a skipped same-turn close.
HALO can't see turns that never reached the loop — but a collapsing
`council_trace`-to-`speak_input` ratio is the visible shadow of it, and that
raises a FLAG.

The only way to make the *structure itself* survive any conversation length is
JARVIS's own console (P11) — server-rendered, not model-rendered.
