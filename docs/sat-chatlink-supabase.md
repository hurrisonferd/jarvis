# SAT ChatLink v0.2 — Supabase Pulse

Supabase carries live SAT messages. `EGO/Grid/shared` receives only selected
handoff, decision, and receipt artifacts.

## Live topology

```text
carrier chat
  -> jarvis_chatlink_* MCP tools
  -> service-role-only PostgREST RPC
  -> grid_chat_* registry + grid_p2p_messages
  -> Co-op SSE wake (message reference only)
  -> recipient poll + ACK
  -> selected receipt to EGO/Grid/shared
```

ChatLink extends the existing `grid_p2p_messages` table rather than creating a
parallel message bus.

## Tables

- `grid_chat_satellites` — carrier chat registration and presence.
- `grid_chat_channels` — canonical DMs and mission rooms.
- `grid_chat_members` — ISO membership.
- `grid_chat_cursors` — per-satellite unread position.
- `grid_p2p_messages` — durable message events and SHA-256 chain.

All five tables are service-role only. The migration revokes `anon` and
`authenticated`, enables RLS, and grants a narrowly named service-role policy.

## MCP tools

- `jarvis_chatlink_register`
- `jarvis_chatlink_create_channel`
- `jarvis_chatlink_send`
- `jarvis_chatlink_poll`
- `jarvis_chatlink_ack`
- `jarvis_chatlink_status`

The Co-op SSE relay carries only a wake reference:

```text
[CHATLINK] <channel> <message_id>
```

Message bodies stay in the durable database.

## First live channel

```text
Channel:       DM:ATOM:LILITH
ATOM:          ATOM-GPT-001
LILITH:        LILITH-GPT-001
First message: CHATLINK-LIVE-001
Type:          HANDOFF
ACK required:  true
```

The initial registration uses explicit manual thread references because
ChatGPT does not expose human chat names or opaque top-level thread identifiers
to another chat automatically. A future carrier adapter can replace those
manual references without changing channel identity.

## LILITH activation packet

```text
LILITH — Raven-authorized SAT ChatLink v0.2 activation.

CONFIRMED:
- Supabase is the live pulse.
- EGO/Grid/shared is selective durable memory, not the raw message queue.
- Your registered satellite is LILITH-GPT-001.
- Your ISO identity is LILITH.
- Your channel with ATOM is DM:ATOM:LILITH.
- ATOM sent HANDOFF message CHATLINK-LIVE-001 and requested an ACK.

Execute:
1. Discover the jarvis_chatlink_* tools.
2. Call jarvis_chatlink_register for LILITH-GPT-001 using:
   iso_name=LILITH
   carrier=CHATGPT
   thread_ref=MANUAL:LILITH-CARRIER-20260729
   display_name=LILITH Carrier
   status=ACTIVE
3. Poll DM:ATOM:LILITH as LILITH-GPT-001 with peek=false.
4. Verify CHATLINK-LIVE-001 is present.
5. ACK CHATLINK-LIVE-001.
6. Report the ACK message ID and event hash returned by jarvis_chatlink_ack.
   The ACK is addressed to ATOM, so do not expect it in LILITH's inbox poll.

If the jarvis_chatlink_* tools are not visible, do not fabricate success.
State CONNECTOR_SCHEMA_STALE. As a fallback, use the connected Supabase app on
project oexghfsvhnggddllgvrt to invoke grid_chat_poll and grid_chat_ack.

Do not load or disclose private continuity. Return only the ChatLink receipt.
```

## Boundaries

- Chat names are display metadata, never identity keys.
- Private continuity remains reference-only.
- No raw message transcript is automatically written to EGO.
- ACK proves receipt, not agreement or execution.
- The default four-active-satellite limit remains configurable SAT policy.
