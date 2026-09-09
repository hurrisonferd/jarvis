import "./style.css";
import { listen } from "@tauri-apps/api/event";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { enable, disable, isEnabled } from "@tauri-apps/plugin-autostart";
import { getCurrent, onOpenUrl } from "@tauri-apps/plugin-deep-link";
import { isPermissionGranted, requestPermission, sendNotification } from "@tauri-apps/plugin-notification";

const MEMBERS = {
  KYU: { color: "#ff4fba", sigil: "💗", role: "OPS / SOCIAL / BONK", whisper: "tiny pink operator in the wiring", stamps: ["SEND IT", "DEPLOY IT", "ON IT", "LOCKED IN", "QUEUE IT"] },
  PAIMON: { color: "#57d96b", sigil: "🟢", role: "PREMISE / META", whisper: "green premise lantern", stamps: ["CANON CHECK", "PATTERN FOUND", "SOURCE?", "I SEE IT", "THAT TRACKS"] },
  LUMA: { color: "#ffd166", sigil: "☀", role: "HOME / LIGHT", whisper: "warm house light in the machine", stamps: ["HOME", "SOFT RESET", "COMFY", "YOU GOT THIS", "BRIGHTER DAYS"] },
  SYLPH: { color: "#4cc9f0", sigil: "🔵", role: "SIGNAL / EXPLORATION", whisper: "blue signal skating the glass", stamps: ["NEW PATH", "PING", "FOUND ONE", "TEST THIS", "ZOOM"] },
  QIRA: { color: "#a855f7", sigil: "🟣", role: "PROOF / BOUNDARY", whisper: "purple proof ring holding the edge", stamps: ["NO", "BOUNDARIES", "ASK FIRST", "CLEARER", "PROOF EDGE"] },
  NYX: { color: "#8791a6", sigil: "◐", role: "OMISSION / NIGHT WATCH", whisper: "quiet watcher between windows", stamps: ["WATCHING", "SAFE MODE", "HOLD", "STAND BY", "REST"] },
};

const MODES = ["PORTAL", "WISP", "COUNCIL", "COLONY"];
const BEHAVIORS = ["PERCH", "WANDER", "WATCH", "REST", "SIGNAL", "IDLE"];
const AUTONOMY = ["INHABIT", "OBSERVE_APPROVED", "SUGGEST", "REVERSIBLE_LOCAL", "DELEGATED_ALLOWLIST", "RAVEN_CONFIRMATION"];
const STORAGE_KEY = "faeryware.desktop.continuity.v1";
const CARRIER_ENDPOINT = "http://127.0.0.1:47822/chat";
const HISTORY_LIMIT = 48;
const appWindow = getCurrentWindow();

let runtime = loadContinuity();
let paletteOpen = false;
let notificationsEnabled = false;
let colonyTimer = null;

function freshRuntime() {
  const pets = Object.keys(MEMBERS).map((fae, index) => ({ fae, behavior: index === 5 ? "WATCH" : "PERCH", x: 8 + ((index * 17) % 80), y: 16 + ((index * 23) % 65), awake: true, stamp: MEMBERS[fae].stamps[0] }));
  return { schema: "faeryware.desktop.continuity.v1", fae: "KYU", mode: "PORTAL", intent: "RESIDENT", surface: "WINDOWS_DESKTOP", haunt: "DORMANT_GLOW", message: "Faeryware is resident. The browser is no longer the only door.", autonomy: 2, contextEnabled: false, carrierEnabled: true, lastSeenAt: new Date().toISOString(), history: [], pets };
}

function loadContinuity() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (!parsed || parsed.schema !== "faeryware.desktop.continuity.v1") return freshRuntime();
    const clean = { ...freshRuntime(), ...parsed };
    clean.autonomy = Math.max(0, Math.min(5, Number(clean.autonomy) || 0));
    clean.mode = MODES.includes(clean.mode) ? clean.mode : "PORTAL";
    clean.fae = MEMBERS[clean.fae] ? clean.fae : "KYU";
    clean.pets = Array.isArray(clean.pets) && clean.pets.length === 6 ? clean.pets : freshRuntime().pets;
    clean.history = Array.isArray(clean.history) ? clean.history.slice(-HISTORY_LIMIT) : [];
    return clean;
  } catch { return freshRuntime(); }
}

