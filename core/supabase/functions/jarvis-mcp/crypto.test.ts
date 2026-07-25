// Grid signing tests. Run: node --experimental-strip-types crypto.test.ts
import { GNPL_SIG_VERSION, identityAssertion, isBase64, messagePayload } from "./crypto.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

// --- identity assertion: deterministic, fixed field order ---
const a1 = identityAssertion("raven-node-0", "Raven (John Barber)", "PUBKEYB64");
const a2 = identityAssertion("raven-node-0", "Raven (John Barber)", "PUBKEYB64");
check("identity assertion is deterministic", a1 === a2);
check("assertion carries the version tag", a1.startsWith(`GNPL-NODE-IDENTITY:${GNPL_SIG_VERSION}`));
check("assertion binds node_id, owner, pubkey in order", a1 === "GNPL-NODE-IDENTITY:v1\nnode_id=raven-node-0\nowner=Raven (John Barber)\npubkey=PUBKEYB64");
check("different pubkey -> different assertion", identityAssertion("raven-node-0", "Raven", "A") !== identityAssertion("raven-node-0", "Raven", "B"));

// --- message payload: deterministic, fixed field order ---
const m = { from_node: "ayre-node-1", to_node: "raven-node-0", intent: "hello", body: "hi" };
check("message payload is deterministic", messagePayload(m) === messagePayload({ ...m }));
check("message payload carries the version tag", messagePayload(m).startsWith(`GNPL-MSG:${GNPL_SIG_VERSION}`));
check("tampering the body changes the payload", messagePayload(m) !== messagePayload({ ...m, body: "hi " }));

// --- base64 guard ---
check("accepts valid base64", isBase64("aGVsbG8="));
check("accepts unpadded-but-aligned base64", isBase64("aGVsbG9h"));
check("rejects non-base64", !isBase64("not base64!!"));
check("rejects wrong-length base64", !isBase64("abc"));
check("rejects non-string", !isBase64(42 as unknown));

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
