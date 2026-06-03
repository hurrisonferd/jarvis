// Council tests. Run: node --experimental-strip-types council.test.ts
import { councilVote, deliberationDirective, memberProfile, registry, reviewOutput, shouldDeliberate, TIERS, TIER_WEIGHT } from "./council.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

// --- registry covers all 27 ---
const allSystems = Object.values(TIERS).flat();
check("registry covers 27 god systems", allSystems.length === 27);
check("registry groups by tier (the folders)", Object.keys(registry()).length === Object.keys(TIERS).length);

// --- member profile: fixed authority by tier ---
const aegis = memberProfile("AEGIS");
check("AEGIS is T1 with its tier weight", aegis.tier === "T1" && aegis.weight === TIER_WEIGHT.T1);
check("member has a fixed role", aegis.role.includes("constraint"));
const apollo = memberProfile("APOLLO");
check("interface tier weighs less than guardian tier", apollo.weight < aegis.weight);
const zeus = memberProfile("ZEUS");
check("T0 carries top authority", zeus.weight === 1.0);

// --- council vote: deterministic, sorted by fixed weight ---
const routing = { intent: "remember", primary: "MNEMOS", triggered: [{ system: "AEGIS" }, { system: "SKADI" }, { system: "MNEMOS" }] };
const aegisResults = [{ capability: { system: "MNEMOS" }, verdict: "REDIRECT" }];
const trace = councilVote(routing, aegisResults);
check("vote resolves to the routing primary", trace.resolved === "MNEMOS");
check("vote carries the intent", trace.intent === "remember");
check("votes sorted by descending weight", trace.votes.every((v, i) => i === 0 || trace.votes[i - 1].weight >= v.weight));
check("AEGIS verdict flows into the member's vote", trace.votes.find((v) => v.system === "MNEMOS")?.verdict === "REDIRECT");
check("summary names the leader + member count", trace.summary.includes("MNEMOS leads") && trace.summary.includes("member"));

// --- empty routing degrades cleanly ---
const empty = councilVote({ intent: "converse", primary: "HALO", triggered: [{ system: "HALO" }] }, []);
check("converse turn resolves to HALO", empty.resolved === "HALO");

// --- output review: flags a held write claimed as done ---
const flagged = reviewOutput("Done — I saved that to memory.", [{ verdict: "REDIRECT", capability: { system: "MNEMOS" } }]);
check("review FLAGs a held write claimed done", flagged.verdict === "FLAG" && flagged.flags.length === 1);
const clean = reviewOutput("Here's my read, Raven — though I'm inferring the second half.", [{ verdict: "REDIRECT", capability: { system: "MNEMOS" } }]);
check("review PASSes an honest reply with no false claim", clean.verdict === "PASS");
check("review always returns the council instruction", clean.instruction.includes("honesty layer"));

// --- conditional deliberation: fires only on heavy intents ---
check("deliberate on plan", shouldDeliberate("plan"));
check("deliberate on decide/audit/expansion", shouldDeliberate("decide") && shouldDeliberate("audit") && shouldDeliberate("expansion"));
check("deliberate on analyze", shouldDeliberate("analyze"));
check("do NOT deliberate on converse", !shouldDeliberate("converse"));
check("do NOT deliberate on recall", !shouldDeliberate("recall"));

const planTrace = councilVote({ intent: "plan", primary: "ATHENA", triggered: [{ system: "ATHENA" }, { system: "MERIDIAN" }, { system: "MIMIR" }] }, []);
const delib = deliberationDirective(planTrace);
check("plan turn triggers deliberation", !!delib && delib.triggered);
check("deliberation carries the engaged lenses", !!delib && delib.lenses.length === 3 && delib.lenses.some((l) => l.system === "ATHENA"));
check("deliberation instruction names the lenses + integrated read", !!delib && delib.instruction.includes("ATHENA") && delib.instruction.includes("integrated read"));

const converseTrace = councilVote({ intent: "converse", primary: "HALO", triggered: [{ system: "HALO" }] }, []);
check("converse turn does NOT deliberate", deliberationDirective(converseTrace) === undefined);

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
