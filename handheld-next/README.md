# JARVIS Pocket Universe — Modular Construction Dock

This directory is a safe successor workspace. It does not replace the production root handheld.

## Current slice

- independent handheld shell
- modular screen router
- governed event bus with fail-closed public mutation rule
- native OMNI Room screen
- sanitized observer snapshot contract
- preserved legacy provenance

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

`data/observer-snapshot.json` is deliberately public-safe fixture data. Private OMNI artifacts, channel content, approval digests, service credentials, and mutation authority must never be copied into GitHub Pages.
