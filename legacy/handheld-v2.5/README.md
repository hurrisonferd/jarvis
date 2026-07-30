# JARVIS Handheld v2.5 — Preserved Vessel

The production handheld is frozen by immutable source provenance:

- Canonical commit: `42928e59cbb22546e9e1ed4f0e00bee59f4bb563`
- Canonical root blob: `58e480f3c89f3d0955b6e667e55374eae2000a23`
- Live path at freeze: `/index.html`

Do not refactor the production root in place. The modular successor is built under `/handheld-next/` and must pass parity gates before any root promotion.

## Preservation law

1. Preserve identity and behavior before extraction.
2. Never expose privileged credentials in browser code.
3. Keep public observer state separate from private sovereign state.
4. Root promotion requires mobile, PWA, navigation, event, and data parity.