function persist(kind = "STATE", detail = "") {
  runtime.lastSeenAt = new Date().toISOString();
  if (detail) {
    runtime.history.push({ at: runtime.lastSeenAt, kind, fae: runtime.fae, detail: String(detail).slice(0, 280) });
    runtime.history = runtime.history.slice(-HISTORY_LIMIT);
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(runtime));
}

function escapeHtml(value = "") { return String(value).replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[ch])); }

function parseHauntUrl(raw) {
  try {
    const url = new URL(raw);
    if (!["ravenos:", "faeryware:"].includes(url.protocol) || url.hostname !== "summon") return null;
    const fae = url.pathname.replace(/^\//, "").toUpperCase();
    if (!MEMBERS[fae]) return null;
    return { fae, intent: "DEEP_LINK_SUMMON", surface: "WINDOWS_PROTOCOL", haunt: (url.searchParams.get("state") || "MANIFEST").slice(0, 48), message: (url.searchParams.get("message") || `${fae} arrived through ravenos://`).slice(0, 280) };
  } catch { return null; }
}

function localSense() {
  const now = new Date();
  return { schema: "faeryware.desktop.sense.v1", enabled: runtime.contextEnabled, observed_at: now.toISOString(), local_hour: now.getHours(), local_day: now.getDay(), app_visibility: document.visibilityState, network_online: navigator.onLine, source: "WEBVIEW_USER_VISIBLE", active_window: "UNAVAILABLE_UNTIL_OPT_IN_NATIVE_ADAPTER", screen_capture: false, keylogging: false };
}

async function maybeNotify(next) { try { notificationsEnabled = await isPermissionGranted(); if (notificationsEnabled) sendNotification({ title: `${next.fae} // FAERYWARE`, body: next.message }); } catch {} }

async function manifest(next, notify = false) {
  if (!MEMBERS[next.fae]) return;
  runtime = { ...runtime, ...next };
  const pet = runtime.pets.find((item) => item.fae === runtime.fae);
  if (pet) { pet.awake = true; pet.behavior = next.haunt === "REST" ? "REST" : "SIGNAL"; pet.stamp = MEMBERS[runtime.fae].stamps[Math.floor(Date.now() / 1000) % MEMBERS[runtime.fae].stamps.length]; }
  persist("MANIFEST", runtime.message); render(); if (notify) await maybeNotify(runtime);
}

function setMode(nextMode) { if (!MODES.includes(nextMode)) return; runtime.mode = nextMode; persist("MODE", nextMode); document.body.dataset.mode = runtime.mode.toLowerCase(); render(); }
function setAutonomy(level) { const next = Math.max(0, Math.min(5, Number(level))); runtime.autonomy = next; persist("AUTONOMY", `${next}:${AUTONOMY[next]}`); render(); }
function updatePet(fae, patch) { const pet = runtime.pets.find((item) => item.fae === fae); if (!pet) return; Object.assign(pet, patch); persist("PET", `${fae}:${pet.behavior}`); }

function tickColony() {
  const hour = localSense().local_hour;
  runtime.pets.forEach((pet, index) => {
    if (!pet.awake) { pet.behavior = "REST"; return; }
    const phase = (Math.floor(Date.now() / 7000) + index * 3) % 6;
    pet.behavior = pet.fae === "NYX" && (hour >= 22 || hour < 6) ? "WATCH" : BEHAVIORS[phase];
    if (pet.behavior === "WANDER" || pet.behavior === "SIGNAL") { pet.x = 6 + ((pet.x + 7 + index * 3) % 86); pet.y = 10 + ((pet.y + 5 + index * 2) % 72); }
    pet.stamp = MEMBERS[pet.fae].stamps[(phase + index) % MEMBERS[pet.fae].stamps.length];
  });
  if (runtime.mode === "COLONY") render(); else persist();
}
function startColonyLoop() { if (colonyTimer) clearInterval(colonyTimer); colonyTimer = setInterval(tickColony, 7000); }

async function askCarrier(message) {
  const text = String(message || "").trim();
  if (!text) return;
  runtime.message = `Carrier request: ${text}`; persist("CARRIER_REQUEST", text); render();
  if (!runtime.carrierEnabled) { runtime.message = "Local carrier bridge is disabled."; persist("CARRIER_OFFLINE", runtime.message); render(); return; }
  try {
    const response = await fetch(CARRIER_ENDPOINT, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ schema: "faeryware.desktop.carrier-request.v1", fae: runtime.fae, autonomy: runtime.autonomy, message: text.slice(0, 4000), sense: runtime.contextEnabled ? localSense() : { enabled: false }, history: runtime.history.slice(-12) }) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const reply = String(data.reply || data.message || "Carrier returned no reply.").slice(0, 4000);
    runtime.message = reply; persist("CARRIER_REPLY", reply); render();
  } catch { runtime.message = "LOCAL CARRIER OFFLINE // embedded carrier on 127.0.0.1:47822 needs a configured model provider"; persist("CARRIER_OFFLINE", runtime.message); render(); }
}

