// ODIN — intent router for the JARVIS companion path.
//
// Raven's directive: what we say or do should trigger the right god system,
// not a fixed pipeline. This is ODIN's contract — "determines which systems
// handle each task." It reads an incoming SPEAK and returns a routing decision:
// the canonical spine plus the intent-specific systems that should light up.
//
// Boundary (GL6): ODIN DECIDES and SURFACES. It does not execute side-effects.
// SKADI (gated by AEGIS) is the only thing that runs actions. Keeping routing
// pure means it stays testable and can't mutate state on its own.
//
// Grounded in the 27 god systems (god_systems/, P26 Canon). Do not redefine.

export type Tier =
  | "FOUNDATIONAL" | "EXECUTION" | "TIMING" | "MEMORY"
  | "OBSERVABILITY" | "GOVERNANCE" | "INTEGRITY" | "INTERFACE"
  | "INFRASTRUCTURE" | "TRANSLATION" | "GUARDIAN";

export type Trigger = { system: string; reason: string };

export type RoutingDecision = {
  intent: string;
  spine: string[];          // always-on canonical path for this turn
  triggered: Trigger[];     // intent-specific systems that fired
  primary: string;          // the headline system for this turn
};

// Canonical function note per system — used as the "reason" when a rule fires.
const FN: Record<string, string> = {
  AYRE: "intake + intent parse",
  AEGIS: "Gold Law / authority gate",
  ODIN: "orchestration routing",
  SKADI: "execution runtime",
  KRONOS: "scheduling / sequencing",
  MNEMOS: "persistent semantic memory",
  MIMIR: "contextual knowledge access",
  HUGINN: "cross-session reconciliation",
  HALO: "ambient monitoring",
  ATHENA: "strategic planning",
  MERIDIAN: "alignment enforcement",
  PROMETHEUS: "expansion rationale ledger",
  NEMESIS: "drift / overlap detection",
  ARGUS: "comprehensive surveillance",
  BIFROST: "external relay / transport",
  ATLAS: "infrastructure",
  APOLLO: "output formatting + delivery",
  DANTE: "interface surface",
  JANUS: "mode transition / handoff",
  HERMES: "translation",
  ZEUS: "supreme authority arbitration",
  HADES: "archival sink",
  ERIS: "entropy guardian (always active)",
};

// Intent rules. First matching rule sets the intent + primary; multiple rules
// may contribute triggered systems. Order matters: most specific first.
type Rule = {
  intent: string;
  test: RegExp;
  primary: string;
  systems: string[];
};

const RULES: Rule[] = [
  // Expansion / new capability — must route through the GL7 ledger.
  {
    intent: "expansion",
    test: /\b(add|new|expand|introduce|create)\b.*\b(system|feature|capability|module|god\s*system|tool)\b/i,
    primary: "PROMETHEUS",
    systems: ["PROMETHEUS", "NEMESIS", "AEGIS"],
  },
  // Memory / recall.
  {
    intent: "recall",
    test: /\b(remember|recall|what did|last time|history|earlier|previously|forget|memory|mnemos)\b/i,
    primary: "MNEMOS",
    systems: ["MNEMOS", "MIMIR", "HUGINN"],
  },
  // Build / execute / ship.
  {
    intent: "execute",
    test: /\b(build|implement|run|ship|fix|carve|refactor|push|commit|extract|wire)\b/i,
    primary: "SKADI",
    systems: ["ODIN", "AEGIS", "KRONOS", "SKADI"],
  },
  // Audit / review / governance check.
  {
    intent: "audit",
    test: /\b(audit|review|check|inspect|drift|overlap|verify|validate|lint|test)\b/i,
    primary: "NEMESIS",
    systems: ["ARGUS", "NEMESIS", "HUGINN", "AEGIS"],
  },
  // Plan / design / architecture / strategy.
  {
    intent: "plan",
    test: /\b(plan|design|architect|architecture|strategy|approach|roadmap|should we|how do we)\b/i,
    primary: "ATHENA",
    systems: ["ATHENA", "MERIDIAN", "MIMIR"],
  },
  // External integration.
  {
    intent: "integrate",
    test: /\b(github|supabase|edge function|api|webhook|deploy|external|relay|fetch|http)\b/i,
    primary: "BIFROST",
    systems: ["BIFROST", "ATLAS", "AEGIS"],
  },
  // Image / visual render.
  {
    intent: "render",
    test: /\b(image|render|concept card|picture|draw|visual|art|generate.*image)\b/i,
    primary: "APOLLO",
    systems: ["APOLLO", "SKADI"],
  },
  // Decision / authority.
  {
    intent: "decide",
    test: /\b(decide|decision|approve|reject|authori[sz]e|commit to|go ahead|sign off)\b/i,
    primary: "AEGIS",
    systems: ["AEGIS", "ATHENA", "ZEUS"],
  },
  // Personal / companion — no god-system execution, ambient presence only.
  {
    intent: "companion",
    test: /\b(tired|stressed|scared|alone|struggle|hard|worried|hope|proud|thank you|love)\b/i,
    primary: "HALO",
    systems: ["HALO"],
  },
];

