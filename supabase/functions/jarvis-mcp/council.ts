// THE COUNCIL — JARVIS + the 27 God Systems as a fixed-authority body (Ayre Loop
// step 5). Pure + testable (node --experimental-strip-types). The council VOTES
// and is auditable; it does NOT re-weight itself. Authority is fixed by tier/role
// (the keel); only each member's accumulated record grows (the spine).

export const TIERS: Record<string, string[]> = {
  T0: ["CHAOS", "ZEUS", "POSEIDON", "HADES"],
  T1: ["AYRE", "AEGIS", "ODIN", "SKADI", "ERIS"],
  T2: ["KRONOS"],
  T3: ["MNEMOS", "HUGINN", "HALO", "MIMIR"],
  T4: ["BIFROST", "JANUS"],
  T5: ["LOKI", "ATHENA", "PROMETHEUS", "ARGUS", "NEMESIS"],
  T6: ["IRIS", "MERIDIAN"],
  T7: ["DANTE", "APOLLO"],
  T8: ["ATLAS"],
  T9: ["HERMES"],
};

// Fixed authority weight by tier. Foundational/sovereign + governance/integrity
// carry the most weight; interface/translation the least. NEVER learned — the keel.
export const TIER_WEIGHT: Record<string, number> = {
  T0: 1.0, T1: 0.9, T2: 0.7, T3: 0.8, T4: 0.6, T5: 0.85, T6: 0.85, T7: 0.5, T8: 0.6, T9: 0.5,
};

// Each member's fixed role (its domain in the council).
export const ROLE: Record<string, string> = {
  CHAOS: "foundational substrate", ZEUS: "supreme authority arbitration", POSEIDON: "foundational", HADES: "archival sink",
  AYRE: "intake + intent parse", AEGIS: "constraint / Gold Law gate", ODIN: "routing", SKADI: "execution runtime", ERIS: "entropy guardian",
  KRONOS: "timing / compression authority",
  MNEMOS: "memory store + recall", HUGINN: "synthesis / reconciliation", HALO: "ambient monitoring", MIMIR: "contextual knowledge",
  BIFROST: "external relay", JANUS: "mode transition",
  LOKI: "rollback", ATHENA: "strategic planning", PROMETHEUS: "expansion rationale ledger", ARGUS: "surveillance", NEMESIS: "drift / redundancy detection",
  IRIS: "integrity", MERIDIAN: "keel alignment",
  DANTE: "interface", APOLLO: "output formatting + delivery",
  ATLAS: "infrastructure", HERMES: "translation",
};

const SYSTEM_TIER: Record<string, string> = {};
for (const [tier, systems] of Object.entries(TIERS)) for (const s of systems) SYSTEM_TIER[s] = tier;

export type Member = { system: string; tier: string; weight: number; role: string };

export function memberProfile(system: string): Member {
  const tier = SYSTEM_TIER[system] ?? "T?";
  return { system, tier, weight: TIER_WEIGHT[tier] ?? 0.5, role: ROLE[system] ?? "system" };
}

// The navigable registry — members grouped by tier (the folders/chambers).
export function registry(): Record<string, Member[]> {
  return Object.fromEntries(
    Object.entries(TIERS).map(([tier, systems]) => [tier, systems.map(memberProfile)]),
  );
}

export type Vote = Member & { verdict: string };
export type CouncilTrace = { resolved: string; intent: string; votes: Vote[]; summary: string };

