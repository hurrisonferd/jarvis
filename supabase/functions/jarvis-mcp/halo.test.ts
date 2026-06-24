// HALO throughput tests. Run: node --experimental-strip-types halo.test.ts
import { haloThroughputCheck, THROUGHPUT_RULE } from "./halo.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

const base = { windowMinutes: 30, inputs: 6, outputs: 6, councilTraces: 6, keelPresent: true, guardVerdict: "PASS" };

// calm / healthy
const calm = haloThroughputCheck({ ...base, inputs: 3, outputs: 3, councilTraces: 3 });
check("calm healthy turn PASSes", calm.verdict === "PASS" && calm.integrity === "intact");
check("idle window reports idle posture", haloThroughputCheck({ ...base, inputs: 0, outputs: 0, councilTraces: 0 }).posture === "idle");

// high velocity, presentation thinning, memory intact -> NOTE (safe routing of pressure)
const hot = haloThroughputCheck({ windowMinutes: 10, inputs: 40, outputs: 5, councilTraces: 40, keelPresent: true, guardVerdict: "PASS" });
check("high velocity detected", hot.posture === "high");
check("presentation thinning recognized", hot.presentation === "thinning");
check("thinning presentation + intact memory is a NOTE, not a FLAG", hot.verdict === "NOTE" && hot.integrity === "intact");

// keel missing -> integrity FLAG regardless of velocity
const noKeel = haloThroughputCheck({ ...base, keelPresent: false });
check("missing keel FLAGs integrity", noKeel.verdict === "FLAG" && noKeel.integrity === "at_risk");
check("missing keel names MERIDIAN", noKeel.flags.some((f) => f.includes("MERIDIAN")));

// guard FLAG -> integrity FLAG
check("guard FLAG raises integrity FLAG", haloThroughputCheck({ ...base, guardVerdict: "FLAG" }).verdict === "FLAG");

// route step thinning (council traces collapse under volume) -> FLAG (the call that must not thin)
const routeThin = haloThroughputCheck({ windowMinutes: 10, inputs: 20, outputs: 2, councilTraces: 3, keelPresent: true, guardVerdict: "PASS" });
check("collapsing council traces under volume FLAGs the route step", routeThin.verdict === "FLAG" && routeThin.flags.some((f) => f.includes("route")));

// the rule is carried for the auditor
check("posture carries the throughput rule", calm.rule === THROUGHPUT_RULE && hot.rule.includes("never the memory"));

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
