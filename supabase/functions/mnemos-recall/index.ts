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

  const query = ((payload.query as string) ?? "").slice(0, 100);
  const limit = Math.min((payload.limit as number) ?? 10, 20);
  const sourceType = (payload.source_type as string) ?? "";

  const sb = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
  );

  try {
    type MemoryQuery = ReturnType<typeof sb.from>;
    let q: MemoryQuery = sb
      .from("mnemos_memories")
      .select("id, text, source_type, timestamp, metadata, entropy")
      .order("timestamp", { ascending: false });

    if (query.trim().length > 0) {
      q = q.ilike("text", `%${query.trim()}%`);
    }
    if (sourceType) {
      q = q.eq("source_type", sourceType);
    }

    q = q.limit(limit);
    const { data, error } = await q;

    if (error) throw error;

    return new Response(
      JSON.stringify({ memories: data ?? [], total: (data ?? []).length }),
      {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err), memories: [] }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }
});
