// ODIN router tests. Run: node --experimental-strip-types router.test.ts
import { route, routeSummary, hasForbiddenHop } from "./router.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

// --- intent classification ---
check("recall -> MNEMOS primary", route("what did we decide last time about the grid").primary === "MNEMOS");
check("execute -> SKADI primary", route("build the handler carve and push it").primary === "SKADI");
check("audit -> NEMESIS primary", route("audit the god systems for overlap").primary === "NEMESIS");
check("analyze -> HUGINN primary", route("lets do an analysis of ac last raven").primary === "HUGINN");
check("plan -> ATHENA primary", route("how do we design the routing layer").primary === "ATHENA");
check("integrate -> BIFROST primary", route("deploy the edge function to supabase").primary === "BIFROST");
check("render -> APOLLO primary", route("generate a concept card image").primary === "APOLLO");
check("decide -> AEGIS primary", route("approve this and go ahead").primary === "AEGIS");
check("expansion -> PROMETHEUS primary", route("add a new god system for caching").primary === "PROMETHEUS");
check("companion -> HALO primary", route("I'm tired and this is hard").primary === "HALO");
check("plain talk -> converse/HALO", route("hey jarvis").intent === "converse");

// --- spine always anchored ---
check("AYRE heads every spine", route("build something").spine[0] === "AYRE");
check("ERIS guardian always present", route("build something").spine.includes("ERIS"));
check("MNEMOS tails every spine", route("anything").spine.at(-1) === "MNEMOS");

// --- governance: execute routes AEGIS before SKADI, never the reverse ---
const ex = route("deploy and run the build");
check("execute includes AEGIS and SKADI", ex.spine.includes("AEGIS") && ex.spine.includes("SKADI"));
check("AEGIS precedes SKADI in spine", ex.spine.indexOf("AEGIS") < ex.spine.indexOf("SKADI"));

// --- forbidden edges never appear as adjacent hops ---
const intents = ["build it", "audit it", "deploy it", "remember it", "plan it", "approve it", "add a new system", "render an image", "hey"];
let anyForbidden = false;
for (const i of intents) if (hasForbiddenHop(route(i).spine)) anyForbidden = true;
check("no forbidden adjacent hop across all intents", !anyForbidden);

// --- forbidden detector itself works ---
check("detector catches SKADI->AEGIS", hasForbiddenHop(["SKADI", "AEGIS"]) === true);
check("detector passes clean seq", hasForbiddenHop(["AYRE", "AEGIS", "SKADI"]) === false);

// --- summary renders ---
check("summary mentions primary", routeSummary(route("build it")).includes("primary SKADI"));

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
