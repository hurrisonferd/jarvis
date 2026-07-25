#!/usr/bin/env node
// THE GRID — sovereign signing tool (GNPL v0.2.0). Run this OFF-SYSTEM, on your
// own machine. It generates your node's Ed25519 keypair and signs the identity
// assertion. The PRIVATE KEY NEVER LEAVES YOUR MACHINE — you give the node only
// the public key + the signature (the identity certificate). The node verifies;
// it never signs. Only you can assert your node's identity. (GL2.)
//
// No dependencies — pure node:crypto. Node 18+.
//
//   node operations/scripts/grid_keygen.mjs keygen "raven-node-0" "Raven (John Barber)"
//   node operations/scripts/grid_keygen.mjs sign-msg <priv.pem> <from_node> <to_node> <intent> <body>
//   node operations/scripts/grid_keygen.mjs verify <pubkey_b64> <message> <sig_b64>

import { createPrivateKey, createPublicKey, generateKeyPairSync, sign, verify } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

const SIG_VERSION = "v1";

// MUST match core/supabase/functions/jarvis-mcp/crypto.ts byte-for-byte.
const identityAssertion = (nodeId, owner, pubkey) =>
  [`GNPL-NODE-IDENTITY:${SIG_VERSION}`, `node_id=${nodeId}`, `owner=${owner}`, `pubkey=${pubkey}`].join("\n");
const messagePayload = (from, to, intent, body) =>
  [`GNPL-MSG:${SIG_VERSION}`, `from_node=${from}`, `to_node=${to}`, `intent=${intent}`, `body=${body}`].join("\n");

// Raw 32-byte Ed25519 public key as standard base64 (what the node's Web Crypto
// importKey("raw", ...) expects). Node's JWK `x` is base64url; convert.
const rawPubB64 = (publicKey) => {
  const x = publicKey.export({ format: "jwk" }).x; // base64url
  return Buffer.from(x.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("base64");
};

const [cmd, ...args] = process.argv.slice(2);

if (cmd === "keygen") {
  const [nodeId = "raven-node-0", owner = "Raven (John Barber)"] = args;
  const { publicKey, privateKey } = generateKeyPairSync("ed25519");
  const pubB64 = rawPubB64(publicKey);
  const assertion = identityAssertion(nodeId, owner, pubB64);
  const cert = sign(null, Buffer.from(assertion, "utf8"), privateKey).toString("base64");
  const pem = privateKey.export({ type: "pkcs8", format: "pem" });

  const keyFile = `${nodeId}.private.pem`;
  writeFileSync(keyFile, pem, { mode: 0o600 });

  console.log("\n=== GRID NODE KEY GENERATED ===\n");
  console.log(`Private key written to: ${keyFile}`);
  console.log("  >>> KEEP THIS SECRET. NEVER share it, commit it, or paste it anywhere. <<<\n");
  console.log("Register the node's identity with these two values (jarvis_node_register_key):\n");
  console.log("public_key:");
  console.log(`  ${pubB64}\n`);
  console.log("identity_cert:");
  console.log(`  ${cert}\n`);
  console.log(`owner: ${owner}`);
  console.log(`node_id (must match the node's JARVIS_NODE_ID): ${nodeId}\n`);
  console.log("The node will rebuild this exact assertion and verify the cert before accepting:");
  console.log("---\n" + assertion + "\n---\n");
} else if (cmd === "sign-msg") {
  const [pemPath, from, to, intent = "message", body = ""] = args;
  const privateKey = createPrivateKey(readFileSync(pemPath));
  const payload = messagePayload(from, to, intent, body);
  const sig = sign(null, Buffer.from(payload, "utf8"), privateKey).toString("base64");
  console.log("sig:", sig);
} else if (cmd === "verify") {
  const [pubB64, message, sigB64] = args;
  const pub = createPublicKey({
    key: Buffer.concat([Buffer.from("302a300506032b6570032100", "hex"), Buffer.from(pubB64, "base64")]),
    format: "der", type: "spki",
  });
  const ok = verify(null, Buffer.from(message, "utf8"), pub, Buffer.from(sigB64, "base64"));
  console.log(ok ? "VALID" : "INVALID");
} else {
  console.log("usage: keygen <node_id> <owner> | sign-msg <priv.pem> <from> <to> <intent> <body> | verify <pub_b64> <message> <sig_b64>");
  process.exit(1);
}