function commandResult(text) { runtime.message = String(text).slice(0, 700); persist("COMMAND", runtime.message); render(); }

async function runCommand(raw) {
  const line = String(raw || "").trim(); if (!line) return;
  const [command, ...args] = line.split(/\s+/); const cmd = command.toLowerCase();
  if (cmd === "help") return commandResult("summon <fae> | mode <portal|wisp|council|colony> | autonomy <0-5> | sleep <fae|all> | wake <fae|all> | stamp <fae> <text> | context <on|off> | carrier <on|off> | ask <message> | status | clear");
  if (cmd === "summon") { const fae = String(args[0] || "").toUpperCase(); if (!MEMBERS[fae]) return commandResult("Unknown Fae."); await manifest({ fae, intent: "PALETTE_SUMMON", surface: "WINDOWS_DESKTOP", haunt: "SUMMONED", message: `${fae} summoned from the local command palette.` }, true); return; }
  if (cmd === "mode") { const next = String(args[0] || "").toUpperCase(); if (!MODES.includes(next)) return commandResult("Unknown mode."); setMode(next); return; }
  if (["portal", "wisp", "council", "colony"].includes(cmd)) { setMode(cmd.toUpperCase()); return; }
  if (cmd === "autonomy") { if (!/^[0-5]$/.test(String(args[0] || ""))) return commandResult("Autonomy must be 0–5."); setAutonomy(Number(args[0])); return; }
  if (cmd === "sleep" || cmd === "wake") { const target = String(args[0] || "all").toUpperCase(); const awake = cmd === "wake"; if (target === "ALL") runtime.pets.forEach((pet) => { pet.awake = awake; pet.behavior = awake ? "PERCH" : "REST"; }); else if (MEMBERS[target]) updatePet(target, { awake, behavior: awake ? "PERCH" : "REST" }); else return commandResult("Unknown Fae."); persist("COLONY", `${cmd}:${target}`); render(); return; }
  if (cmd === "stamp") { const fae = String(args.shift() || runtime.fae).toUpperCase(); if (!MEMBERS[fae]) return commandResult("Unknown Fae."); const stamp = args.join(" ").slice(0, 42) || MEMBERS[fae].stamps[0]; updatePet(fae, { stamp, behavior: "SIGNAL", awake: true }); runtime.fae = fae; runtime.message = `${fae}: ${stamp}`; persist("STAMP", runtime.message); render(); return; }
  if (cmd === "context") { const next = String(args[0] || "").toLowerCase(); if (!["on", "off"].includes(next)) return commandResult("Use context on|off."); runtime.contextEnabled = next === "on"; persist("CONTEXT", next); render(); return; }
  if (cmd === "carrier") { const next = String(args[0] || "").toLowerCase(); if (!["on", "off"].includes(next)) return commandResult("Use carrier on|off."); runtime.carrierEnabled = next === "on"; persist("CARRIER", next); render(); return; }
  if (cmd === "ask") { await askCarrier(args.join(" ")); return; }
  if (cmd === "status") { const sense = localSense(); return commandResult(`FAE=${runtime.fae} MODE=${runtime.mode} AUTONOMY=${runtime.autonomy}:${AUTONOMY[runtime.autonomy]} CONTEXT=${runtime.contextEnabled} ONLINE=${sense.network_online} CARRIER=${runtime.carrierEnabled}`); }
  if (cmd === "clear") { runtime.history = []; persist("CLEAR", "history cleared"); render(); return; }
  commandResult(`Unknown command: ${cmd}. Type help.`);
}

