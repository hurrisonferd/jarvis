# Pocket Universe Architecture — Instrument Cluster v0.2

```text
private Omni RV / God Vehicle
  -> public-safe instrument projector
  -> omni.instrument.v2 envelope
  -> public sanitizer gate
  -> handheld instrument loader
  -> freshness classifier
  -> OMNI Room VEHICLE layer

public observer state
  -> observer adapter
  -> SYSTEM / CREW layers

all browser events
  -> governed event bus
  -> AEGIS gate
```

## Laws

- Production root remains untouched during extraction.
- Browser runtime is public-observer by default.
- Private command state requires authenticated capability and a separate transport.
- Public runtime cannot request mutation.
- Vehicle instrument freshness is tracked separately from crew-observer freshness.
- A fresh vehicle instrument receipt does not make old crew observations current.
- Each screen owns rendering and control handling.
- Shared state enters through adapters rather than direct screen-level network calls.
- Events are envelopes with timestamp and identity.
- Public instrument visibility never grants private owner/effect authority.

## OMNI observer contract

Required fields:

- `schema_version`
- `generated_at`
- `receipt_hash`
- `compression`
- `interventions`
- `panels`

## Omni RV instrument contract

Schema: `omni.instrument.v2`

Required fields:

- `generated_at`
- `receipt_hash`
- `vehicle`
- `performance`
- `capacity`
- `proof`
- `safety`
- `access_domains`
- `public_safe`

Freshness states:

- `FRESH` <= 6 hours
- `AGING` <= 24 hours
- `STALE` > 24 hours
- `FUTURE` if timestamp is materially ahead of the client clock
- `UNKNOWN` if timestamp cannot be parsed

## Forbidden public material

- channel/message bodies
- approval digests
- service-role credentials
- private relationship metadata
- mutation RPC names or payloads
- secrets/passwords/tokens
- owner effect authority
- private repository paths in the instrument envelope

## Security-zone model

```text
PRIVATE ZONE
God Vehicle can resolve owner-native systems and prepare effect handoff.

PUBLIC ZONE
Pocket Universe may display sanitized gauges and receipts only.
Public mutation remains fail-closed.
```

## Extraction / promotion order

1. shell and controls
2. router and menu
3. BUS and AEGIS
4. read adapters
5. OMNI observer room
6. public Omni RV instrument cluster
7. legacy screen parity modules
8. PWA and service worker
9. emulator boundary
10. authenticated private command transport, separately gated
11. explicit Raven promotion approval
