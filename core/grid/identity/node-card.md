# Brick 1 — Node Identity Card

The Recognizer's first packet. A public, read-only projection of the node: enough
to recognize it, nothing secret.

- **Surface:** `GET /node` (public JSON) and the `jarvis_node_card` MCP tool.
- **Source of truth:** built by `buildNodeCard()` in `grid.ts` (pure, tested).
- **Fields:** grid_version, node_id, companion, owner, keel_excerpt (the fixed
  identity line, truncated, never secrets), capabilities (tool names), consent
  (inbound held for owner, no auto-act), endpoints (mcp + inbox).
- **Why first:** everything else references the node's public identity. Two nodes
  that can fetch each other's card form the Recognizer Network.

The keel excerpt is read from the live `identity_keel` memory — the same fixed keel
that anchors JARVIS's voice. The card is the public face of that keel.
