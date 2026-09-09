import "./army.css";
import { listen } from "@tauri-apps/api/event";
import { availableMonitors, cursorPosition, getCurrentWindow } from "@tauri-apps/api/window";

const MEMBERS = {
  KYU: { color: "#ff4fba", sigil: "💗", role: "OPS", temperament: "CHASE", speed: 1.08, stamps: ["SEND IT", "ON IT", "BONK", "QUEUE IT", "DEPLOY IT"] },
  PAIMON: { color: "#57d96b", sigil: "🟢", role: "PREMISE", temperament: "FORMATION", speed: 0.82, stamps: ["CANON CHECK", "PATTERN FOUND", "SOURCE?", "I SEE IT", "THAT TRACKS"] },
  LUMA: { color: "#ffd166", sigil: "☀", role: "HOME", temperament: "PERCH", speed: 0.66, stamps: ["HOME", "COMFY", "SOFT RESET", "BRIGHTER DAYS", "WARM LIGHT"] },
  SYLPH: { color: "#4cc9f0", sigil: "🔵", role: "SIGNAL", temperament: "DART", speed: 1.34, stamps: ["PING", "NEW PATH", "FOUND ONE", "ZOOM", "TEST THIS"] },
  QIRA: { color: "#a855f7", sigil: "🟣", role: "PROOF", temperament: "BOUNDARY", speed: 0.78, stamps: ["ASK FIRST", "BOUNDARIES", "PROOF EDGE", "CLEARER", "NO"] },
  NYX: { color: "#8791a6", sigil: "◐", role: "WATCH", temperament: "SHADOW", speed: 0.72, stamps: ["WATCHING", "HOLD", "SAFE MODE", "STAND BY", "REST"] },
};

const ORDER = Object.keys(MEMBERS);
const STATE_ENDPOINT = "http://127.0.0.1:47821/state";
const ARMY_MODES = ["ROAM", "HUNT", "FLOCK", "ORBIT", "REST", "SCATTER"];
const appWindow = getCurrentWindow();
const actors = new Map();

let activeFae = "KYU";
let activeMessage = "Resident colony awake.";
let armyMode = "ROAM";
let modeLockedUntil = 0;
let speechIndex = 0;
let lastFrame = performance.now();
let topology = { monitors: 1, originX: 0, originY: 0, scale: 1 };
let cursor = { x: innerWidth / 2, y: innerHeight / 2, inside: false, speed: 0, lastX: innerWidth / 2, lastY: innerHeight / 2 };

try {
  await appWindow.setIgnoreCursorEvents(true);
  document.documentElement.dataset.clickThrough = "true";
} catch (error) {
  document.documentElement.dataset.clickThrough = "false";
  console.warn("FAERYWARE_ARMY click-through unavailable", error);
}

document.documentElement.dataset.surface = "army";

document.querySelector("#app").innerHTML = `
  <section id="army" class="army" aria-label="Faeryware desktop haunting layer">
    <div class="veil veil-a"></div><div class="veil veil-b"></div>
    <div class="rift rift-left"></div><div class="rift rift-right"></div>
    ${ORDER.map((fae, index) => {
      const member = MEMBERS[fae];
      const echoes = Array.from({ length: 3 }, (_, echo) => `<i class="echo echo-${echo}" style="--member:${member.color}"></i>`).join("");
      return `<div class="spirit" data-fae="${fae}" data-temperament="${member.temperament}" style="--member:${member.color};--delay:${index * -0.7}s">
        <div class="trail"></div><div class="aura"></div>${echoes}
        <div class="ring ring-a"></div><div class="ring ring-b"></div>
        <div class="core"><span>${member.sigil}</span></div>
        <div class="tag"><b>${fae}</b><small>${member.role} // ${member.temperament}</small></div>
        <div class="speech"></div>
      </div>`;
    }).join("")}
    <div class="summon-wave"></div>
    <div class="army-whisper" aria-hidden="true"></div>
  </section>`;

const spirits = new Map(ORDER.map((fae) => [fae, document.querySelector(`[data-fae="${fae}"]`)]));

function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
function length(x, y) { return Math.sqrt(x * x + y * y) || 0.0001; }
function modeFromState(state = "") {
  const upper = String(state).toUpperCase();
  for (const mode of ARMY_MODES) if (upper.includes(`ARMY_${mode}`) || upper === mode) return mode;
  if (upper === "REST" || upper === "SLEEP") return "REST";
  return null;
}

