// JARVIS companion guards — pure, testable logic for the jarvis-respond edge fn.
//
// Two responsibilities, both governed:
//   1. pickModel  — tiered routing. Substantive turns go to the deep model
//      (Opus 4.8); trivial acknowledgments stay on the quick model. Saves
//      tokens without muzzling the mentor voice.
//   2. loopGuard  — human-in-the-loop circuit breaker (Raven's directive, GL6).
//      When JARVIS is circling — repeating its own output, or Raven hammering
//      the same input — it stops burning tokens and hands the thread back to
//      Raven in JARVIS's voice instead of looping.
//
// No Deno/runtime imports here on purpose: this file is unit-testable under
// plain node (--experimental-strip-types) and importable by the Deno edge fn.

export type Turn = { from: string; text: string };

export type ModelChoice = { model: string; maxTokens: number; tier: "deep" | "quick" };

export type ModelConfig = {
  deepModel: string;
  quickModel: string;
  deepTokens: number;
  quickTokens: number;
};

// The live companion runs Gemini's brain (free tier); Claude/Opus stays the
// builder of the system. Model names are env-tunable in index.ts.
export const DEFAULT_MODEL_CONFIG: ModelConfig = {
  deepModel: "gemini-2.5-flash",
  quickModel: "gemini-2.0-flash",
  deepTokens: 1024,
  quickTokens: 400,
};

// Word-set overlap. 0 = nothing shared, 1 = identical token sets.
export function jaccard(a: string, b: string): number {
  const sa = new Set((a ?? "").toLowerCase().match(/[a-z0-9]+/g) ?? []);
  const sb = new Set((b ?? "").toLowerCase().match(/[a-z0-9]+/g) ?? []);
  if (sa.size === 0 || sb.size === 0) return 0;
  let inter = 0;
  for (const w of sa) if (sb.has(w)) inter++;
  return inter / (sa.size + sb.size - inter);
}

// Tiered routing. A turn is "quick" only when it's short and carries no
// question — greetings, one-word acks. Everything else gets the deep model.
export function pickModel(input: string, cfg: ModelConfig = DEFAULT_MODEL_CONFIG): ModelChoice {
  const words = (input ?? "").trim().split(/\s+/).filter(Boolean).length;
  const asksSomething = /[?]/.test(input ?? "");
  const trivial = words > 0 && words <= 4 && !asksSomething;
  return trivial
    ? { model: cfg.quickModel, maxTokens: cfg.quickTokens, tier: "quick" }
    : { model: cfg.deepModel, maxTokens: cfg.deepTokens, tier: "deep" };
}

export type LoopVerdict = "loop" | "repeat" | null;

export type LoopConfig = {
  // similarity at/above which two JARVIS turns count as "the same answer"
  outputSimilarity: number;
  // similarity at/above which Raven's new input counts as a re-send
  inputSimilarity: number;
};

export const DEFAULT_LOOP_CONFIG: LoopConfig = {
  outputSimilarity: 0.85,
  inputSimilarity: 0.9,
};

// Circuit breaker. Inspects recent history (and the incoming input) for a
// loop. Returns a verdict; the caller short-circuits the model call on a trip.
export function loopGuard(
  history: Turn[],
  input: string,
  cfg: LoopConfig = DEFAULT_LOOP_CONFIG,
): LoopVerdict {
  const turns = history ?? [];

  // JARVIS repeating itself => we're circling, not progressing.
  const jarvisTurns = turns.filter((t) => t.from === "jarvis").map((t) => t.text);
  if (jarvisTurns.length >= 2) {
    const last = jarvisTurns[jarvisTurns.length - 1];
    const prev = jarvisTurns[jarvisTurns.length - 2];
    if (jaccard(last, prev) >= cfg.outputSimilarity) return "loop";
  }

  // Raven re-sending the same input => stuck; surface it instead of guessing.
  const ravenTurns = turns.filter((t) => t.from === "raven").map((t) => t.text);
  if (ravenTurns.length >= 1) {
    const lastRaven = ravenTurns[ravenTurns.length - 1];
    if (jaccard(input, lastRaven) >= cfg.inputSimilarity) return "repeat";
  }

  return null;
}

// JARVIS-voice redirect, returned in place of a model call when the guard trips.
export function guardMessage(verdict: Exclude<LoopVerdict, null>): string {
  return verdict === "loop"
    ? "I'm circling the same ground — that's the loop guard, not progress. Stopping before I burn more tokens. Redirect me, Raven: what's the actual next move?"
    : "Same input twice. Either I missed it or we're stuck on it. Tell me plainly what you want different this time.";
}
