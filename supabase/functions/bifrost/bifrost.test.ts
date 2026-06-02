// BIFROST tests. Run: node --experimental-strip-types bifrost.test.ts
import { buildRequest, endpoint, parseGrounded, reachSummary } from "./bifrost.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

// --- request building ---
const req = buildRequest("latest on Godot 4");
check("request carries the query", JSON.stringify(req).includes("Godot 4"));
check("request enables google_search tool", JSON.stringify(req).includes("google_search"));
check("query is bounded", (buildRequest("x".repeat(9000)).contents as any)[0].parts[0].text.length <= 4000);

// --- endpoint ---
check("endpoint builds native generateContent URL",
  endpoint("https://generativelanguage.googleapis.com", "gemini-2.0-flash")
  === "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent");
check("endpoint trims trailing slash", endpoint("https://x.com/", "m").startsWith("https://x.com/v1beta"));

// --- parse grounded response ---
const sample = {
  candidates: [{
    content: { parts: [{ text: "Godot 4.3 shipped " }, { text: "with new features." }] },
    groundingMetadata: { groundingChunks: [
      { web: { uri: "https://godotengine.org/a", title: "Godot A" } },
      { web: { uri: "https://godotengine.org/a", title: "dup" } },
      { web: { uri: "https://godotengine.org/b", title: "Godot B" } },
    ] },
  }],
};
const r = parseGrounded(sample);
check("answer concatenates text parts", r.answer === "Godot 4.3 shipped with new features.");
check("sources deduped by uri", r.sources.length === 2);
check("grounded flag set when sources present", r.grounded === true);

const empty = parseGrounded({ candidates: [{ content: { parts: [{ text: "no web" }] } }] });
check("ungrounded when no chunks", empty.grounded === false && empty.answer === "no web");
check("malformed response -> safe empty", parseGrounded(null).answer === "");

// --- summary ---
const s = reachSummary(r);
check("summary includes answer", s.includes("Godot 4.3"));
check("summary numbers sources", s.includes("[1]") && s.includes("SOURCES:"));
check("summary bounded", reachSummary({ answer: "z".repeat(5000), sources: [] }, 800).length <= 820);

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
