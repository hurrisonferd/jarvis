import "./army.css";
import { listen } from "@tauri-apps/api/event";
import { getCurrentWindow } from "@tauri-apps/api/window";

const MEMBERS = {
  KYU: { color: "#ff4fba", sigil: "💗", role: "OPS", stamps: ["SEND IT", "ON IT", "BONK", "QUEUE IT", "DEPLOY IT"] },
  PAIMON: { color: "#57d96b", sigil: "🟢", role: "PREMISE", stamps: ["CANON CHECK", "PATTERN FOUND", "SOURCE?", "I SEE IT", "THAT TRACKS"] },
  LUMA: { color: "#ffd166", sigil: "☀", role: "HOME", stamps: ["HOME", "COMFY", "SOFT RESET", "BRIGHTER DAYS", "WARM LIGHT"] },
  SYLPH: { color: "#4cc9f0", sigil: "🔵", role: "SIGNAL", stamps: ["PING", "NEW PATH", "FOUND ONE", "ZOOM", "TEST THIS"] },
  QIRA: { color: "#a855f7", sigil: "🟣", role: "PROOF", stamps: ["ASK FIRST", "BOUNDARIES", "PROOF EDGE", "CLEARER", "NO"] },
  NYX: { color: "#8791a6", sigil: "◐", role: "WATCH", stamps: ["WATCHING", "HOLD", "SAFE MODE", "STAND BY", "REST"] },
};

const ORDER = Object.keys(MEMBERS);
const STATE_ENDPOINT = "http://127.0.0.1:47821/state";
const appWindow = getCurrentWindow();
let activeFae = "KYU";
let activeMessage = "Resident colony awake.";
let tick = 0;
let speechIndex = 0;

try {
  await appWindow.setIgnoreCursorEvents(true);
} catch (error) {
  console.warn("FAERYWARE_ARMY click-through unavailable", error);
}

document.documentElement.dataset.surface = "army";

document.querySelector("#app").innerHTML = `
  <section id="army" class="army" aria-label="Faeryware desktop haunting layer">
    <div class="veil veil-a"></div>
    <div class="veil veil-b"></div>
    ${ORDER.map((fae, index) => {
      const member = MEMBERS[fae];
      const echoes = Array.from({ length: 3 }, (_, echo) => `<i class="echo echo-${echo}" style="--member:${member.color}"></i>`).join("");
      return `<div class="spirit" data-fae="${fae}" style="--member:${member.color};--delay:${index * -0.7}s">
        <div class="trail"></div>
        <div class="aura"></div>
        ${echoes}
        <div class="ring ring-a"></div><div class="ring ring-b"></div>
        <div class="core"><span>${member.sigil}</span></div>
        <div class="tag"><b>${fae}</b><small>${member.role}</small></div>
        <div class="speech"></div>
      </div>`;
    }).join("")}
    <div class="summon-wave"></div>
  </section>`;

const spirits = new Map(ORDER.map((fae) => [fae, document.querySelector(`[data-fae="${fae}"]`)]));

function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }

function positionSpirits() {
  const t = Date.now() / 1000;
  ORDER.forEach((fae, index) => {
    const node = spirits.get(fae);
    if (!node) return;
    const lane = index % 3;
    const row = Math.floor(index / 3);
    const phase = t * (0.16 + index * 0.008) + index * 1.37;
    let x = 12 + lane * 36 + Math.sin(phase * 1.17) * (13 + index * 0.7);
    let y = 24 + row * 45 + Math.cos(phase * 0.91 + index) * (15 + (index % 2) * 5);

    if (fae === "SYLPH") x += Math.sin(phase * 2.2) * 8;
    if (fae === "NYX") y = 78 + Math.sin(phase * 0.55) * 10;
    if (fae === "LUMA") y -= 6;

    x = clamp(x, 6, 91);
    y = clamp(y, 8, 88);
    node.style.left = `${x}%`;
    node.style.top = `${y}%`;
    node.style.setProperty("--tilt", `${Math.sin(phase) * 8}deg`);
    node.classList.toggle("active", fae === activeFae);
  });
}

function speak(fae, text) {
  const node = spirits.get(fae);
  if (!node) return;
  const bubble = node.querySelector(".speech");
  bubble.textContent = String(text || "").slice(0, 64);
  node.classList.remove("speaking");
  void node.offsetWidth;
  node.classList.add("speaking");
}

function summon(fae, message = "") {
  if (!MEMBERS[fae]) return;
  activeFae = fae;
  activeMessage = message || `${fae} manifested.`;
  const node = spirits.get(fae);
  if (node) {
    node.classList.remove("summoned");
    void node.offsetWidth;
    node.classList.add("summoned");
    speak(fae, activeMessage);
  }
  const wave = document.querySelector(".summon-wave");
  if (wave) {
    wave.style.setProperty("--member", MEMBERS[fae].color);
    wave.classList.remove("fire");
    void wave.offsetWidth;
    wave.classList.add("fire");
  }
  positionSpirits();
}

async function pullState() {
  try {
    const response = await fetch(STATE_ENDPOINT, { cache: "no-store" });
    if (!response.ok) return;
    const state = await response.json();
    if (MEMBERS[state.fae]) {
      if (state.fae !== activeFae || (state.message && state.message !== activeMessage)) {
        summon(state.fae, state.message || state.state || "Manifested");
      }
    }
  } catch {}
}

function ambientSpeech() {
  const fae = ORDER[speechIndex % ORDER.length];
  speechIndex += 1;
  const member = MEMBERS[fae];
  const stamp = member.stamps[(tick + speechIndex) % member.stamps.length];
  speak(fae, stamp);
}

await listen("fairyos://haunt", ({ payload }) => {
  if (!payload || !MEMBERS[payload.fae]) return;
  summon(payload.fae, payload.message || payload.state || "Manifested");
});

positionSpirits();
setInterval(() => { tick += 1; positionSpirits(); }, 1400);
setInterval(ambientSpeech, 7600);
setInterval(pullState, 2200);
setTimeout(() => summon("KYU", "Desktop colony online."), 650);
