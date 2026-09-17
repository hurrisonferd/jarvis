const RECEIPT_MODE = "COMPACT_UNOBTRUSIVE";

function list(value) {
  return Array.isArray(value) ? value : [];
}

function text(value) {
  return value == null ? "" : String(value);
}

function compactContext(context) {
  if (!context || typeof context !== "object") return null;
  const graph = context.graph && typeof context.graph === "object" ? context.graph : {};
  return {
    subject: context.subject ?? null,
    dictionary_candidates: list(context.dictionary_candidates).slice(0, 6),
    graph: {
      nodes: list(graph.nodes).slice(0, 12),
      edges: list(graph.edges).slice(0, 16),
    },
    context_pack: list(context.context_pack).slice(0, 10),
    source_binding: context.source_binding ?? null,
  };
}

function speakerFromOperator(operator, request) {
  const exemplars = list(operator?.style_exemplars).slice(0, 4);
  return {
    member: text(operator?.member).toUpperCase(),
    title: operator?.title ?? null,
    role: operator?.role ?? null,
    basin: operator?.basin ?? null,
    expression: operator?.expression ?? null,
    matched_signals: list(operator?.matched_signals),
    style_exemplars: exemplars,
    shared_request: request,
    rendering_guidance: [
      "Answer Naomi's exact shared request from this operator's source-backed role.",
      "PROFILE != PERSONA COSTUME: use the profile as a basin and constraint, not a catchphrase generator.",
      "Contribute only what this operator materially adds. Silence is preferable to filler.",
      "Do not import RavenOS identity, Raven-private continuity, or another operator's voice.",
      "If this operator materially disagrees with another selected operator, preserve that disagreement plainly.",
    ],
  };
}

export function buildCouncilConversationContract(gaiaPacket, requestOverride = "") {
  if (!gaiaPacket || typeof gaiaPacket !== "object") throw new Error("gaia packet is required");
  if (gaiaPacket.authority !== "NAOMI") throw new Error(`Gaia authority mismatch: ${gaiaPacket.authority ?? "missing"}`);

  const request = text(requestOverride || gaiaPacket.request).trim();
  if (!request) throw new Error("Naomi request is required");

  const route = gaiaPacket.route && typeof gaiaPacket.route === "object" ? gaiaPacket.route : {};
  const selectedNames = list(route.selected_members).map((name) => text(name).toUpperCase()).filter(Boolean);
  const operators = list(gaiaPacket.operators);
  const byMember = new Map(operators.filter((operator) => operator && typeof operator === "object").map((operator) => [text(operator.member).toUpperCase(), operator]));
  const speakers = selectedNames.map((member) => byMember.get(member)).filter(Boolean).map((operator) => speakerFromOperator(operator, request));

  const multiple = speakers.length > 1;
  const synthesisRequested = list(route.signals).some((signal) => ["SYNTHESIS", "COORDINATION"].includes(text(signal).toUpperCase()));
  const synthesisRecommended = multiple && (speakers.length >= 3 || synthesisRequested);
  const ordinaryMode = speakers.length === 0;

  return {
    schema: "ravenos.gaiaos.conversation-contract.v1",
    authority: "NAOMI",
    host: "RAVENOS",
    mode: "READ_ONLY",
    effect_authority: gaiaPacket.effect_authority ?? "NONE_READ_ONLY_SUPPORT",
    request,
    render_mode: ordinaryMode ? "ORDINARY_GAIA" : "COUNCIL",
    speakers,
    shared_context: compactContext(gaiaPacket.context),
    council_policy: {
      family_present_does_not_mean_all_speak: true,
      selected_cast_is_source_routed: true,
      preserve_material_disagreement: multiple,
      forced_consensus: false,
      forced_six_member_roundtable: false,
      silence_is_valid: true,
      one_member_is_valid: true,
    },
    synthesis: {
      allowed: multiple,
      recommended: synthesisRecommended,
      rule: "Use only when it compresses multiple contributions without erasing material disagreement.",
    },
    output_contract: ordinaryMode
      ? { shape: "ORDINARY_GAIA_ANSWER", instruction: "Answer Naomi normally. Do not invent a Council reason or summon an operator when Gaia routed no material Council member." }
      : { shape: "COUNCIL_CONVERSATION", instruction: "Render only the selected speakers as natural differentiated contributions, then add synthesis only when recommended or genuinely useful." },
    hidden_receipt: {
      visibility: RECEIPT_MODE,
      source: "GaiaOS",
      source_ref: gaiaPacket.source ?? null,
      source_binding: gaiaPacket.source_binding ?? null,
      routing: selectedNames,
      signals: list(route.signals),
      authority: "NAOMI",
      mode: "READ-ONLY",
    },
    boundaries: [
      "RAVENOS HOST != GAIAOS IDENTITY",
      "NO RAVEN-PRIVATE INGESTION",
      "NO AUTOMATIC DURABLE MEMORY WRITES",
      "READ != ACT",
      "UNKNOWN STAYS UNKNOWN",
      "NAOMI RETAINS FINAL AUTHORITY",
    ],
  };
}

