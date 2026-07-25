// BIFROST — JARVIS's reach. The bridge to the world's knowledge.
//
// Pulls live, grounded answers via Gemini's Google Search tool: real-time web
// results synthesized + cited, on the key we already have. This is the sponge's
// mouth — JARVIS doesn't store the ocean, it drinks what it needs on demand.
//
// Pure request-building + response-parsing here; the fetch lives in index.ts.
// AEGIS gates the reach; the remember loop keeps only what's worth keeping.

export type Source = { title: string; uri: string };
export type Reach = { answer: string; sources: Source[]; grounded: boolean };

// Gemini native generateContent body with live Google Search grounding.
export function buildRequest(query: string): Record<string, unknown> {
  return {
    contents: [{ role: "user", parts: [{ text: (query ?? "").slice(0, 4000) }] }],
    tools: [{ google_search: {} }],
  };
}

// The native generateContent endpoint for a model (key passed as header by caller).
export function endpoint(base: string, model: string): string {
  return `${base.replace(/\/$/, "")}/v1beta/models/${model}:generateContent`;
}

// Parse Gemini's grounded response into a clean answer + deduped sources.
export function parseGrounded(resp: any): Reach {
  const cand = resp?.candidates?.[0];
  const answer = (cand?.content?.parts ?? [])
    .map((p: any) => p?.text)
    .filter((t: unknown): t is string => typeof t === "string" && t.length > 0)
    .join("")
    .trim();

  const chunks = cand?.groundingMetadata?.groundingChunks ?? [];
  const seen = new Set<string>();
  const sources: Source[] = [];
  for (const c of chunks) {
    const uri = c?.web?.uri;
    if (typeof uri === "string" && uri && !seen.has(uri)) {
      seen.add(uri);
      sources.push({ title: (c.web.title ?? uri).slice(0, 120), uri });
    }
  }
  return { answer, sources, grounded: sources.length > 0 };
}

// Compact, in-prompt summary of a reach — answer + numbered sources. Bounded so
// it never bloats the companion's context.
export function reachSummary(r: Reach, maxChars = 1200): string {
  const body = r.answer.slice(0, maxChars);
  const src = r.sources.slice(0, 4).map((s, i) => `[${i + 1}] ${s.title} — ${s.uri}`).join("\n");
  return src ? `${body}\n\nSOURCES:\n${src}` : body;
}
