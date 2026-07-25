# Node Signatures — the sovereign-key model (GNPL v0.2.0)

Trust between nodes, without a central authority. Each node has an Ed25519
keypair. The **private key is held by the owner (Raven), off-system — it never
touches the node.** The node holds only the public key and **verifies**; it never
signs. Only the holder of the private key can assert the node's identity. (GL2:
JARVIS proposes; Raven signs.)

## What the node does

- Publishes its public key + identity certificate in the node card (`signed_identity`).
- Verifies inbound message signatures (`POST /node/message` with `sig` + `from_pubkey`)
  and stamps each message `signature_valid: true/false`. A valid signature proves
  **integrity + sender key** — it does **not** authorize action. Inbound stays
  `pending` + `untrusted`, held for Raven.
- Never signs anything. It cannot forge its own authority.

## The canonical payloads (signed byte-for-byte)

Defined in `core/supabase/functions/jarvis-mcp/crypto.ts` and mirrored in the keygen
tool. Field order is fixed; verifiers rebuild the exact string.

**Identity assertion** (bound by the certificate):
```
GNPL-NODE-IDENTITY:v1
node_id=<id>
owner=<owner>
pubkey=<raw 32-byte ed25519 public key, base64>
```

**Message payload**:
```
GNPL-MSG:v1
from_node=<id>
to_node=<id>
intent=<intent>
body=<body>
```

## Raven's procedure (off-system)

On your own machine — Node 18+, no dependencies:

```sh
# 1. Generate the keypair + sign the identity assertion.
node operations/scripts/grid_keygen.mjs keygen "raven-node-0" "Raven (John Barber)"
#    -> writes raven-node-0.private.pem (KEEP SECRET) and prints:
#         public_key   (base64)
#         identity_cert (base64)

# 2. Register the PUBLIC key with the node (paste the two values).
#    Via the connector: jarvis_node_register_key { public_key, identity_cert }
#    The node rebuilds the assertion, verifies the cert (Ed25519), and only then
#    stores it. Token-gated; approve the Allow prompt.

# 3. (optional) Sign an outbound message to another node:
node operations/scripts/grid_keygen.mjs sign-msg raven-node-0.private.pem \
     raven-node-0 <to_node> <intent> "<body>"
#    -> sig: ...   (send { ...envelope, from_pubkey, sig } to the target inbox)
```

The private key stays in `raven-node-0.private.pem` on your machine. Never commit
it, paste it, or send it anywhere. If it leaks, generate a new keypair and
re-register — the old identity is then revoked by replacement.

## Verified end-to-end (2026-06-03)

A cert/signature produced by `grid_keygen.mjs` verifies under the node's Web
Crypto Ed25519 path; a tampered message fails. The node's `verifyEd25519` matches
the offline signer byte-for-byte.

## Roadmap (next)

- **TOFU attribution** — confirm a message's `from_pubkey` matches the sender
  node's published card (currently the node verifies the signature but trusts the
  claimed key). 
- **Outbound signing** — a path for Raven to attach a signature to `jarvis_node_send`
  (the node still won't auto-sign).
- **Revocation / rotation** — a signed revocation record.
