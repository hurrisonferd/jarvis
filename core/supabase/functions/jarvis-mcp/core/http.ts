// core/http.ts — the response shaper + Supabase fetch layer. Every tool returns through
// `text()`; every server-side read goes through `callFunction`/`rest`. (Extracted from
// index.ts, zero behavior change.)

import { type Json, SERVICE_KEY, SUPABASE_URL } from "./env.ts";

// Wrap any payload as an MCP text content block. Strings pass through; objects pretty-print.
export function text(content: unknown) {
  return {
    content: [
      {
        type: "text" as const,
        text: typeof content === "string" ? content : JSON.stringify(content, null, 2),
      },
    ],
  };
}

// POST to a sibling edge function with the service key. Throws on non-2xx.
export async function callFunction(name: string, body: Json): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/functions/v1/${name}`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${SERVICE_KEY}`,
      apikey: SERVICE_KEY,
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`${name} ${res.status}: ${JSON.stringify(payload)}`);
  return payload;
}

// GET against PostgREST with the service key. Throws on non-2xx.
export async function rest(path: string, opts?: { method?: string; body?: unknown; prefer?: string }): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method: opts?.method ?? "GET",
    headers: {
      authorization: `Bearer ${SERVICE_KEY}`,
      apikey: SERVICE_KEY,
      "content-type": "application/json",
      ...(opts?.prefer ? { prefer: opts.prefer } : opts?.body ? { prefer: "return=minimal" } : {}),
    },
    ...(opts?.body !== undefined ? { body: JSON.stringify(opts.body) } : {}),
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`rest ${res.status}: ${JSON.stringify(payload)}`);
  return payload;
}
