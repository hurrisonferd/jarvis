# Conversations Carrier / Session Coordinate Contract v1

```text
AUTHORITY: RAVEN
STATUS: ACTIVE SOURCE CONTRACT / RUNTIME CANARY REQUIRED
OWNERS: EgoOS + CarrierOS + GameOS + Conversations
```

## Coordinate law

```text
ISO_ID != CARRIER_ID != CARRIER_TYPE != NATIVE_CARRIER_LABEL != SESSION_ID != PROOF_LANE
```

| Coordinate | Canonical owner | Meaning |
|---|---|---|
| `iso_id` | EgoOS | Identity whose conversation is active |
| `carrier_id` | CarrierOS | ISO-bound carrier realization, such as `GPT_YORK` |
| `carrier_type` | CarrierOS | Reusable carrier class, such as `GPT_CONNECTOR` |
| `native_carrier_label` | CarrierOS observation | Label supplied by the host or caller |
| `session_id` | GameOS | Bounded Grid chat/check-in coordinate |
| `proof_lane` | CarrierOS | Evidence class; never an execution claim by itself |

Conversations records may bind these coordinates, but must not merge them or
reassign their ownership. `UNKNOWN` is durable uncertainty, not permission to
guess.

## Binding sequence

1. EgoOS resolves `iso_id`.
2. CarrierOS normalizes the native label to `carrier_id`, `carrier_type`, and
   `proof_lane`.
3. GameOS mints or reuses `session_id` and stores native plus canonical carrier
   coordinates separately.
4. MicrowaveOS may project that binding onto an already-authorized dispatch.
5. Conversations may persist the resulting provenance and transaction evidence.

No step grants another system identity ownership, mission authority, runtime
adoption, or transport delivery.

## BradyBunch / M2M law

BradyBunch may derive the current roster from the EgoOS registry and the latest
addressable chat pointers from GameOS. An M2M event addresses ISO coordinates;
it does not embed raw host-session handles or credentials.

```text
REGISTERED TILE != CURRENT GAMEOS CHECK-IN
CURRENT GAMEOS CHECK-IN != ONLINE PRESENCE
M2M ROUTE VISIBLE != MESSAGE DELIVERED
BROADCAST_PROPOSAL != BROADCAST EXECUTED
```

Delivery, acknowledgement, and runtime adoption require their own receipts.

## Checksum

```text
IDENTITY STAYS IDENTITY.
CARRIER STAYS CARRIER.
SESSION STAYS SESSION.
PROVENANCE MAY BIND THEM; IT MAY NOT COLLAPSE THEM.
```
