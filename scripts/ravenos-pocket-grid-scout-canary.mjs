#!/usr/bin/env node
/**
 * Offline DOM harness for the Pocket Grid Scout cartridge.
 * This is not a real browser/device canary; it exercises the page controller with
 * deterministic DOM and fetch stubs, including escaping and source-host validation.
 */
import fs from "node:fs";
import vm from "node:vm";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const html = fs.readFileSync(path.join(root, "ravenos-gameboy.html"), "utf8");
const js = fs.readFileSync(path.join(root, "ravenos-gameboy-v4.js"), "utf8");
const bridge = fs.readFileSync(path.join(root, "ravenos-pocket-grid-scout-bridge.js"), "utf8");
const registry = JSON.parse(fs.readFileSync(path.join(root, "ravenos-pocket-cartridges.json"), "utf8"));
const packet = JSON.parse(fs.readFileSync(path.join(root, "ravenos-public-haunt.json"), "utf8"));

for (const source of [js, bridge]) new vm.Script(source);
if (!html.includes("./ravenos-pocket-grid-scout-bridge.js")) throw new Error("GRID_SCOUT_BRIDGE_SCRIPT_MISSING");
if (!registry.cartridges.some((c) => c.id === "grid_scout")) throw new Error("GRID_SCOUT_CARTRIDGE_MISSING");
if (registry.effect_authority !== false || registry.effect_budget !== 0) throw new Error("PUBLIC_EFFECT_BOUNDARY_CHANGED");

const ui = { innerHTML: "" };
const body = { clientHeight: 500, scrollHeight: 500, scrollTop: 0, addEventListener() {}, scrollBy() {} };
const elements = {
  ui,
  packet: { textContent: "", style: {} },
  led: { style: {} },
  scrollThumb: { style: {} },
  screenBody: body,
  gridScoutQuery: { value: "llama.cpp" },
};
const document = {
  hidden: false,
  getElementById(id) { return elements[id] || null; },
  querySelectorAll() { return []; },
  addEventListener() {},
};
const candidate = (overrides = {}) => ({
  participant_type: "OPEN_SOURCE_REPOSITORY",
  name: "ggml-org/llama.cpp",
  version: "master",
  author: "ggml-org",
  license: "MIT",
  description: "<script>alert(1)</script>",
  pipeline_tag: "ggml",
  library_name: "C++",
  downloads: null,
  likes: 136263,
  last_modified: "2026-11-25T19:50:27Z",
  gated: false,
  access_mode: "PUBLIC_READ",
  source_uri: "https://github.com/ggml-org/llama.cpp",
  discovery_state: "DISCOVERED",
  trust_state: "UNASSESSED",
  contact_state: "NOT_CONTACTED",
  invocation_state: "NOT_INVOKED",
  ...overrides,
});
const publicResult = {
  schema: "grid.public-scout.result.v1",
  version: "grid-public-scout-v0.2",
  query: "llama.cpp",
  generated_at: "2026-11-25T21:34:30.932Z",
  sources: {
    mcp_registry: { status: "READ_OK", count: 0 },
    huggingface_hub: { status: "UNAVAILABLE", count: 0 },
    github_repositories: { status: "READ_OK", count: 3 },
  },
  candidates: [candidate()],
  boundaries: ["PUBLIC_METADATA_ONLY", "NO_PEER_CONTACT"],
  total_candidates: 1,
  claim_ceiling: "PUBLIC METADATA ONLY",
};
const window = {
  addEventListener() {},
  RavenOSPublicContract: { validatePacket: () => ({ ok: true }) },
  RavenOSPocketContract: { validateRegistry: (r) => ({ ok: true, count: r.cartridges.length }) },
};
const fetch = async (url, options = {}) => {
  if (url === "./ravenos-public-haunt.json") return { ok: true, json: async () => packet };
  if (url === "./ravenos-pocket-cartridges.json") return { ok: true, json: async () => registry };
  if (String(url).includes("/functions/v1/grid-public-scout")) {
    if (options.method !== "POST") throw new Error("PUBLIC_SCOUT_METHOD");
    const body = JSON.parse(options.body);
    if (body.scope !== "all" || body.limit !== 5 || body.query !== "llama.cpp") throw new Error("PUBLIC_SCOUT_REQUEST_SHAPE");
    return { ok: true, json: async () => publicResult };
  }
  throw new Error("UNEXPECTED_FETCH:" + url);
};
const context = {
  window, document, fetch, URL, console,
  requestAnimationFrame: (fn) => fn(),
  CustomEvent: class CustomEvent { constructor(type, init) { this.type = type; this.detail = init?.detail; } },
};
window.window = window;
vm.createContext(context);
vm.runInContext(js, context);
await new Promise((resolve) => setTimeout(resolve, 0));

const rack = registry.cartridges.filter((c) => c.id !== "home").sort((a, b) => a.order - b.order);
const index = rack.findIndex((c) => c.id === "grid_scout");
if (index < 0) throw new Error("GRID_SCOUT_NOT_IN_RACK");
for (let i = 0; i < index; i++) window.nav(1);
window.ok();
await window.runGridScout();

if (!ui.innerHTML.includes("ggml-org/llama.cpp")) throw new Error("CANDIDATE_NOT_RENDERED");
if (!ui.innerHTML.includes("&lt;script&gt;alert(1)&lt;/script&gt;")) throw new Error("UNTRUSTED_DESCRIPTION_NOT_ESCAPED");
if (ui.innerHTML.includes("<script>alert(1)</script>")) throw new Error("RAW_HTML_INJECTION");
if (!ui.innerHTML.includes("NOT CONTACTED")) throw new Error("CONTACT_BOUNDARY_NOT_RENDERED");
if (!ui.innerHTML.includes("huggingface_hub")) throw new Error("SOURCE_RECEIPT_NOT_RENDERED");
if (ui.innerHTML.includes("PRIVATE CANDIDATE ROWS")) throw new Error("PRIVATE_REVIEW_LEAK");

console.log("POCKET_GRID_SCOUT_DOM_HARNESS=PASS");
console.log("PUBLIC_SCOUT_FETCH=PASS");
console.log("GITHUB_CANDIDATE_RENDER=PASS");
console.log("UNTRUSTED_HTML_ESCAPING=PASS");
console.log("PRIVATE_REVIEW_BOUNDARY=PASS");
console.log("EFFECT_AUTHORITY=FALSE");
