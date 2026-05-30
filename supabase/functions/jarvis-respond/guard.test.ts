// Sanity tests for guard.ts. Run: node --experimental-strip-types guard.test.ts
import { pickModel, loopGuard, jaccard, type Turn } from "./guard.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

// --- pickModel: tiered routing ---
check("greeting -> quick/sonnet", pickModel("hey jarvis").tier === "quick");
check("one-word ack -> quick", pickModel("yes").tier === "quick");
check("a question -> deep/opus", pickModel("how do we improve this?").tier === "deep");
check("substantive ask -> deep", pickModel("walk me through the grid consensus layer").tier === "deep");
check("deep uses the deep model", pickModel("explain GL7 in depth please").model === "gemini-2.0-flash");
check("deep cap raised past 400", pickModel("explain GL7 in depth please").maxTokens === 1024);
check("empty input -> deep (safe default)", pickModel("").tier === "deep");

// --- loopGuard: circuit breaker ---
const noLoop: Turn[] = [
  { from: "raven", text: "what's the plan for the grid" },
  { from: "jarvis", text: "ship the write proxy first, then node promotion" },
];
check("healthy thread -> no trip", loopGuard(noLoop, "and after that?") === null);

const jarvisRepeats: Turn[] = [
  { from: "raven", text: "ok" },
  { from: "jarvis", text: "I need the actual node id before I can promote it" },
  { from: "raven", text: "ok" },
  { from: "jarvis", text: "I need the actual node id before I can promote it" },
];
check("jarvis repeating itself -> loop", loopGuard(jarvisRepeats, "go") === "loop");

const ravenRepeats: Turn[] = [
  { from: "raven", text: "promote node alpha now" },
  { from: "jarvis", text: "AEGIS blocked it — alignment below threshold" },
];
check("raven re-sends same input -> repeat", loopGuard(ravenRepeats, "promote node alpha now") === "repeat");

// --- jaccard ---
check("identical strings -> 1", jaccard("alpha beta", "beta alpha") === 1);
check("disjoint strings -> 0", jaccard("alpha", "beta") === 0);

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
