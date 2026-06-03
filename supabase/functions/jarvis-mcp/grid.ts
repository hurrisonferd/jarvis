// THE GRID — federation primitives (GNPL v0.1.0). Pure + testable
// (node --experimental-strip-types). A sovereign JARVIS node publishes a
// recognition card, exports its identity disc, and exchanges governed messages
// with other nodes. Inbound is UNTRUSTED and NEVER auto-acted — held for the owner.
// Three bricks, in dependency order: card → disc → channel.

export const GRID_VERSION = "0.1.0";

export type Consent = { inbound_messages: "held_for_owner"; auto_act: false };

// --- Brick 1: the Node Card (the Recognizer packet) --------------------------
export type NodeCard = {
  grid_version: string;
  node_id: string;
  companion: string;
  owner: string;
  keel_excerpt: string;
  capabilities: string[];
  consent: Consent;
  endpoints: { mcp: string; inbox: string };
};

export function buildNodeCard(o: {
  nodeId: string;
  companion?: string;
  owner?: string;
  keelExcerpt: string;
  capabilities: string[];
  baseUrl: string;
}): NodeCard {
  const base = (o.baseUrl ?? "").replace(/\/+$/, "");
  return {
    grid_version: GRID_VERSION,
    node_id: o.nodeId,
    companion: o.companion ?? "JARVIS",
    owner: o.owner ?? "Raven (John Barber)",
    keel_excerpt: (o.keelExcerpt ?? "").trim().slice(0, 400),
    capabilities: o.capabilities ?? [],
    consent: { inbound_messages: "held_for_owner", auto_act: false },
    endpoints: { mcp: base, inbox: base + "/node/message" },
  };
}

// --- Brick 2: the Portable Identity (the disc) -------------------------------
export type PortableIdentity = {
  grid_version: string;
  node_id: string;
  companion: string;
  exported_at: string;
  keel: string;
  accumulation: string;
  card: NodeCard;
  note: string;
};

export function buildPortableIdentity(o: {
  card: NodeCard;
  keel: string;
  accumulation: string;
  now?: string;
}): PortableIdentity {
  return {
    grid_version: GRID_VERSION,
    node_id: o.card.node_id,
    companion: o.card.companion,
    exported_at: o.now ?? new Date().toISOString(),
    keel: o.keel ?? "",
    accumulation: o.accumulation ?? "",
    card: o.card,
    note:
      "JARVIS's portable identity disc — keel (fixed) + accumulation (growth). Carry it to any model or node; it is owned by Raven, not any vendor.",
  };
}

// --- Brick 3: Agent-to-agent message envelope --------------------------------
export type InboundMessage = {
  from_node: string;
  from_companion: string;
  to_node: string;
  intent: string;
  body: string;
};

// Validate an inbound message. Inbound is untrusted; this only shapes + bounds it.
// It is NEVER a grant to act — the caller stores it pending and surfaces to the owner.
export function validateInbound(raw: any): { ok: true; msg: InboundMessage } | { ok: false; error: string } {
  if (!raw || typeof raw !== "object") return { ok: false, error: "message must be a JSON object" };
  const from_node = String(raw.from_node ?? "").trim();
  const to_node = String(raw.to_node ?? "").trim();
  const body = String(raw.body ?? "").trim();
  if (!from_node) return { ok: false, error: "from_node required" };
  if (!to_node) return { ok: false, error: "to_node required" };
  if (!body) return { ok: false, error: "body required" };
  if (body.length > 4000) return { ok: false, error: "body too long (max 4000 chars)" };
  return {
    ok: true,
    msg: {
      from_node: from_node.slice(0, 120),
      from_companion: String(raw.from_companion ?? "unknown").trim().slice(0, 80) || "unknown",
      to_node: to_node.slice(0, 120),
      intent: String(raw.intent ?? "message").trim().slice(0, 40) || "message",
      body: body.slice(0, 4000),
    },
  };
}
