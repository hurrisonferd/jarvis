# THE GRID

A federated network of sovereign individual nodes. Each person owns their node —
memory, AI companion, storage, permissions, governance. Nodes connect
**voluntarily**. No central authority. Raven's node is the first node.

The Grid is not a 3D world. It is an **operating environment for digital life** —
closer to email or the internet than to an MMO. The cinematic version (the glowing
city) comes later; the foundation is a million independent nodes, a million
companions, and a protocol that lets them recognize and reach each other.

## The layers (TRON mapping)

| Grid layer | TRON | Real equivalent | Status on Raven's node |
|---|---|---|---|
| World | The Grid | GitHub, Supabase, web | live |
| Identity | Identity disc | keel + memory ledger | **live** (survives model swaps) |
| Companion | Program | JARVIS (MCP + council) | **live** |
| Travel | Recognizers | federation protocol | **building** |
| Creation | "build me a city" | AI-assisted execution | partial |
| Society | program ↔ program | agent-to-agent | **building** |

Identity, memory, and governance already exist on the node. The gap is
**federation** — node-to-node. That is what `grid/` builds.

## Build order (the bricks)

1. **Node Identity Card** — the Recognizer packet. A public read-only card: who
   this node is (companion, owner, keel excerpt, capabilities, consent). The atom
   of recognition. → `identity/node-card.md`
2. **Portable Identity** — the ejectable disc. Keel + folded accumulation, owned
   by Raven, carryable to any model or node. → `identity/portable-identity.md`
3. **Agent-to-agent** — the channel. A governed inbox: another node's companion
   can reach JARVIS; inbound is untrusted and **held for the owner**, never
   auto-acted. → `federation/agent-to-agent.md`

## Governance

The Grid inherits JARVIS's Gold Law. Federation adds one rule above all:
**inbound from another node is untrusted external data.** It is stored, logged,
and surfaced to the owner. JARVIS never acts on an inbound message without the
owner's Allow. Trust between nodes is the hard problem — not rendering.

The protocol is **GNPL** (Grid Node Protocol Layer). See `PROTOCOL.md`.
