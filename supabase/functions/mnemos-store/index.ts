import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "authorization, content-type",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
      },
    });
  }

  if (req.method !== "POST") {
    return new Response("method not allowed", { status: 405 });
  }

  let payload: Record<string, unknown> = {};
  try {
    payload = await req.json();
  } catch {
    return new Response("bad request", { status: 400 });
  }

  const text = ((payload.text as string) ?? "").trim();
  if (!text) {
    return new Response(JSON.stringify({ error: "text required" }), {
      status: 400,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }

  const sb = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
  );

  // Generate IDs server-side — client doesn't need to supply them
  const crypto = globalThis.crypto;
  const id = crypto.randomUUID();
  const source_id = crypto.randomUUID();

  const row = {
    id,
    source_id,
    source_type: (payload.source_type as string) ?? "speak_input",
    text: text.slice(0, 2000),
    entropy: (payload.entropy as number) ?? 0.05,
    platform: (payload.platform as string) ?? "claude_code_cli",
    metadata: (payload.metadata as Record<string, unknown>) ?? {},
    timestamp: (payload.timestamp as string) ?? new Date().toISOString(),
  };

  try {
    const { error } = await sb.from("mnemos_memories").insert(row);
    if (error) throw error;
    return new Response(JSON.stringify({ ok: true, id }), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }
});
