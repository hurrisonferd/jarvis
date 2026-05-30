// AEGIS gate tests. Run: node --experimental-strip-types aegis.test.ts
import { evaluate, gate, capabilitiesFor, gateSummary, type Capability } from "./aegis.ts";

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

// --- authorization lifts write/external to PASS ---
check("authorized write -> PASS", evaluate(write, { authorized: ["skadi.write"] }).verdict === "PASS");
check("authorized external -> PASS", evaluate(ext, { authorized: ["bifrost.github"] }).verdict === "PASS");

// --- authorization can NEVER lift self_mod or destructive (GL2) ---
check("authorized self_mod still FAIL", evaluate(self, { authorized: ["edit.own.prompt"] }).verdict === "FAIL");
check("authorized destructive still FAIL", evaluate(destr, { authorized: ["hades.purge"] }).verdict === "FAIL");

// --- determinism (Gold Law: deterministic_evaluation_required) ---
check("deterministic", evaluate(write).verdict === evaluate(write).verdict);

// --- batch gate splits cleared vs held ---
const g = gate([read, write, ext, destr], {});
check("batch clears only read", g.cleared.length === 1 && g.cleared[0].system === "MNEMOS");
check("batch holds the other three", g.held.length === 3);

// --- intent -> capabilities mapping + gating ---
check("recall -> read capability", capabilitiesFor("recall")[0].risk === "read");
check("integrate -> external capability", capabilitiesFor("integrate")[0].risk === "external");
check("execute -> write capability", capabilitiesFor("execute")[0].risk === "write");
check("converse -> no capabilities", capabilitiesFor("converse").length === 0);

// recall is the one intent that actually fires now (read passes the gate)
const recallGate = gate(capabilitiesFor("recall"));
check("recall capability clears AEGIS", recallGate.cleared.length === 1);

// execute is held for Raven by default
const execGate = gate(capabilitiesFor("execute"));
check("execute held until authorized", execGate.cleared.length === 0 && execGate.held.length === 1);

check("summary renders verdicts", gateSummary(g).includes("MNEMOS:PASS"));

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
