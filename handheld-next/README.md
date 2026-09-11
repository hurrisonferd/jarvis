# JARVIS Pocket Universe — Instrument Cluster v0.2.0

This directory is a safe successor workspace. It does not replace the production root handheld or the private Omni RV command deck.

## Current slice

- independent handheld shell
- modular screen router
- governed event bus with fail-closed public mutation rule
- native OMNI Room with SYSTEM / CREW / VEHICLE layers
- sanitized observer snapshot contract
- sanitized Omni RV instrument contract (`omni.instrument.v2`)
- explicit FRESH / AGING / STALE / FUTURE instrument states
- public-safe vehicle versions, access coverage, capacity and proof state
- deterministic instrument-cluster canary
- preserved legacy provenance

The vehicle instrument feed is separate from crew observation data on purpose. A fresh vehicle receipt must not make old crew observations look current.

Open `/handheld-next/` through GitHub Pages after the branch is merged.

## Promotion gates

The root handheld remains canonical until all gates pass:

1. boot and navigation parity
2. mobile touch parity
3. installed-PWA parity
4. Supabase read parity
5. governed-write parity
6. emulator and save-state parity
7. event and God-System activation parity
8. private/public state separation
9. OMNI receipt and recovery integrity
10. explicit Raven promotion approval

## Data boundary

`data/observer-live.json` / `data/observer-snapshot.json` carry public-safe observer state. `data/instrument-live.json` carries a separately sanitized Omni RV instrument envelope. Neither surface may contain private command state, channel/message bodies, approval digests, service credentials, secrets, private relationship metadata, mutation RPC payloads, or owner effect authority.

The public vessel may **observe instrument state**. It may not become the private God Vehicle merely because it can display its gauges.
