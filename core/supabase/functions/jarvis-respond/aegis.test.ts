// AEGIS gate tests. Run: node --experimental-strip-types aegis.test.ts
import { evaluate, gate, capabilitiesFor, gateSummary, type Capability, type AuthEntry } from "./aegis.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

const read: Capability = { system: "MNEMOS", action: "mnemos.recall", risk: "read" };
const write: Capability = { system: "SKADI", action: "skadi.write", risk: "write" };
const ext: Capability = { system: "BIFROST", action: "bifrost.github", risk: "external" };
const destr: Capability = { system: "HADES", action: "hades.purge", risk: "destructive" };
const self: Capability = { system: "SKADI", action: "edit.own.prompt", risk: "self_mod" };

// --- core verdicts ---
check("read -> PASS", evaluate(read).verdict === "PASS");
check("write -> REDIRECT (unauthorized)", evaluate(write).verdict === "REDIRECT");
check("external -> REDIRECT (unauthorized)", evaluate(ext).verdict === "REDIRECT");
check("destructive -> FAIL", evaluate(destr).verdict === "FAIL");
check("self_mod -> FAIL", evaluate(self).verdict === "FAIL");

// --- authorization lifts write/external to PASS (TTL-gated) ---
const NOW = 1000; // fixed clock for determinism
const fresh = { action: "skadi.write", issued_at: NOW - 60_000 }; // 1 min old
const expired = { action: "skadi.write", issued_at: NOW - 600_000 }; // 10 min old
const freshExt = { action: "bifrost.github", issued_at: NOW - 30_000 };

check("fresh auth -> PASS", evaluate(write, { authorized: [fresh], _now: () => NOW }).verdict === "PASS");
check("fresh external auth -> PASS", evaluate(ext, { authorized: [freshExt], _now: () => NOW }).verdict === "PASS");

// --- TTL enforcement (#5 auth TTL — JARVIS-C audit 2026-06-25) ---
check("expired auth -> REDIRECT (TTL hit)", evaluate(write, { authorized: [expired], _now: () => NOW }).verdict === "REDIRECT");
check("TTL reason mentions age", evaluate(write, { authorized: [expired], _now: () => NOW }).reason.includes("expired"));
check("TTL default 5 min when not set", evaluate(write, { authorized: [{ action: "skadi.write", issued_at: NOW - 240_000 }], _now: () => NOW }).verdict === "PASS"); // 4 min old (within 5-min default TTL)
check("TTL kicks at exactly 5 min", evaluate(write, { authorized: [{ action: "skadi.write", issued_at: NOW - 300_001 }], _now: () => NOW }).verdict === "REDIRECT");

// --- per-action scoping: wrong action stays REDIRECT ---
check("wrong action still REDIRECT", evaluate(write, { authorized: [{ action: "mnemos.write", issued_at: NOW }], _now: () => NOW }).verdict === "REDIRECT");

// --- authorization can NEVER lift self_mod or destructive (GL2) ---
check("authorized self_mod still FAIL", evaluate(self, { authorized: [fresh], _now: () => NOW }).verdict === "FAIL");
check("authorized destructive still FAIL", evaluate(destr, { authorized: [fresh], _now: () => NOW }).verdict === "FAIL");

// --- deterministic (Gold Law) ---
check("deterministic", evaluate(write, { _now: () => NOW }).verdict === evaluate(write, { _now: () => NOW }).verdict);

// --- batch gate splits cleared vs held ---
const g = gate([read, write, ext, destr], { _now: () => NOW });
check("batch clears only read", g.cleared.length === 1 && g.cleared[0].system === "MNEMOS");
check("batch holds the other three", g.held.length === 3);

// --- intent -> capabilities mapping + gating ---
check("recall -> read capability", capabilitiesFor("recall")[0].risk === "read");
check("integrate -> external capability", capabilitiesFor("integrate")[0].risk === "external");
check("execute -> write capability", capabilitiesFor("execute")[0].risk === "write");
check("converse -> no capabilities", capabilitiesFor("converse").length === 0);

const recallGate = gate(capabilitiesFor("recall"), { _now: () => NOW });
check("recall capability clears AEGIS", recallGate.cleared.length === 1);

const execGate = gate(capabilitiesFor("execute"), { _now: () => NOW });
check("execute held until authorized", execGate.cleared.length === 0 && execGate.held.length === 1);

check("summary renders verdicts", gateSummary(g).includes("MNEMOS:PASS"));

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