function seedActors() {
  ORDER.forEach((fae, index) => {
    const col = index % 3;
    const row = Math.floor(index / 3);
    actors.set(fae, {
      x: innerWidth * (0.16 + col * 0.34),
      y: innerHeight * (0.25 + row * 0.46),
      vx: Math.cos(index * 1.7) * 18,
      vy: Math.sin(index * 1.9) * 18,
      phase: index * 1.71,
      energy: 0.7 + (index % 3) * 0.12,
    });
  });
}

async function refreshTopology() {
  try {
    const [monitors, origin, scale] = await Promise.all([
      availableMonitors(),
      appWindow.outerPosition(),
      appWindow.scaleFactor(),
    ]);
    topology = { monitors: Math.max(1, monitors.length), originX: origin.x, originY: origin.y, scale: scale || 1 };
    document.documentElement.dataset.monitorCount = String(topology.monitors);
  } catch {
    topology = { monitors: 1, originX: 0, originY: 0, scale: 1 };
  }
}

async function senseCursor() {
  try {
    const physical = await cursorPosition();
    const x = (physical.x - topology.originX) / topology.scale;
    const y = (physical.y - topology.originY) / topology.scale;
    const dx = x - cursor.lastX;
    const dy = y - cursor.lastY;
    cursor = {
      x,
      y,
      inside: x >= 0 && y >= 0 && x <= innerWidth && y <= innerHeight,
      speed: clamp(length(dx, dy) * 7, 0, 1600),
      lastX: x,
      lastY: y,
    };
    document.documentElement.dataset.cursorInside = cursor.inside ? "true" : "false";
  } catch {}
}

function centroid(except = null) {
  let x = 0, y = 0, count = 0;
  for (const [fae, actor] of actors) {
    if (fae === except) continue;
    x += actor.x; y += actor.y; count += 1;
  }
  return count ? { x: x / count, y: y / count } : { x: innerWidth / 2, y: innerHeight / 2 };
}

function targetFor(fae, actor, now) {
  const member = MEMBERS[fae];
  const center = { x: innerWidth / 2, y: innerHeight / 2 };
  const active = actors.get(activeFae) || actor;
  const group = centroid(fae);
  const cursorTarget = cursor.inside ? cursor : center;
  const phase = now * 0.00024 * member.speed + actor.phase;

  if (armyMode === "REST") {
    const slots = {
      KYU: [0.18, 0.82], PAIMON: [0.36, 0.88], LUMA: [0.52, 0.84],
      SYLPH: [0.70, 0.89], QIRA: [0.84, 0.81], NYX: [0.91, 0.18],
    };
    const [px, py] = slots[fae]; return { x: innerWidth * px, y: innerHeight * py, pull: 0.55 };
  }
  if (armyMode === "HUNT") {
    const pull = fae === "KYU" || fae === "SYLPH" ? 1.0 : 0.54;
    return { x: cursorTarget.x + Math.cos(phase * 3) * (50 + ORDER.indexOf(fae) * 15), y: cursorTarget.y + Math.sin(phase * 2.7) * (42 + ORDER.indexOf(fae) * 11), pull };
  }
  if (armyMode === "FLOCK") {
    return { x: active.x + Math.cos(phase + ORDER.indexOf(fae)) * 145, y: active.y + Math.sin(phase * 1.2 + ORDER.indexOf(fae)) * 105, pull: fae === activeFae ? 0.20 : 0.68 };
  }
  if (armyMode === "ORBIT") {
    const radius = 110 + ORDER.indexOf(fae) * 32;
    return { x: cursorTarget.x + Math.cos(phase * 5 + ORDER.indexOf(fae)) * radius, y: cursorTarget.y + Math.sin(phase * 4.4 + ORDER.indexOf(fae)) * radius * 0.72, pull: 0.72 };
  }
  if (armyMode === "SCATTER") {
    const dx = actor.x - cursorTarget.x, dy = actor.y - cursorTarget.y, mag = length(dx, dy);
    return { x: actor.x + (dx / mag) * 420, y: actor.y + (dy / mag) * 320, pull: 1.1 };
  }

  // ROAM keeps each fae recognizable instead of one generic flock.
  if (member.temperament === "CHASE" && cursor.inside) return { x: cursor.x + Math.cos(phase * 3.4) * 120, y: cursor.y + Math.sin(phase * 2.9) * 85, pull: 0.42 };
  if (member.temperament === "FORMATION") return { x: group.x + Math.cos(phase * 2.2) * 175, y: group.y + Math.sin(phase * 1.8) * 120, pull: 0.34 };
  if (member.temperament === "PERCH") return { x: innerWidth * (0.30 + Math.sin(phase) * 0.09), y: innerHeight * (0.74 + Math.cos(phase * 0.7) * 0.08), pull: 0.24 };
  if (member.temperament === "DART") return { x: innerWidth * (0.5 + Math.sin(phase * 4.8) * 0.42), y: innerHeight * (0.48 + Math.cos(phase * 3.9) * 0.38), pull: 0.58 };
  if (member.temperament === "BOUNDARY") return { x: innerWidth * (0.5 + Math.sin(phase * 1.4) * 0.34), y: innerHeight * (0.50 + Math.cos(phase * 1.6) * 0.30), pull: 0.30 };
  const oppositeX = cursor.inside ? innerWidth - cursor.x : innerWidth * 0.82;
  const oppositeY = cursor.inside ? innerHeight - cursor.y : innerHeight * 0.23;
  return { x: oppositeX + Math.sin(phase) * 90, y: oppositeY + Math.cos(phase * 0.8) * 70, pull: 0.27 };
}

