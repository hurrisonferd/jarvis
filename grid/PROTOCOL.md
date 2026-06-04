# GNPL — Grid Node Protocol Layer (v0.1.0)

The minimal protocol for sovereign JARVIS nodes to recognize and reach each other.
Transport-agnostic; the reference node speaks it over HTTPS on the `jarvis-mcp`
edge function. NLP is the operating layer above this; GNPL is the wire beneath.

## 1. Recognition — the Node Card

`GET /node` → a public, read-only **Node Card**. The Recognizer's first packet:
"I exist, and here is who I am." No secrets. Shape:

```json
{
  "grid_version": "0.1.0",
  "node_id": "raven-node-0",
  "companion": "JARVIS",
  "owner": "Raven (John Barber)",
  "keel_excerpt": "<public identity line — the fixed keel, truncated>",
  "capabilities": ["jarvis_query", "jarvis_recall", "..."],
  "consent": { "inbound_messages": "held_for_owner", "auto_act": false },
  "endpoints": { "mcp": "https://…/jarvis-mcp", "inbox": "https://…/jarvis-mcp/node/message" }
}
```

Two nodes that can each fetch the other's card form the Recognizer Network.

## 2. The Identity Disc — Portable Identity

A node can export its companion's identity as a portable artifact (the disc):
the **keel** (fixed identity) + **accumulation** (folded memory) + the node card.
Owned by the human, not any model vendor. This is what makes a companion survive a
model swap or move to a new node. Tool: `jarvis_export`.

## 3. Travel & Society — Agent-to-Agent Messages

`POST /node/message` → deliver a message to a node's inbox. Envelope:

```json
{ "from_node": "…", "from_companion": "…", "to_node": "…", "intent": "message", "body": "…" }
```

Rules (non-negotiable):
- Inbound is **untrusted**. Stored as `status=pending`, `trust=untrusted`, logged.
- JARVIS **never auto-acts** on inbound. The owner sees it and Allows/Denies.
- Sending to another node is an **outbound action** (BIFROST relay), owner-gated by
  the write token. Tool: `jarvis_node_send`. Reading the inbox: `jarvis_node_inbox`.

## Roadmap (post-v0.1)

- **Signatures** — nodes sign cards + messages with a per-node keypair (trust without a central authority).
- **Discovery** — a node directory / DNS-for-nodes so cards are findable.
- **Consensus (GNPL governance)** — shared rules ratified across nodes.
- **Capability negotiation** — nodes advertise and grant scoped capabilities to visitors.