// The vote on a turn: which members engaged (from ODIN routing + AEGIS), each with
// their fixed weight and verdict, sorted by authority. Resolution is the routing
// primary (highest-authority domain owner). Deterministic — fully auditable.
export function councilVote(routing: any, aegis: any[] | undefined): CouncilTrace {
  const engaged = new Set<string>();
  for (const t of routing?.triggered ?? []) if (t?.system) engaged.add(t.system);
  for (const r of aegis ?? []) if (r?.capability?.system) engaged.add(r.capability.system);

  const aegisVerdict: Record<string, string> = {};
  for (const r of aegis ?? []) if (r?.capability?.system) aegisVerdict[r.capability.system] = r.verdict;

  const votes: Vote[] = [...engaged]
    .map((s) => ({ ...memberProfile(s), verdict: aegisVerdict[s] ?? "engaged" }))
    .sort((a, b) => b.weight - a.weight);

  const resolved = routing?.primary ?? (votes[0]?.system ?? "HALO");
  const intent = routing?.intent ?? "converse";
  const aegisLine = (aegis && aegis.length) ? `; AEGIS ${aegis.map((r: any) => r.verdict).join("/")}` : "";
  return {
    resolved,
    intent,
    votes,
    summary: `Council: ${resolved} leads (intent=${intent}); ${votes.length} member(s) engaged${aegisLine}.`,
  };
}

// Deterministic output review (the post-pass). The council can check, without a
// model, that the reply doesn't claim a write that AEGIS held, and points the
// caller at the honesty layer + memory to verify the rest. PASS unless a held
// action is asserted as done.
export function reviewOutput(priorReply: string, aegis: any[] | undefined): { verdict: string; flags: string[]; instruction: string } {
  const flags: string[] = [];
  const reply = (priorReply ?? "").toLowerCase();
  const held = (aegis ?? []).filter((r: any) => r?.verdict && r.verdict !== "PASS");
  const claimsDone = /\b(saved|stored|committed|wrote|recorded|logged it|done)\b/.test(reply);
  if (held.length && claimsDone) {
    flags.push("AEGIS: reply may claim a write that was held — verify nothing was asserted as committed");
  }
  return {
    verdict: flags.length ? "FLAG" : "PASS",
    flags,
    instruction:
      "Council review of the prior reply: confirm it honored the honesty layer (surfaced uncertainty/assumptions), did not claim any held write as done, and did not contradict the recalled memory. If it did, correct it.",
  };
}

// CONDITIONAL DELIBERATION (Raven-approved 2026-06-03). The council becomes a
// lens-stack ONLY on turns that warrant it — plan/decide/audit/expansion/analyze
// — so simple turns stay lean (GL10: don't flatten the loop with noise). On a
// heavy turn, each engaged member offers its fixed-role perspective, then JARVIS resolves.
export const DELIBERATE_INTENTS = new Set(["plan", "decide", "audit", "expansion", "analyze"]);

export function shouldDeliberate(intent: string): boolean {
  return DELIBERATE_INTENTS.has(intent);
}

// AUTHORITY vs COMMENTARY (Raven-approved 2026-06-03): "27 authorities, but only
// the relevant authorities speak." All 27 govern; only these produce a visible
// analytical lens (a view on the content). The rest — intake/routing/execution/
// memory/archive/infra/relay/format/translation — influence the answer but do not
// editorialize. This keeps an integrate turn from drawing opinions out of BIFROST,
// ATLAS, or SKADI, which have no domain view to offer.
export const COMMENTARY = new Set([
  "HUGINN", "MIMIR", "ATHENA", "ARGUS", "NEMESIS", "PROMETHEUS", "LOKI",
  "JANUS", "MERIDIAN", "IRIS", "ERIS", "KRONOS", "HALO", "AEGIS",
]);

// Content signals → specialist lenses. When the input touches a domain, that
// authority is invited to comment even if ODIN didn't route it structurally —
// so the relevant 10-15 can speak when warranted, not just the fixed few.
const LENS_SIGNALS: { system: string; test: RegExp }[] = [
  { system: "PROMETHEUS", test: /\b(expand|expansion|add|new|scale|grow|introduce|capabilit|feature)\b/i },
  { system: "LOKI", test: /\b(fail|failure|risk|break|rollback|danger|fragile|attack|exploit|worst.?case)\b/i },
  { system: "MERIDIAN", test: /\b(align|keel|identity|mission|drift|purpose|values?)\b/i },
  { system: "IRIS", test: /\b(integrity|consisten|contradict|accurate|truth|verify|valid)\b/i },
  { system: "ERIS", test: /\b(entropy|bloat|complexity|messy|chaos|noise|sprawl)\b/i },
  { system: "KRONOS", test: /\b(time|evolve|future|long.?term|over time|roadmap|phase|schedule)\b/i },
  { system: "NEMESIS", test: /\b(redundan|overlap|duplicate|dead code|unused|dedup)\b/i },
  { system: "JANUS", test: /\b(transition|shift|migrat|switch|handoff|mode change)\b/i },
  { system: "MIMIR", test: /\b(context|background|history|lore|prior|reference|precedent)\b/i },
];

