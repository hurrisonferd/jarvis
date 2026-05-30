// MNEMOS recall tests. Run: node --experimental-strip-types recall.test.ts
import { buildRecallBlock, formatRow, type Scoped } from "./recall.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

const sem = (t: string, s: number): Scoped => ({ text: t, source_type: "context", timestamp: "2026-05-30", similarity: s });
const ex = (t: string): Scoped => ({ text: t, source_type: "speak_input", timestamp: "2026-05-29" });

// --- semantic leads and shows similarity ---
const b = buildRecallBlock({ semantic: [sem("the grid is federated", 0.91)], exchanges: [ex("hey")] });
check("semantic section first", b[0].startsWith("MOST RELEVANT (semantic):"));
check("similarity rendered as %", b[0].includes("~91%"));
check("exchanges follow", b[1].startsWith("RECENT EXCHANGES:"));

// --- dedup: a memory shown semantically never repeats in a later scope ---
const dup = buildRecallBlock({
  semantic: [sem("shared memory line", 0.8)],
  context: [{ text: "shared memory line", source_type: "context" }, { text: "unique ctx", source_type: "context" }],
});
check("dup not repeated in context", !dup.find(p => p.startsWith("RELEVANT CONTEXT"))?.includes("shared memory line"));
check("unique context still shown", dup.find(p => p.startsWith("RELEVANT CONTEXT"))?.includes("unique ctx") === true);

// --- empty scopes omitted ---
const empty = buildRecallBlock({});
check("no scopes -> empty block", empty.length === 0);
const onlyProfile = buildRecallBlock({ profile: [{ text: "Raven = John Barber", source_type: "raven_profile" }] });
check("single scope renders", onlyProfile.length === 1 && onlyProfile[0].startsWith("RAVEN PROFILE:"));

// --- limits respected ---
const many = buildRecallBlock({ semantic: Array.from({ length: 10 }, (_, i) => sem("m" + i, 0.5)) }, { semanticLimit: 3 });
const rowCount = many[0].split("\n").slice(1).length; // drop the header line
check("semantic limit honored", rowCount === 3);

// --- formatRow ---
check("formatRow without similarity omits %", !formatRow({ text: "x", source_type: "decision" }).includes("~"));
check("formatRow truncates long text", formatRow({ text: "z".repeat(300), source_type: "x" }).length < 200);

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
