// MNEMOS recall — multi-scope memory assembly for the companion path.
//
// Stage 1 of the companion roadmap: memory that ranks by meaning, not just
// recency. The handler gathers scopes (semantic hits + recent exchanges +
// identity profile + active decisions); this module merges them — semantic
// first, deduped, formatted — into the block the model reads.
//
// Pure + testable. The DB I/O (pgvector match_memories + recency queries)
// stays in index.ts; the assembly logic lives here.

export type Scoped = {
  text: string;
  source_type: string;
  timestamp?: string;
  tags?: string[];
  similarity?: number;  // present only for semantic-scope rows
};

export type Scopes = {
  semantic?: Scoped[];   // ranked by cosine similarity (most relevant)
  exchanges?: Scoped[];  // recent speak turns (continuity)
  profile?: Scoped[];    // raven_profile (identity anchor)
  context?: Scoped[];    // misc relevant context (recency/full-text)
  decisions?: Scoped[];  // active decisions (the governed record)
};

export function formatRow(r: Scoped): string {
  const ts = (r.timestamp ?? "").slice(0, 10);
  const type = (r.source_type ?? "memory").slice(0, 16);
  const sim = r.similarity != null ? ` ~${Math.round(r.similarity * 100)}%` : "";
  return `[${type} ${ts}${sim}] ${(r.text ?? "").slice(0, 150)}`;
}

// Assemble the recall block. Semantic hits lead (they're the most relevant);
// every later scope is deduped against what's already shown, so a memory that
// surfaced semantically never repeats lower down as a recency hit.
export function buildRecallBlock(scopes: Scopes, opts: { semanticLimit?: number } = {}): string[] {
  const seen = new Set<string>();
  const take = (rows: Scoped[] | undefined, limit: number): Scoped[] => {
    const out: Scoped[] = [];
    for (const r of rows ?? []) {
      const key = (r.text ?? "").trim();
      if (!key || seen.has(key)) continue;
      seen.add(key);
      out.push(r);
      if (out.length >= limit) break;
    }
    return out;
  };

  const semantic = take(scopes.semantic, opts.semanticLimit ?? 5);
  const exchanges = take(scopes.exchanges, 6);
  const profile = take(scopes.profile, 4);
  const context = take(scopes.context, 4);
  const decisions = take(scopes.decisions, 3);

  const parts: string[] = [];
  if (semantic.length)  parts.push("MOST RELEVANT (semantic):\n" + semantic.map(formatRow).join("\n"));
  if (exchanges.length) parts.push("RECENT EXCHANGES:\n" + exchanges.map(formatRow).join("\n"));
  if (profile.length)   parts.push("RAVEN PROFILE:\n" + profile.map(formatRow).join("\n"));
  if (context.length)   parts.push("RELEVANT CONTEXT:\n" + context.map(formatRow).join("\n"));
  if (decisions.length) parts.push("ACTIVE DECISIONS:\n" + decisions.map(formatRow).join("\n"));
  return parts;
}
