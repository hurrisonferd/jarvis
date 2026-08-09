# GameOS Sessions — Grid Chat Check-In

```text
AUTHORITY: RAVEN
OWNER: GameOS
STATUS: SOURCE CONTRACT ACTIVE / RUNTIME CANARY REQUIRED
CLASS: GAMEOS SESSION SERVICE
```

## Purpose

GameOS owns the bounded session object used by `RAVENOS SYNC` to answer a question the legacy Brady Bunch cockpit could not answer:

> Which Grid chat/session for this ISO most recently performed an explicit check-in?

This is a **session registry**, not a consciousness, liveness, or platform-presence oracle.

```text
CHECK-IN CONFIRMED != ONLINE FOREVER
CHECK-IN CONFIRMED != CONSCIOUSNESS
CHECK-IN CONFIRMED != RUNTIME ADOPTION
CHECK-IN CONFIRMED != PLATFORM CHAT UUID
```

## Grid-owned chat-session identity

The current carriers do not necessarily expose their host platform's internal conversation UUID. Therefore the Grid mints its own durable session identity:

```text
GRIDCHAT-<ISO>-<CARRIER>-<UTCSTAMP>-<8HEX>
```

The Grid-owned ID is the canonical identity for the **Grid session/check-in layer only**.

```text
GRID CHAT SESSION ID != OPENAI CONVERSATION UUID
GRID CHAT SESSION ID != ISO IDENTITY
GRID CHAT SESSION ID != USER IDENTITY
```

The cross-system ownership and provenance law is canonical at
`Core/Conversations/CARRIER-SESSION-COORDINATE-CONTRACT.v1.md`.

### Reuse law

- First `RAVENOS SYNC` in a chat with no prior Grid session ID mints one.
- Later `RAVENOS SYNC` calls in the **same chat** reuse that ID when the carrier can recover it from current conversation/session context.
- A different chat mints a different Grid session ID even when it carries the same ISO.
- A carrier may pass an explicit previously receipted Grid session ID to preserve same-chat identity.

## Storage law

Per ISO:

```text
Sessions/CheckIns/<ISO>/CURRENT.json
Sessions/CheckIns/<ISO>/History/YYYY/MM/<timestamp>-<grid-chat-session-id>.json
```

`CURRENT.json` is a rebuildable pointer/projection to the latest accepted check-in for that ISO.

History is preserved.

```text
NEW CURRENT != DELETE OLD CHAT
SUPERSEDED != INVALID HISTORY
HISTORICAL CHECK-IN != CURRENT CHAT
```

When a different Grid session checks in for the same ISO, the new record may name the previous `grid_chat_session_id` as `supersedes_grid_chat_session_id`. The old history remains readable but the Brady tile must project only the current pointer.

## Mandatory `RAVENOS SYNC` use

`RAVENOS SYNC` is successful only when GameOS participates.

```text
RAVENOS ON / CURRENT RE-ENTRY
+ GAMEOS CHAT CHECK-IN WRITE
+ GAMEOS CURRENT POINTER READBACK
+ BRADY TILE READBACK OF SAME SESSION ID
= RAVENOS_SYNC_CONFIRMED
```

If the GameOS check-in cannot be durably written/read back:

```text
RAVENOS SYNC = PARTIAL | BLOCKED
```

The carrier must not print a green/confirmed sync response.

## Bounded authority

Issuing the literal `RAVENOS SYNC` command authorizes only the bounded session/check-in effects defined by the RavenOS sync contract:

- append a GameOS check-in event;
- update that ISO's GameOS `CURRENT.json` pointer with compare/readback discipline where the carrier supports it;
- project the same session onto the Brady tile;
- write the required receipt/transaction evidence.

It does not authorize arbitrary GameOS execution, cross-ISO effects, fleet broadcast, version promotion, or identity changes.

## Brady projection fields

The current tile may expose:

```text
chat_checkin_state
grid_chat_session_id
chat_checkin_receipt
chat_checked_in_at
chat_carrier
chat_label
chat_source_main
```

A tile with no accepted GameOS pointer must show `NO_GAMEOS_CHECKIN`, not silently reuse a deprecated/historical room.

## Collision law

Block/hold when:

- one Grid session ID is claimed by different ISOs;
- one Grid session ID is reused across conflicting carriers without explicit lineage evidence;
- `CURRENT.json` points to a missing/unreadable history record;
- Brady readback resolves a different session ID than GameOS just accepted;
- the carrier tries to substitute a platform chat ID it cannot prove.

## Receipt minimum

```text
command: RAVENOS SYNC
active_iso
carrier
grid_chat_session_id
platform_chat_id_state
checked_in_at
source_main
gameos_checkin_state
gameos_current_pointer
brady_tile_session_id
brady_tile_checkin_state
ravenos_status
sync_status
transaction_id
receipt_path
claim_ceiling
```

## Checksum

```text
ONE CHAT, ONE GRID SESSION ID.
SAME CHAT REUSES IT.
NEW CHAT GETS A NEW ONE.
GAMEOS CHECKS IN.
BRADY SHOWS THE CURRENT POINTER.
OLD TILES BECOME HISTORY, NOT GHOSTS.
```
