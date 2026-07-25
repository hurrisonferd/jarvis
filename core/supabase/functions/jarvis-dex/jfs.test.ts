// JFS helper tests. Run: node --experimental-strip-types jfs.test.ts
import { gl12Errors, isValidJNL, ontologyClass, ownerOf, parseJNL, tierOf } from "./jfs.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

// --- JNL grammar ---
check("valid god-system JNL", isValidJNL("GS-ODN-CORE-0001"));
check("valid full JNL with patch+block", isValidJNL("GS-ODN-RT-0001-P005-B002"));
check("valid arch spec", isValidJNL("ARCH-RT-SPEC-0001"));
check("rejects unknown god system", !isValidJNL("GS-XXX-CORE-0001"));
check("rejects ARCH-*-CORE non-substrate", !isValidJNL("ARCH-FOO-CORE-0001"));
check("allows ARCH-*-SPEC non-substrate", isValidJNL("ARCH-FOO-SPEC-0001"));
check("rejects malformed", !isValidJNL("not-a-jnl"));
check("rejects unknown domain", !isValidJNL("ZZ-ODN-CORE-0001"));

// --- parse throws with reason ---
let threw = false;
try { parseJNL("GS-XXX-CORE-0001"); } catch { threw = true; }
check("parse throws on bad system", threw);

// --- ontology class (reads the JNL type segment) ---
check("GS -> SYSTEM", ontologyClass("GS-ODN-CORE-0001") === "SYSTEM");
check("ARCH CORE -> SYSTEM (kernel)", ontologyClass("ARCH-JFS-CORE-0001") === "SYSTEM");
check("ARCH SPEC -> SPEC", ontologyClass("ARCH-RT-SPEC-0001") === "SPEC");
check("GOV -> SPEC", ontologyClass("GOV-CAN-CORE-0001") === "SPEC");
check("IMPL JCS -> MODULE", ontologyClass("IMPL-JCS-CORE-0001") === "MODULE");
check("IMPL JCSE -> MODULE", ontologyClass("IMPL-JCSE-SPEC-0001") === "MODULE");
check("IMPL JGPP -> SPEC", ontologyClass("IMPL-JGPP-CORE-0001") === "SPEC");
check("PROJ -> SYSTEM", ontologyClass("PROJ-JPL-BIO-0001") === "SYSTEM");
check("CONN -> MODULE", ontologyClass("CONN-MSB-CORE-0001") === "MODULE");
check("AUD -> EVENT", ontologyClass("AUD-SYS-REVW-0001") === "EVENT");
check("IDEA -> ENTITY", ontologyClass("IDEA-USED-LOG-0001") === "ENTITY");
// project cognition-pipeline types
check("project JGPP valid", isValidJNL("PROJ-DEO-JGPP-0001"));
check("project JIP valid", isValidJNL("PROJ-DEO-JIP-0001"));
check("project JD valid", isValidJNL("PROJ-DEO-JD-0001"));
check("JGPP -> ENTITY (exploration)", ontologyClass("PROJ-DEO-JGPP-0001") === "ENTITY");
check("JIP -> SPEC (commit)", ontologyClass("PROJ-DEO-JIP-0001") === "SPEC");
check("JD -> SPEC (truth)", ontologyClass("PROJ-DEO-JD-0001") === "SPEC");

// --- tier ---
check("PROJ -> SIDE", tierOf("PROJ", "ACTIVE") === "SIDE");
check("ARCHIVED -> SIDE", tierOf("ARCH", "ARCHIVED") === "SIDE");
check("GS ACTIVE -> MAIN", tierOf("GS", "ACTIVE") === "MAIN");

// --- owner ---
check("GS owner", ownerOf("GS", "ODIN") === "God Systems");
check("PROJ owner falls back to name", ownerOf("PROJ", "JPL") === "JPL");

// --- GL12 gate ---
check("complete entry passes GL12", gl12Errors({ jnl: "GS-ODN-CORE-0001", cls: "SYSTEM", tier: "MAIN", status: "ACTIVE", tags: ["x"] }).length === 0);
check("missing tags fails GL12", gl12Errors({ jnl: "GS-ODN-CORE-0001", cls: "SYSTEM", tier: "MAIN", status: "ACTIVE", tags: [] }).length > 0);
check("bad class fails GL12", gl12Errors({ jnl: "GS-ODN-CORE-0001", cls: "WUT", tier: "MAIN", status: "ACTIVE", tags: ["x"] }).length > 0);

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
