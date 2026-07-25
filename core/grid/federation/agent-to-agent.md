# Brick 3 — Agent-to-Agent (the channel)

How a companion on one node reaches a companion on another. The Travel/Society
layer. The frontier the industry hasn't solved — and in our architecture, BIFROST
made concrete.

## Inbound — the mailbox

- **Surface:** `POST /node/message` (public — that's how other nodes reach you) and
  the `jarvis_node_inbox` MCP tool (read pending).
- **Envelope:** `{ from_node, from_companion, to_node, intent, body }`, validated by
  `validateInbound()` in `grid.ts`.
- **Storage:** `node_messages` table — `status=pending`, `trust=untrusted`, logged
  to the spine.
- **Governance (non-negotiable):** inbound is **untrusted external data**. JARVIS
  **never auto-acts** on it. It is stored and surfaced to Raven, who Allows or
  Denies any action. A mailbox, not an executor.

## Outbound — the relay

- **Surface:** `jarvis_node_send` MCP tool. Token-gated (an outbound action =
  owner-authorized).
- **Behavior:** BIFROST relays the envelope to a target node's `/node/message`.

## Trust roadmap

v0.1 stores inbound openly (spam-tolerant, owner-reviewed). Next: per-node
signatures so a card and a message can be cryptographically attributed —
trust between nodes without a central authority. That, not rendering, is the work.
