// SKADI — execution planning for the companion reflex arc.
//
// Stage 2: closing the loop. ODIN routes, AEGIS gates, and now a *cleared*
// capability actually runs. This module holds the pure planning + extraction
// logic; the side-effect itself (writing to MNEMOS) lives in index.ts, behind
// AEGIS clearance. SKADI never decides whether it's allowed — AEGIS already did.
//
// Governance: only AEGIS-cleared capabilities reach execution. A held capability
// produces a "held" plan, surfaced to Raven, and nothing runs.

import type { Capability, GateResult } from "./aegis.ts";

export type ExecStatus = "done" | "held" | "failed" | "noop";

export type ExecPlan = {
  action: string;        // capability action id (e.g. mnemos.write)
  status: ExecStatus;    // outcome class — set to "done" only after the I/O succeeds
  detail: string;        // human-readable note for the response / system prompt
  payload?: Record<string, unknown>; // data the handler needs to perform the effect
};

// Strip the imperative prefix off a "remember that ..." turn to get the fact
// worth committing. Pure + testable.
export function extractFact(input: string): string {
  return (input ?? "")
    .replace(/^\s*(please\s+)?(remember|note|log|store|commit)\b\s*(that|this|to memory)?\s*[:,-]?\s*/i, "")
    .trim();
}

// Plan executions for the AEGIS-cleared capabilities of this turn. Cleared
// capabilities get a concrete plan; everything else is reported as held so the
// handler can run only what passed. Pure — no side-effects here.
export function planExecutions(
  intent: string,
  gate: { cleared: Capability[]; held: GateResult[] },
  input: string,
): ExecPlan[] {
  const plans: ExecPlan[] = [];

  for (const cap of gate.cleared) {
    if (cap.action === "mnemos.write") {
      const fact = extractFact(input);
      if (!fact) {
        plans.push({ action: cap.action, status: "noop", detail: "nothing to store — empty fact" });
      } else {
        plans.push({
          action: cap.action,
          status: "done",            // optimistic; handler downgrades to "failed" on I/O error
          detail: `committing to memory: "${fact.slice(0, 80)}"`,
          payload: { text: fact, source_type: "raven_directive", tags: ["directive", intent] },
        });
      }
    } else {
      // Cleared but not yet wired to an effect (e.g. bifrost.github needs a token).
      plans.push({ action: cap.action, status: "noop", detail: `${cap.action} cleared but not wired yet` });
    }
  }

  for (const h of gate.held) {
    plans.push({ action: h.capability.action, status: "held", detail: h.reason });
  }

  return plans;
}

export function execSummary(plans: ExecPlan[]): string {
  if (plans.length === 0) return "SKADI: nothing to execute this turn";
  return "SKADI: " + plans.map((p) => `${p.action}:${p.status}`).join(", ");
}
