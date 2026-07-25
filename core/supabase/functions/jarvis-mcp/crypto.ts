// THE GRID — signing primitives (GNPL v0.2.0). The DETERMINISTIC canonical
// payloads that the off-system signer (Raven, who holds the private key) and the
// node's verifier must agree on byte-for-byte. Pure + testable. Sovereign-key
// model: the node holds only the PUBLIC key and VERIFIES; it never signs. Only
// the holder of the private key (Raven) can assert the node's identity. (GL2.)

export const GNPL_SIG_VERSION = "v1";

// The node's identity assertion — the exact bytes Raven signs to bind a public
// key to this node. The resulting signature is the node's identity certificate:
// "the holder of this key attests this pubkey owns this node_id." Self-certifying
// (trust-on-first-use, like an SSH host key). Field order is FIXED — verifiers
// rebuild this string and must get identical bytes.
export function identityAssertion(nodeId: string, owner: string, pubkey: string): string {
  return [
    `GNPL-NODE-IDENTITY:${GNPL_SIG_VERSION}`,
    `node_id=${nodeId}`,
    `owner=${owner}`,
    `pubkey=${pubkey}`,
  ].join("\n");
}

// The message payload — the exact bytes signed for an agent-to-agent message.
// A receiver rebuilds this from the delivered envelope and verifies against the
// sender's published pubkey. Field order is FIXED.
export function messagePayload(m: { from_node: string; to_node: string; intent: string; body: string }): string {
  return [
    `GNPL-MSG:${GNPL_SIG_VERSION}`,
    `from_node=${m.from_node}`,
    `to_node=${m.to_node}`,
    `intent=${m.intent}`,
    `body=${m.body}`,
  ].join("\n");
}

// Standard base64 sanity check (keys + signatures travel as base64). Bounds the
// verifier's input before it touches Web Crypto.
export function isBase64(s: unknown): boolean {
  return typeof s === "string" && s.length > 0 && s.length % 4 === 0 && /^[A-Za-z0-9+/]+={0,2}$/.test(s);
}