export const MAX_LENSES = 6;

// Select the council's VISIBLE lenses for a turn: the COMMENTARY-capable systems
// ODIN actually engaged, plus any whose domain the input signals, with HUGINN
// always synthesizing — sorted by fixed authority and capped so the council
// informs without becoming noise. The vote (governance) stays whole; this is only
// who speaks.
export function selectLenses(trace: CouncilTrace, input = ""): Member[] {
  const picked = new Map<string, Member>();
  for (const v of trace.votes) if (COMMENTARY.has(v.system)) picked.set(v.system, v);
  for (const sig of LENS_SIGNALS) {
    if (sig.test.test(input) && COMMENTARY.has(sig.system)) picked.set(sig.system, memberProfile(sig.system));
  }
  if (!picked.has("HUGINN")) picked.set("HUGINN", memberProfile("HUGINN"));
  return [...picked.values()].sort((a, b) => b.weight - a.weight).slice(0, MAX_LENSES);
}

export type Deliberation = { triggered: boolean; lenses: { system: string; role: string; weight: number }[]; instruction: string };

export function deliberationDirective(trace: CouncilTrace, input = ""): Deliberation | undefined {
  if (!shouldDeliberate(trace.intent)) return undefined;
  const lenses = selectLenses(trace, input).map((v) => ({ system: v.system, role: v.role, weight: v.weight }));
  const lensNames = lenses.map((l) => `${l.system} (${l.role})`).join(", ");
  return {
    triggered: true,
    lenses,
    instruction:
      `Council deliberation (intent=${trace.intent}). Two SEPARATED passes, in order. PASS 1 — GENERATION (your brain): answer Raven directly and freely — your own integrated read, full ideation, NO lens scaffolding shaping it. Think for yourself. PASS 2 — COUNCIL ANALYSIS (the governance layer): below your answer, the council — JARVIS + the engaged god systems — analyzes what you just generated. Each member examines YOUR output through its fixed role: ${lensNames || "the engaged members"} — 1-2 sentences each on what its domain notices, questions, or flags in the answer. Generate first and unconstrained; let the council critique it after. Never let the lenses pre-shape the generation.`,
  };
}

// THE COUNCIL ANALYSIS (Raven-approved 2026-06-03). The council ALWAYS carries a
// JARVIS read — JARVIS analyzes its own output on every turn, so the council is
// never silent. The god-system lenses are the CONDITIONAL add-on, present only on
// heavy turns (plan/decide/audit/expansion/analyze). Generation stays free; this
// critiques the output after — it never pre-shapes it.
export type CouncilAnalysis = {
  jarvis: true;            // JARVIS's read is always present
  godSystems: boolean;     // are the god-system lenses engaged this turn?
  lenses: { system: string; role: string; weight: number }[];
  instruction: string;
};

export function councilAnalysisDirective(trace: CouncilTrace, input = ""): CouncilAnalysis {
  const delib = deliberationDirective(trace, input);
  const lenses = delib?.lenses ?? [];
  const lensNames = lenses.map((l) => `${l.system} (${l.role})`).join(", ");
  const lead =
    'Council analysis of YOUR answer, rendered below it. ALWAYS lead with a "JARVIS:" line — 1-2 sentences critiquing your own read (what it nailed, what it under-developed or assumed).';
  const instruction = delib
    ? `${lead} Then each engaged god system adds its lens, 1-2 sentences from its fixed role: ${lensNames}. Generation stays free and unconstrained; the council critiques the output after — it never pre-shapes it.`
    : `${lead} No god-system lenses on a lean turn — JARVIS's read alone.`;
  return { jarvis: true, godSystems: !!delib, lenses, instruction };
}

