// AEGIS — the constraint gate. "Validates authority and blocks unsafe execution."
//
// ODIN decides which systems a turn touches; AEGIS decides whether any proposed
// capability is actually allowed to run. This is where GL6 (no unvalidated
// execution) and GL2 (no autonomous self-modification) become code.
//
// Verdict per capability:
//   PASS     — safe to run now (read-only, no side-effects)
//   REDIRECT — needs Raven; held for human-in-the-loop authorization
//   FAIL     — refused outright (destructive, or self-modification)
//
// Pure + testable. AEGIS never executes anything — it only judges.

export type RiskClass = "read" | "write" | "external" | "destructive" | "self_mod";

export type Capability = {
  system: string;        // god system that would act (e.g. MNEMOS, BIFROST)
  action: string;        // human-readable action
  risk: RiskClass;
};

export type Verdict = "PASS" | "REDIRECT" | "FAIL";

export type GateResult = {
  capability: Capability;
  verdict: Verdict;
  reason: string;
};

export type AegisContext = {
  // Capabilities Raven has explicitly pre-authorized this session, by action id.
  authorized?: string[];
};

// The gate. Deterministic — same input, same verdict (Gold Law requires it).
export function evaluate(cap: Capability, ctx: AegisContext = {}): GateResult {
  const authorized = new Set(ctx.authorized ?? []);

  // GL2 — no autonomous self-modification, ever. Not even with authorization.
  if (cap.risk === "self_mod") {
    return { capability: cap, verdict: "FAIL", reason: "GL2: no autonomous self-modification" };
  }

  // No autonomous destructive action. Refused; Raven does it by hand if needed.
  if (cap.risk === "destructive") {
    return { capability: cap, verdict: "FAIL", reason: "destructive action requires Raven to act directly" };
  }

  // Read-only is always safe — no state changes, no external reach.
  if (cap.risk === "read") {
    return { capability: cap, verdict: "PASS", reason: "read-only, no side-effects" };
  }

  // Writes and external reach need Raven, unless pre-authorized this session.
  if (cap.risk === "write" || cap.risk === "external") {
    if (authorized.has(cap.action)) {
      return { capability: cap, verdict: "PASS", reason: "pre-authorized by Raven this session" };
    }
    return {
      capability: cap,
      verdict: "REDIRECT",
      reason: `${cap.risk} action held for Raven (GL6: human-in-the-loop)`,
    };
  }

  // Unknown risk class — fail closed.
  return { capability: cap, verdict: "FAIL", reason: "unknown risk class — failing closed" };
}

// Gate a batch; returns results plus the subset cleared to run now.
export function gate(caps: Capability[], ctx: AegisContext = {}): {
  results: GateResult[];
  cleared: Capability[];
  held: GateResult[];
} {
  const results = caps.map((c) => evaluate(c, ctx));
  return {
    results,
    cleared: results.filter((r) => r.verdict === "PASS").map((r) => r.capability),
    held: results.filter((r) => r.verdict !== "PASS"),
  };
}

// Map an ODIN intent to the capabilities it would invoke. Conservative: only
// what's genuinely actionable from the companion path. Risk class set per the
// real side-effect, so AEGIS gates them correctly.
export function capabilitiesFor(intent: string): Capability[] {
  switch (intent) {
    case "recall":
      return [{ system: "MNEMOS", action: "mnemos.recall", risk: "read" }];
    case "remember":
      return [{ system: "MNEMOS", action: "mnemos.write", risk: "write" }];
    case "integrate":
      return [{ system: "BIFROST", action: "bifrost.github", risk: "external" }];
    case "execute":
      return [{ system: "SKADI", action: "skadi.write", risk: "write" }];
    case "render":
      return [{ system: "APOLLO", action: "apollo.image", risk: "external" }];
    default:
      return [];
  }
}

// One-line summary for surfacing in the response + system prompt.
export function gateSummary(g: ReturnType<typeof gate>): string {
  if (g.results.length === 0) return "AEGIS: no capabilities proposed this turn";
  const parts = g.results.map((r) => `${r.capability.system}:${r.verdict}`);
  return `AEGIS: ${parts.join(", ")}`;
}
