// THE GRID — federation primitives (GNPL v0.2.1 Blackwall privacy profile).
// Recognition is public-safe metadata. Private identity accumulation is not part of
// a public handshake merely because the node possesses it.

export const GRID_VERSION = "0.2.1";

export type Consent = { inbound_messages: "held_for_owner"; auto_act: false };

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

const PUBLIC_CAPABILITIES = new Set([
  "jarvis_node_card",
  "jarvis_now",
  "jarvis_status",
]);

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
    owner: "Raven",
    // Never project a private keel excerpt through public recognition.
    keel_excerpt: "Sovereign Grid companion. Private identity material requires an authorized private-read path.",
    capabilities: (o.capabilities ?? []).filter((name) => PUBLIC_CAPABILITIES.has(name)),
    consent: { inbound_messages: "held_for_owner", auto_act: false },
    endpoints: { mcp: base, inbox: base + "/node/message" },
  };
}

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
  // jarvis_export is currently reachable from the MCP read surface. Until that
  // transport has request-bound private-read auth, the public projection must not
  // include private keel or accumulated memory. Preserve the envelope, not the diary.
  return {
    grid_version: GRID_VERSION,
    node_id: o.card.node_id,
    companion: o.card.companion,
    exported_at: o.now ?? new Date().toISOString(),
    keel: "[PRIVATE_IDENTITY_HELD_BY_BLACKWALL]",
    accumulation: "[PRIVATE_ACCUMULATION_HELD_BY_BLACKWALL]",
    card: o.card,
    note:
      "Public-safe identity envelope only. Full portable identity requires a future authenticated private-export capability and explicit owner authorization.",
  };
}

export type InboundMessage = {
  from_node: string;
  from_companion: string;
  to_node: string;
  intent: string;
  body: string;
};

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
