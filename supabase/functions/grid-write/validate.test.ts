// NEMESIS — tests for the grid-write whitelist (the GL5 write boundary). Pure;
// runs in CI via `node --experimental-strip-types`. If this gate regresses, the
// public anon key could regain arbitrary write — so it is pinned here.
import { validateWrite, WHITELIST } from "./validate.ts";

let passed = 0;
let failed = 0;
function ok(name: string, cond: boolean) {
  if (cond) { passed++; }
  else { failed++; console.error("FAIL -", name); }
}

// allowed writes
ok("sessions insert allowed", validateWrite({ table: "sessions", op: "insert", data: {} }).ok);
ok("sessions update allowed (with match)", validateWrite({ table: "sessions", op: "update", data: {}, match: { id: 1 } }).ok);
ok("consensus_proposals insert allowed", validateWrite({ table: "consensus_proposals", op: "insert", data: {} }).ok);
ok("push_subscriptions upsert allowed", validateWrite({ table: "push_subscriptions", op: "upsert", data: {} }).ok);
ok("push_subscriptions delete allowed (with match)", validateWrite({ table: "push_subscriptions", op: "delete", match: { endpoint: "x" } }).ok);

// table not whitelisted → rejected (the core GL5 guarantee)
ok("unknown table rejected", !validateWrite({ table: "users", op: "insert", data: {} }).ok);
ok("world_kernels NOT writable here", !validateWrite({ table: "world_kernels", op: "insert", data: {} }).ok);

// op not allowed on a whitelisted table
ok("events update rejected (insert-only)", !validateWrite({ table: "events", op: "update", data: {}, match: { id: 1 } }).ok);
ok("sessions delete rejected", !validateWrite({ table: "sessions", op: "delete", match: { id: 1 } }).ok);
ok("save_states update rejected (insert-only)", !validateWrite({ table: "save_states", op: "update", data: {}, match: { id: 1 } }).ok);

// shape requirements
ok("update without match rejected", !validateWrite({ table: "sessions", op: "update", data: {} }).ok);
ok("update with empty match rejected", !validateWrite({ table: "sessions", op: "update", data: {}, match: {} }).ok);
ok("delete without match rejected", !validateWrite({ table: "push_subscriptions", op: "delete" }).ok);
ok("insert without data object rejected", !validateWrite({ table: "sessions", op: "insert" }).ok);
ok("insert with non-object data rejected", !validateWrite({ table: "sessions", op: "insert", data: "x" }).ok);

// error messages are present
const r = validateWrite({ table: "nope", op: "insert", data: {} });
ok("rejection carries an error string", !r.ok && typeof r.error === "string" && r.error.length > 0);

// whitelist sanity — every table maps to a non-empty op set
ok("whitelist has 9 tables", Object.keys(WHITELIST).length === 9);
ok("no table has empty op set", Object.values(WHITELIST).every((s) => s.size > 0));

console.log(`${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
