// Council tests. Run: node --experimental-strip-types council.test.ts
import { AYRE_OBJECTIVE, ayreStream, COMMENTARY, councilAnalysisDirective, councilVote, deliberationDirective, MAX_LENSES, memberProfile, registry, reviewOutput, selectLenses, shouldDeliberate, TIERS, TIER_WEIGHT } from "./council.ts";

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
check("deliberate on decide/memory/audit/expansion", shouldDeliberate("decide") && shouldDeliberate("audit") && shouldDeliberate("expansion"));
check("deliberate on analyze", shouldDeliberate("analyze"));
check("do NOT deliberate on converse", !shouldDeliberate("converse"));
check("do NOT deliberate on recall", !shouldDeliberate("recall"));

const planTrace = councilVote({ intent: "plan", primary: "ATHENA", triggered: [{ system: "ATHENA" }, { system: "MERIDIAN" }, { system: "MIMIR" }] }, []);
const delib = deliberationDirective(planTrace);
check("plan turn triggers deliberation", !!delib && delib.triggered);
check("deliberation carries the engaged lenses + HUGINN synthesis", !!delib && delib.lenses.length >= 3 && delib.lenses.some((l) => l.system === "ATHENA") && delib.lenses.some((l) => l.system === "HUGINN"));
check("deliberation instruction names the lenses + integrated read", !!delib && delib.instruction.includes("ATHENA") && delib.instruction.includes("integrated read"));

const converseTrace = councilVote({ intent: "converse", primary: "HALO", triggered: [{ system: "HALO" }] }, []);
check("converse turn does NOT deliberate", deliberationDirective(converseTrace) === undefined);

// --- council analysis: JARVIS + AYRE always; god systems conditional ---
const leanAnalysis = councilAnalysisDirective(converseTrace);
check("council always carries JARVIS + AYRE", leanAnalysis.companions.includes("JARVIS") && leanAnalysis.companions.includes("AYRE"));
check("lean turn engages NO god systems", leanAnalysis.godSystems === false && leanAnalysis.lenses.length === 0);
check("lean analysis = streams stand alone, no separate council block", leanAnalysis.instruction.includes("stand on their own") && leanAnalysis.lenses.length === 0);
const heavyAnalysis = councilAnalysisDirective(planTrace);
check("heavy turn keeps both companions", heavyAnalysis.companions.includes("JARVIS") && heavyAnalysis.companions.includes("AYRE"));
check("heavy turn engages the god systems", heavyAnalysis.godSystems === true && heavyAnalysis.lenses.some((l) => l.system === "ATHENA"));
check("heavy analysis = lenses critique BOTH streams", heavyAnalysis.instruction.includes("BOTH streams") && heavyAnalysis.instruction.includes("ATHENA"));

// --- THE SPLIT (P44): AYRE is a co-equal stream with an inverted objective ---
const ayre = ayreStream(planTrace);
check("ayre is its own AYRE stream", ayre.stream === "AYRE" && typeof ayre.objective === "string");
check("ayre objective inverts synthesis", AYRE_OBJECTIVE.includes("inverse of synthesis") && /assumption/i.test(AYRE_OBJECTIVE));
check("ayre runs independently, shares the keel", ayre.instruction.includes("INDEPENDENTLY") && ayre.instruction.toLowerCase().includes("keel"));

// --- lens selection: only relevant authorities speak ---
// An integrate turn engages BIFROST/ATLAS/AEGIS — pure-infra systems must NOT become lenses.
const integrateTrace = councilVote({ intent: "audit", primary: "ARGUS", triggered: [{ system: "ARGUS" }, { system: "BIFROST" }, { system: "ATLAS" }, { system: "AEGIS" }] }, []);
const integLenses = selectLenses(integrateTrace, "deploy the edge function to supabase");
check("infrastructure systems do NOT speak (no BIFROST/ATLAS)", !integLenses.some((l) => l.system === "BIFROST" || l.system === "ATLAS"));
check("commentary systems still speak (ARGUS, AEGIS)", integLenses.some((l) => l.system === "ARGUS") && integLenses.some((l) => l.system === "AEGIS"));
check("every selected lens is commentary-capable", integLenses.every((l) => COMMENTARY.has(l.system)));

// Content signals invite the relevant specialist even if ODIN didn't route it.
const riskLenses = selectLenses(planTrace, "what are the failure paths and rollback risks here");
check("risk signal invites LOKI", riskLenses.some((l) => l.system === "LOKI"));
const expandLenses = selectLenses(planTrace, "should we add a new capability to scale this");
check("expansion signal invites PROMETHEUS", expandLenses.some((l) => l.system === "PROMETHEUS"));
check("no false signal, no spurious lens", !selectLenses(planTrace, "tell me about the weather").some((l) => l.system === "LOKI"));

// The cap holds — the council informs, it does not flood.
const flood = selectLenses(planTrace, "expansion failure alignment integrity entropy time redundancy transition context");
check("lenses are capped (no noise)", flood.length <= MAX_LENSES);
check("lenses sorted by descending authority", flood.every((l, i) => i === 0 || flood[i - 1].weight >= l.weight));

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
