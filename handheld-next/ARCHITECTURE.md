# Pocket Universe Architecture

```text
handheld shell
  -> screen router
  -> governed event bus
  -> AEGIS gate
  -> screen modules
  -> public-safe adapters
  -> observer state
```

## Laws

- Production root remains untouched during extraction.
- Browser runtime is public-observer by default.
- Private command state requires authenticated capability and a separate transport.
- Public runtime cannot request mutation.
- Each screen owns rendering and control handling.
- Shared state enters through adapters rather than direct screen-level network calls.
- Events are envelopes with timestamp and identity.

## OMNI observer contract

Required fields:

- `schema_version`
- `generated_at`
- `receipt_hash`
- `compression`
- `interventions`
- `panels`

Forbidden fields:

- channel message bodies
- approval digests
- service-role credentials
- private relationship metadata
- mutation RPC names or payloads

## Extraction order

1. shell and controls
2. router and menu
3. BUS and AEGIS
4. read adapters
5. OMNI observer room
6. legacy screen parity modules
7. PWA and service worker
8. emulator boundary
9. private authenticated command deck
10. root promotion