// AYRE always parses intake; ERIS is always-active guardian. Every turn gets
// MNEMOS at the tail (the exchange is consolidated to memory downstream).
const SPINE_HEAD = ["AYRE"];
const SPINE_GUARDIAN = "ERIS";

// Forbidden edges (P26): never present these as a direct hop in one decision.
const FORBIDDEN: ReadonlyArray<readonly [string, string]> = [
  ["SKADI", "AEGIS"], ["DANTE", "SKADI"], ["JANUS", "SKADI"], ["LOKI", "HADES"],
];

// Order systems so no forbidden edge appears as an adjacent hop. We anchor on
// canonical precedence: gates/routers before runtime. AEGIS must precede SKADI.
function orderSystems(systems: string[]): string[] {
  const rank: Record<string, number> = {
    AEGIS: 0, ODIN: 1, KRONOS: 2, ATHENA: 1, MERIDIAN: 1, PROMETHEUS: 0,
    BIFROST: 1, ATLAS: 1, MNEMOS: 1, MIMIR: 1, ARGUS: 1, NEMESIS: 1,
    SKADI: 3, APOLLO: 4, HUGINN: 5, HALO: 1, ZEUS: 0,
  };
  const uniq = [...new Set(systems)];
  return uniq.sort((a, b) => (rank[a] ?? 2) - (rank[b] ?? 2));
}

export function hasForbiddenHop(seq: string[]): boolean {
  for (let i = 0; i < seq.length - 1; i++) {
    for (const [a, b] of FORBIDDEN) {
      if (seq[i] === a && seq[i + 1] === b) return true;
    }
  }
  return false;
}

export function route(input: string): RoutingDecision {
  const text = input ?? "";
  const matched = RULES.filter((r) => r.test.test(text));

  // Default: pure conversation → AYRE intake, ambient HALO, MNEMOS tail.
  if (matched.length === 0) {
    return {
      intent: "converse",
      spine: [...SPINE_HEAD, SPINE_GUARDIAN, "MNEMOS"],
      triggered: [{ system: "HALO", reason: FN.HALO }],
      primary: "HALO",
    };
  }

  const primary = matched[0].primary;
  const intent = matched[0].intent;
  const systemSet = orderSystems(matched.flatMap((r) => r.systems));
  const triggered: Trigger[] = systemSet.map((s) => ({ system: s, reason: FN[s] ?? "system" }));

  return {
    intent,
    spine: [...SPINE_HEAD, SPINE_GUARDIAN, ...systemSet, "MNEMOS"],
    triggered,
    primary,
  };
}

// One-line summary for surfacing in the response + system prompt.
export function routeSummary(d: RoutingDecision): string {
  const names = d.triggered.map((t) => t.system).join(" + ");
  return `intent=${d.intent} → ${names || "none"} (primary ${d.primary})`;
}