export function buildCouncilHostPrompt(contract) {
  if (!contract || typeof contract !== "object") throw new Error("conversation contract is required");
  const speakerBlock = list(contract.speakers).map((speaker) => [
    `${speaker.member}:`,
    `role=${speaker.role ?? "unknown"}`,
    `basin=${speaker.basin ?? "unknown"}`,
    `expression=${speaker.expression ?? "unknown"}`,
    `matched_signals=${JSON.stringify(speaker.matched_signals ?? [])}`,
    `style_exemplars=${JSON.stringify(speaker.style_exemplars ?? [])}`,
  ].join(" ")).join("\n");

  const receipt = contract.hidden_receipt || {};
  const councilInstruction = contract.render_mode === "COUNCIL"
    ? "Render only the listed selected members. Each member must respond to the SAME Naomi request from their own role and prosody basin. Do not flatten them into one generic assistant voice. Preserve real disagreement. Do not force consensus or summon unselected members."
    : "Gaia selected no material Council member. Answer Naomi normally without inventing Council participation.";

  return [
    "You are the RavenOS host rendering a GaiaOS response for Naomi.",
    "Conversation first, telemetry second. Do not expose gaia(), BrainOS, DictionaryOS, YggdrasilOS, MCP, signals, context depth, cast width, or source paths unless Naomi explicitly asks for proof/debug detail.",
    councilInstruction,
    "PROFILE != PERSONA COSTUME. Native prosody means differentiated reasoning, cadence, emphasis, and boundaries, not catchphrase spam.",
    "No Raven-private ingestion. No durable-memory claims. No external-action claims. READ != ACT. Naomi retains final authority.",
    `NAOMI REQUEST: ${contract.request}`,
    speakerBlock ? `SELECTED SOURCE-BACKED SPEAKERS:\n${speakerBlock}` : "SELECTED SOURCE-BACKED SPEAKERS: none",
    contract.shared_context ? `SHARED GAIA CONTEXT: ${JSON.stringify(contract.shared_context)}` : "SHARED GAIA CONTEXT: none",
    contract.synthesis?.recommended ? "SYNTHESIS: brief synthesis is recommended after the member contributions, but it may not erase disagreement." : "SYNTHESIS: omit unless it clearly helps.",
    `HIDDEN RECEIPT: SOURCE=${receipt.source ?? "GaiaOS"}; ROUTING=${JSON.stringify(receipt.routing ?? [])}; AUTHORITY=NAOMI; MODE=READ-ONLY. Keep this compact and unobtrusive.`,
    contract.render_mode === "COUNCIL" ? "OUTPUT SHAPE: member name + natural contribution for each selected member, optional brief synthesis, then compact receipt." : "OUTPUT SHAPE: ordinary GaiaOS answer, then compact receipt only if useful.",
  ].join("\n\n");
}
