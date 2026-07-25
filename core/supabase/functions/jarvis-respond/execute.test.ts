// SKADI execution tests. Run: node --experimental-strip-types execute.test.ts
import { extractFact, planExecutions, execSummary } from "./execute.ts";
import { route } from "./router.ts";
import { gate, capabilitiesFor } from "./aegis.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

// --- extractFact strips imperatives ---
check("strips 'remember that'", extractFact("remember that the grid is federated") === "the grid is federated");
check("strips 'note:'", extractFact("note: court date is June 24") === "court date is June 24");
check("strips 'commit to memory'", extractFact("commit to memory the node is sovereign") === "the node is sovereign");
check("leaves bare fact intact-ish", extractFact("the sky is blue").length > 0);

// --- routing: 'remember that' -> remember (not recall) ---
check("'remember that X' -> remember intent", route("remember that P17 needs the secret").intent === "remember");
check("'do you remember X' -> recall intent", route("do you remember the grid plan").intent === "recall");
check("remember -> write capability", capabilitiesFor("remember")[0].action === "mnemos.write");

// --- gate: write held by default, runs when authorized (TTL-fresh grant) ---
const NOW = 1000;
const heldGate = gate(capabilitiesFor("remember"));
check("write held without auth", heldGate.cleared.length === 0 && heldGate.held.length === 1);
const fresh = { action: "mnemos.write", issued_at: NOW };
const okGate = gate(capabilitiesFor("remember"), { authorized: [fresh], _now: () => NOW });
check("write clears with fresh auth", okGate.cleared.length === 1);

// --- planExecutions: held vs done ---
const heldPlans = planExecutions("remember", heldGate, "remember that X");
check("unauthorized -> held plan", heldPlans[0].status === "held");

const donePlans = planExecutions("remember", okGate, "remember that the node is sovereign");
check("authorized -> done plan", donePlans[0].status === "done");
check("done plan carries payload text", donePlans[0].payload?.text === "the node is sovereign");
check("payload tagged directive", (donePlans[0].payload?.tags as string[]).includes("directive"));

// --- empty fact -> noop, never a bogus write ---
const noopPlans = planExecutions("remember", okGate, "remember that   ");
check("empty fact -> noop", noopPlans[0].status === "noop");

// --- summary renders ---
check("summary lists statuses", execSummary(donePlans).includes("mnemos.write:done"));

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
