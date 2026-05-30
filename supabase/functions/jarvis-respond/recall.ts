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
// surfaced semantically never repeats lower down as a recency hit. `exclude`
// seeds the seen-set with text already in the model's context (the message
// history), so recall never re-sends what Opus already has — saves tokens,
// sharpens signal.
export function buildRecallBlock(
  scopes: Scopes,
  opts: { semanticLimit?: number; exclude?: string[]; maxChars?: number } = {},
): string[] {
  const seen = new Set<string>((opts.exclude ?? []).map((t) => (t ?? "").trim()).filter(Boolean));
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

  // Hard budget: the recall block can't bloat the prompt. Sections are added in
  // priority order (semantic first, always kept); later ones drop if over budget.
  const maxChars = opts.maxChars ?? 2400;
  const parts: string[] = [];
  let used = 0;
  const push = (label: string, rows: Scoped[]) => {
    if (!rows.length) return;
    const block = label + "\n" + rows.map(formatRow).join("\n");
    if (parts.length > 0 && used + block.length > maxChars) return;
    parts.push(block);
    used += block.length;
  };

  push("MOST RELEVANT (semantic):", semantic);
  push("RECENT EXCHANGES:", exchanges);
  push("RAVEN PROFILE:", profile);
  push("RELEVANT CONTEXT:", context);
  push("ACTIVE DECISIONS:", decisions);
  return parts;
}