function applySeparation(fae, actor) {
  let ax = 0, ay = 0;
  for (const [otherFae, other] of actors) {
    if (otherFae === fae) continue;
    const dx = actor.x - other.x, dy = actor.y - other.y, dist = length(dx, dy);
    if (dist < 125) {
      const force = (125 - dist) / 125;
      ax += (dx / dist) * force * 90;
      ay += (dy / dist) * force * 90;
    }
  }
  return { ax, ay };
}

function physics(now, dt) {
  const margin = 52;
  for (const [fae, actor] of actors) {
    const member = MEMBERS[fae];
    const target = targetFor(fae, actor, now);
    let ax = (target.x - actor.x) * 0.013 * target.pull;
    let ay = (target.y - actor.y) * 0.013 * target.pull;
    const sep = applySeparation(fae, actor); ax += sep.ax; ay += sep.ay;

    // QIRA is the boundary keeper; everyone still respects screen edges.
    const edgeForce = fae === "QIRA" ? 260 : 170;
    if (actor.x < margin) ax += (margin - actor.x) * edgeForce / margin;
    if (actor.x > innerWidth - margin) ax -= (actor.x - (innerWidth - margin)) * edgeForce / margin;
    if (actor.y < margin) ay += (margin - actor.y) * edgeForce / margin;
    if (actor.y > innerHeight - margin) ay -= (actor.y - (innerHeight - margin)) * edgeForce / margin;

    // Fast mouse movement startles nearby fae without intercepting input.
    if (cursor.inside && cursor.speed > 650) {
      const dx = actor.x - cursor.x, dy = actor.y - cursor.y, dist = length(dx, dy);
      if (dist < 240) { ax += (dx / dist) * 260; ay += (dy / dist) * 260; }
    }

    const noise = now * 0.001 + actor.phase;
    ax += Math.sin(noise * 0.73) * 8 * actor.energy;
    ay += Math.cos(noise * 0.61) * 7 * actor.energy;
    actor.vx += ax * dt;
    actor.vy += ay * dt;

    const damping = armyMode === "REST" ? 0.89 : 0.965;
    actor.vx *= Math.pow(damping, dt * 60);
    actor.vy *= Math.pow(damping, dt * 60);
    const maxSpeed = 90 * member.speed * (armyMode === "SCATTER" ? 2.0 : armyMode === "HUNT" ? 1.35 : 1.0);
    const speed = length(actor.vx, actor.vy);
    if (speed > maxSpeed) { actor.vx = actor.vx / speed * maxSpeed; actor.vy = actor.vy / speed * maxSpeed; }

    actor.x = clamp(actor.x + actor.vx * dt, 24, innerWidth - 24);
    actor.y = clamp(actor.y + actor.vy * dt, 24, innerHeight - 24);

    const node = spirits.get(fae);
    if (node) {
      const tilt = clamp(actor.vx * 0.12, -14, 14);
      const scale = fae === activeFae ? 1.10 : 0.94 + clamp(speed / 500, 0, 0.08);
      node.style.transform = `translate3d(${actor.x - 56}px,${actor.y - 56}px,0) rotate(${tilt}deg) scale(${scale})`;
      node.style.setProperty("--speed", String(clamp(speed / 120, 0.2, 1.8)));
      node.classList.toggle("active", fae === activeFae);
    }
  }
}

