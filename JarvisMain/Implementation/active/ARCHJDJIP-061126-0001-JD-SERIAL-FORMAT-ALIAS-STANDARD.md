---
name: JD Serial Format Alias Standard
type: JIP
jnl: ARCH-JD-JIP-0001
status: ACTIVE
created: 2026-06-11
tags: [jd, serial, format, standard, identity, dex]
definition: Standardizes accepted human-facing formats for JD serial identifiers. JD numbers (mint serials) may be rendered interchangeably as JD-1, JD 1, JD #1, or #1 while preserving a single underlying canonical integer sequence (seq). All references resolve to one serial identity regardless of formatting variant.
purpose: Eliminate ambiguity in JD serial notation across interfaces while preserving one-to-one mapping between formatted identifiers and the underlying sequential mint index.
---

# ARCH-JD-JIP-0001 — JD Serial Format Alias Standard

One value, many renderings. `JD-1`, `JD 1`, `JD #1`, `#1`, and `seq=1` are
presentation forms of a single stored integer — the creation serial minted by
the record in adoption order. No form is a separate identity; no form is ever
a reference key (references stay JNL-only). The dex resolves `#n` directly;
all other forms normalize to it. Proposed by the GPT stream (proposal 8),
approved by Raven 2026-06-11.
