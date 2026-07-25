import "jsr:@core/supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@core/supabase/supabase-js@2";
import { type Op, validateWrite } from "./validate.ts";

// P34 phase 2: governed write proxy.
// The public anon key is read-only at the DB. Every browser write flows through here,
// is checked against a strict (table, op) whitelist (validate.ts — pure + tested),
// and is performed with the service role.
// Closes GL5: the public key can no longer insert/update/delete arbitrary tables.

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
// Custom secret first; fall back to the platform-injected service role key so the
// proxy always has write access regardless of which secret name is configured.
const SUPABASE_SERVICE_KEY =
  Deno.env.get("SUPABASE_SERVICE_KEY") ??
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type, apikey",
};

function reject(reason: string, status = 403) {
  return new Response(JSON.stringify({ ok: false, error: reason }), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return reject("POST only", 405);

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return reject("invalid JSON", 400);
  }

  const table = String(body.table ?? "");
  const op = String(body.op ?? "") as Op;
  const data = body.data;
  const match = (body.match ?? null) as Record<string, unknown> | null;
  const onConflict = body.onConflict ? String(body.onConflict) : undefined;
  const returning = body.returning ? String(body.returning) : undefined;

  const check = validateWrite({ table, op, data, match });
  if (!check.ok) return reject(check.error);

  const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

  try {
    let res;
    if (op === "insert") {
      let q = sb.from(table).insert(data);
      if (returning) q = q.select(returning).single();
      res = await q;
    } else if (op === "upsert") {
      res = await sb.from(table).upsert(data, onConflict ? { onConflict } : undefined);
    } else if (op === "update") {
      res = await sb.from(table).update(data).match(match!);
    } else { // delete
      res = await sb.from(table).delete().match(match!);
    }

    if (res.error) return reject(res.error.message, 400);
    return new Response(JSON.stringify({ ok: true, data: res.data ?? null }), {
      headers: { ...cors, "Content-Type": "application/json" },
    });
  } catch (err) {
    return reject(String(err), 500);
  }
});