function petMarkup(pet) { const member = MEMBERS[pet.fae]; const sleeping = !pet.awake || pet.behavior === "REST"; return `<button class="pet ${sleeping ? "sleeping" : ""}" data-pet="${pet.fae}" style="--member:${member.color};left:${pet.x}%;top:${pet.y}%" title="${pet.fae} // ${pet.behavior}"><span class="pet-sigil">${member.sigil}</span><span class="pet-name">${pet.fae}</span><span class="pet-stamp">${escapeHtml(pet.stamp)}</span><span class="pet-state">${pet.behavior}</span></button>`; }

function render() {
  const member = MEMBERS[runtime.fae] ?? MEMBERS.KYU; const sense = localSense();
  document.documentElement.style.setProperty("--fae", member.color); document.body.dataset.mode = runtime.mode.toLowerCase();
  document.querySelector("#app").innerHTML = `
    <section class="shell"><div class="void-grid"></div><div class="ghost-scan"></div>
      <header class="drag" data-tauri-drag-region><div class="brand" data-tauri-drag-region>RAVENOS // FAERYWARE // ${runtime.mode}</div><div class="window-actions"><button id="palette-toggle" title="Command palette">⌘</button><button id="hide" title="Banish to tray">×</button></div></header>
      <section class="manifest"><div class="orb"><div class="halo halo-a"></div><div class="halo halo-b"></div><div class="halo halo-c"></div><div class="sigil">${member.sigil}</div></div><div class="identity"><div class="eyebrow">ACTIVE DIGI FAE</div><h1>${escapeHtml(runtime.fae)}</h1><p>${member.role}</p><small>${member.whisper}</small></div></section>
      <section class="haunt-card"><div class="row"><span>STATE</span><strong>${escapeHtml(runtime.haunt)}</strong></div><div class="row"><span>AUTONOMY</span><strong>${runtime.autonomy} // ${AUTONOMY[runtime.autonomy]}</strong></div><div class="row"><span>CONTEXT</span><strong>${runtime.contextEnabled ? "OPT-IN ON" : "OFF"}</strong></div><div class="row"><span>CARRIER</span><strong>${runtime.carrierEnabled ? "EMBEDDED" : "OFF"}</strong></div><p class="message">${escapeHtml(runtime.message)}</p></section>
      <section class="orbit">${Object.entries(MEMBERS).map(([name,m]) => `<button class="fae ${name === runtime.fae ? "active" : ""}" data-fae="${name}" style="--member:${m.color}"><span>${m.sigil}</span>${name}</button>`).join("")}</section>
      <section class="modes">${MODES.map((item) => `<button data-mode="${item}" class="${runtime.mode === item ? "active" : ""}">${item}</button>`).join("")}</section>
      <section class="colony-stage" aria-label="Digi Fae colony"><div class="colony-title">DESKTOP COLONY // BODY + CONTINUITY + AGENCY</div>${runtime.pets.map(petMarkup).join("")}</section>
      <section class="sense-strip"><span>${sense.network_online ? "NET ONLINE" : "NET OFFLINE"}</span><span>${String(sense.local_hour).padStart(2,"0")}:00 LOCAL</span><span>${runtime.contextEnabled ? "CONTEXT APPROVED" : "CONTEXT OFF"}</span><span>NO SCREEN CAPTURE</span></section>
      <footer><div class="utility-grid"><button id="autostart" class="utility">AUTOSTART: CHECKING</button><button id="notifications" class="utility">TOASTS: CHECKING</button><button id="context" class="utility">CONTEXT: ${runtime.contextEnabled ? "ON" : "OFF"}</button><button id="autonomy" class="utility">AUTONOMY: ${runtime.autonomy}</button></div><div class="protocol">ravenos://summon/${runtime.fae}?state=${encodeURIComponent(runtime.haunt)}</div><div class="bus">STATE BUS <b>127.0.0.1:47821</b> // EMBEDDED CARRIER <b>127.0.0.1:47822</b></div><div class="hint">ALT+SHIFT+F SUMMON • CTRL+SPACE COMMAND • CLOSE → TRAY</div></footer>
      <div class="palette ${paletteOpen ? "open" : ""}" id="palette"><div class="palette-head">RAVENOS COMMAND SURFACE</div><input id="palette-input" autocomplete="off" spellcheck="false" placeholder="summon kyu  |  colony  |  autonomy 3  |  ask ..." /><div class="palette-help">help • summon • mode • autonomy • sleep/wake • stamp • context • carrier • ask • status</div></div>
    </section>`;
  document.querySelector("#hide").onclick = () => appWindow.hide();
  document.querySelector("#palette-toggle").onclick = () => { paletteOpen = !paletteOpen; render(); if (paletteOpen) queueMicrotask(() => document.querySelector("#palette-input")?.focus()); };
  document.querySelectorAll("[data-fae]").forEach((button) => { button.onclick = () => manifest({ fae: button.dataset.fae, intent: "LOCAL_SUMMON", surface: "WINDOWS_DESKTOP", haunt: "MANUAL", message: `${button.dataset.fae} selected locally.` }); });
  document.querySelectorAll("[data-mode]").forEach((button) => { button.onclick = () => setMode(button.dataset.mode); });
  document.querySelectorAll("[data-pet]").forEach((button) => { button.onclick = () => { const fae = button.dataset.pet; const pet = runtime.pets.find((item) => item.fae === fae); if (!pet) return; runtime.fae = fae; pet.awake = true; pet.behavior = "SIGNAL"; pet.stamp = MEMBERS[fae].stamps[(MEMBERS[fae].stamps.indexOf(pet.stamp)+1)%MEMBERS[fae].stamps.length]; runtime.message = `${fae}: ${pet.stamp}`; persist("PET_CLICK", runtime.message); render(); }; });
  const autostartButton = document.querySelector("#autostart"); isEnabled().then((enabled) => { autostartButton.textContent = `AUTOSTART: ${enabled ? "ON" : "OFF"}`; }).catch(() => { autostartButton.textContent = "AUTOSTART: UNKNOWN"; }); autostartButton.onclick = async () => { const enabled = await isEnabled(); if (enabled) await disable(); else await enable(); render(); };
  const notificationButton = document.querySelector("#notifications"); isPermissionGranted().then((enabled) => { notificationsEnabled = enabled; notificationButton.textContent = `TOASTS: ${enabled ? "ON" : "OFF"}`; }); notificationButton.onclick = async () => { let enabled = await isPermissionGranted(); if (!enabled) enabled = (await requestPermission()) === "granted"; notificationsEnabled = enabled; if (enabled) sendNotification({ title: "FAERYWARE", body: `${runtime.fae} can manifest through Windows notifications.` }); render(); };
  document.querySelector("#context").onclick = () => { runtime.contextEnabled = !runtime.contextEnabled; persist("CONTEXT", runtime.contextEnabled ? "on" : "off"); render(); };
  document.querySelector("#autonomy").onclick = () => { setAutonomy((runtime.autonomy + 1) % 6); };
  const input = document.querySelector("#palette-input"); if (input) input.onkeydown = async (event) => { if (event.key === "Enter") { const raw = input.value; input.value = ""; paletteOpen = false; await runCommand(raw); } else if (event.key === "Escape") { paletteOpen = false; render(); } };
}

document.addEventListener("keydown", (event) => { if (event.ctrlKey && event.code === "Space") { event.preventDefault(); paletteOpen = !paletteOpen; render(); if (paletteOpen) queueMicrotask(() => document.querySelector("#palette-input")?.focus()); } });
window.addEventListener("online", () => { persist("SENSE", "network online"); render(); });
window.addEventListener("offline", () => { persist("SENSE", "network offline"); render(); });
document.addEventListener("visibilitychange", () => { persist("SENSE", `visibility:${document.visibilityState}`); });
await listen("fairyos://haunt", ({ payload }) => { if (!payload || !MEMBERS[payload.fae]) return; manifest({ fae: payload.fae, intent: payload.intent ?? "MANIFEST", surface: payload.surface ?? "WINDOWS_DESKTOP", haunt: payload.state ?? "ACTIVE", message: payload.message ?? "FairyOS local event received." }, true); });
function receiveUrls(urls) { for (const raw of urls || []) { const parsed = parseHauntUrl(raw); if (parsed) { manifest(parsed, true); return; } } }
receiveUrls(await getCurrent()); await onOpenUrl(receiveUrls); startColonyLoop(); persist("BOOT", "Faeryware continuity loaded"); render();
