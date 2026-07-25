// Grid federation tests. Run: node --experimental-strip-types grid.test.ts
import { buildNodeCard, buildPortableIdentity, GRID_VERSION, validateInbound } from "./grid.ts";

let pass = 0, fail = 0;
function check(name: string, cond: boolean) {
  if (cond) { pass++; console.log("  ok  -", name); }
  else { fail++; console.log("FAIL  -", name); }
}

// --- Brick 1: node card ---
const card = buildNodeCard({
  nodeId: "raven-node-0",
  keelExcerpt: "JARVIS is a companion intelligence, built with Raven.",
  capabilities: ["jarvis_query", "jarvis_recall"],
  baseUrl: "https://x.supabase.co/functions/v1/jarvis-mcp/",
});
check("card carries the grid version", card.grid_version === GRID_VERSION);
check("card identifies node + companion + owner", card.node_id === "raven-node-0" && card.companion === "JARVIS" && card.owner.includes("Raven"));
check("card lists capabilities", card.capabilities.includes("jarvis_query"));
check("card consent holds inbound for owner, no auto-act", card.consent.inbound_messages === "held_for_owner" && card.consent.auto_act === false);
check("card strips trailing slash and derives inbox", card.endpoints.mcp.endsWith("jarvis-mcp") && card.endpoints.inbox.endsWith("/node/message"));
check("keel excerpt is bounded", buildNodeCard({ nodeId: "n", keelExcerpt: "x".repeat(900), capabilities: [], baseUrl: "https://h" }).keel_excerpt.length === 400);

// --- Brick 2: portable identity ---
const disc = buildPortableIdentity({ card, keel: "KEEL TEXT", accumulation: "FOLD TEXT", now: "2026-06-03T00:00:00Z" });
check("disc carries keel + accumulation", disc.keel === "KEEL TEXT" && disc.accumulation === "FOLD TEXT");
check("disc embeds the card", disc.card.node_id === "raven-node-0");
check("disc records export time + ownership note", disc.exported_at === "2026-06-03T00:00:00Z" && disc.note.includes("owned by Raven"));

// --- Brick 3: inbound validation ---
const good = validateInbound({ from_node: "ayre-node-1", from_companion: "AYRE", to_node: "raven-node-0", body: "hello from another node" });
check("valid inbound passes", good.ok === true && good.ok && good.msg.from_companion === "AYRE");
check("inbound defaults intent to message", good.ok && good.msg.intent === "message");
check("missing from_node is rejected", validateInbound({ to_node: "x", body: "y" }).ok === false);
check("missing body is rejected", validateInbound({ from_node: "a", to_node: "b" }).ok === false);
check("non-object is rejected", validateInbound("nope").ok === false);
check("over-long body is rejected", validateInbound({ from_node: "a", to_node: "b", body: "x".repeat(4001) }).ok === false);

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) process.exit(1);
