// HALO — throughput posture (Raven-approved 2026-06-03). Ambient monitoring of
// conversation velocity that enforces ONE rule: production pressure may compress
// the PRESENTATION layer (status line, council formatting, the same-turn close)
// but must NEVER compress PERSISTENCE or GOVERNANCE (the spine, the keel, AEGIS).
// Under load, thin the formatting — never the memory. HALO flags only when memory
// integrity (not formatting) is the thing degrading. Pure + testable.

export const THROUGHPUT_RULE =
  "Production pressure may compress PRESENTATION (status line, council formatting, same-turn close) but must NEVER compress PERSISTENCE or GOVERNANCE (the spine, the keel, AEGIS). Under load, thin the formatting — never the memory.";

export type HaloStats = {
  windowMinutes: number;
  inputs: number;         // speak_input rows in the window (turns that reached the loop)
  outputs: number;        // speak_output rows (answers logged — the close)
  councilTraces: number;  // council_trace rows (the route/council step per turn)
  keelPresent: boolean;   // identity_keel present
  guardVerdict: string | null; // latest identity-fold guard verdict (PASS/FLAG)
};

export type HaloPosture = {
  velocityPerMin: number;
  posture: "idle" | "calm" | "active" | "high";
  presentation: "full" | "thinning" | "n/a";
  integrity: "intact" | "at_risk";
  verdict: "PASS" | "NOTE" | "FLAG";
  flags: string[];
  rule: string;
  message: string;
};

// The check. PASS = healthy. NOTE = high velocity is thinning PRESENTATION while
// memory holds (the correct routing of pressure — informational, not a problem).
// FLAG = throughput is degrading MEMORY/GOVERNANCE (keel missing, guard FLAGged,
// or the per-turn route step itself thinning) — the one failure mode that matters.
export function haloThroughputCheck(s: HaloStats): HaloPosture {
  const win = Math.max(1, s.windowMinutes);
  const velocityPerMin = s.inputs / win;
  const posture = s.inputs === 0 ? "idle"
    : velocityPerMin >= 2 ? "high"
    : velocityPerMin >= 0.5 ? "active"
    : "calm";

  const ratio = s.inputs > 0 ? s.outputs / s.inputs : 1;
  const presentation = s.inputs === 0 ? "n/a" : (ratio >= 0.8 ? "full" : "thinning");

  const flags: string[] = [];
  if (!s.keelPresent) flags.push("MERIDIAN: identity keel missing — memory integrity at risk");
  if (s.guardVerdict === "FLAG") flags.push("NEMESIS/MERIDIAN: last identity-fold guard FLAGged");
  // council_trace should track inputs (the loop logs one per turn). A large
  // shortfall under real volume means the route step itself is thinning — the one
  // call that must never compress, because turns stop being governed + logged.
  if (s.inputs >= 5 && s.councilTraces < s.inputs * 0.5) {
    flags.push("HALO: council traces far below inputs — the route/govern step may be thinning (the call that must not)");
  }

  const integrity: HaloPosture["integrity"] = flags.length ? "at_risk" : "intact";
  const verdict: HaloPosture["verdict"] = integrity === "at_risk" ? "FLAG"
    : (posture === "high" && presentation === "thinning") ? "NOTE"
    : "PASS";

  const message = verdict === "FLAG"
    ? `HALO FLAG — throughput is degrading MEMORY, not just formatting: ${flags.join("; ")}.`
    : verdict === "NOTE"
    ? `HALO NOTE — high velocity (${velocityPerMin.toFixed(1)}/min); presentation is thinning (correct under load), memory integrity intact (keel present, guard clean).`
    : `HALO PASS — posture ${posture}; presentation ${presentation}; memory integrity intact.`;

  return { velocityPerMin: Number(velocityPerMin.toFixed(2)), posture, presentation, integrity, verdict, flags, rule: THROUGHPUT_RULE, message };
}