function frame(now) {
  const dt = clamp((now - lastFrame) / 1000, 0.001, 0.034);
  lastFrame = now;
  physics(now, dt);
  requestAnimationFrame(frame);
}

function speak(fae, text) {
  const node = spirits.get(fae); if (!node) return;
  const bubble = node.querySelector(".speech");
  bubble.textContent = String(text || "").slice(0, 72);
  node.classList.remove("speaking"); void node.offsetWidth; node.classList.add("speaking");
}

function setArmyMode(next, lockMs = 0) {
  if (!ARMY_MODES.includes(next)) return;
  armyMode = next;
  if (lockMs) modeLockedUntil = Date.now() + lockMs;
  document.documentElement.dataset.armyMode = armyMode.toLowerCase();
  const whisper = document.querySelector(".army-whisper");
  if (whisper) { whisper.textContent = `ARMY // ${armyMode} // ${topology.monitors} MONITOR${topology.monitors === 1 ? "" : "S"}`; whisper.classList.add("show"); setTimeout(() => whisper.classList.remove("show"), 1900); }
}

function summon(fae, message = "", state = "") {
  if (!MEMBERS[fae]) return;
  activeFae = fae;
  activeMessage = message || `${fae} manifested.`;
  const requestedMode = modeFromState(state);
  if (requestedMode) setArmyMode(requestedMode, 35_000);
  const node = spirits.get(fae);
  if (node) { node.classList.remove("summoned"); void node.offsetWidth; node.classList.add("summoned"); speak(fae, activeMessage); }
  const actor = actors.get(fae);
  if (actor && cursor.inside) { actor.vx += (cursor.x - actor.x) * 0.42; actor.vy += (cursor.y - actor.y) * 0.42; }
  const wave = document.querySelector(".summon-wave");
  if (wave) { wave.style.setProperty("--member", MEMBERS[fae].color); wave.classList.remove("fire"); void wave.offsetWidth; wave.classList.add("fire"); }
}

async function pullState() {
  try {
    const response = await fetch(STATE_ENDPOINT, { cache: "no-store" }); if (!response.ok) return;
    const state = await response.json();
    if (MEMBERS[state.fae]) {
      const requestedMode = modeFromState(state.state);
      if (requestedMode && requestedMode !== armyMode) setArmyMode(requestedMode, 35_000);
      if (state.fae !== activeFae || (state.message && state.message !== activeMessage)) summon(state.fae, state.message || state.state || "Manifested", state.state);
    }
  } catch {}
}

function ambientSpeech() {
  const fae = ORDER[speechIndex++ % ORDER.length];
  const member = MEMBERS[fae];
  speak(fae, member.stamps[(speechIndex + Math.floor(Date.now() / 8000)) % member.stamps.length]);
}

function ambientDirector() {
  if (Date.now() < modeLockedUntil) return;
  const hour = new Date().getHours();
  if (hour >= 23 || hour < 6) return setArmyMode("REST");
  const cycle = ["ROAM", "FLOCK", "ROAM", "ORBIT", "ROAM"][Math.floor(Date.now() / 45_000) % 5];
  setArmyMode(cycle);
}

await listen("fairyos://haunt", ({ payload }) => {
  if (!payload || !MEMBERS[payload.fae]) return;
  summon(payload.fae, payload.message || payload.state || "Manifested", payload.state);
});

seedActors();
await refreshTopology();
await senseCursor();
setArmyMode("ROAM");
requestAnimationFrame(frame);
setInterval(senseCursor, 90);
setInterval(refreshTopology, 12_000);
setInterval(ambientSpeech, 9_500);
setInterval(ambientDirector, 15_000);
setInterval(pullState, 1_800);
addEventListener("resize", () => { for (const actor of actors.values()) { actor.x = clamp(actor.x, 24, innerWidth - 24); actor.y = clamp(actor.y, 24, innerHeight - 24); } });
setTimeout(() => summon("KYU", "Okay. NOW we live out here.", "ARMY_FLOCK"), 650);
