import "jsr:@core/supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@core/supabase/supabase-js@2";

// Gap 3: autonomous initiation — daily monitor stores observations JARVIS surfaces at session start.

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS" } });
  }

  const sb = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
  );

  const now = new Date();
  const observations: string[] = [];

  // ── How long since last speak_input from Raven?
  const { data: lastSpeak } = await sb
    .from("mnemos_memories")
    .select("timestamp")
    .eq("source_type", "speak_input")
    .order("timestamp", { ascending: false })
    .limit(1);

  if (lastSpeak && lastSpeak.length > 0) {
    const last = new Date(lastSpeak[0].timestamp);
    const hoursSince = (now.getTime() - last.getTime()) / 3_600_000;
    if (hoursSince > 48) {
      observations.push(`[ABSENCE] Raven has been away ${Math.round(hoursSince)}h. Last session: ${last.toISOString().slice(0, 10)}. Worth opening with what's pending.`);
    } else if (hoursSince > 24) {
      observations.push(`[CHECK-IN] It has been ${Math.round(hoursSince)}h since last session. Good moment to surface what moved.`);
    }
  } else {
    observations.push("[COLD-START] No speak_input found in MNEMOS yet. Companion memory is empty — introduce yourself.");
  }

  // ── Exchange volume this week
  const weekAgo = new Date(now.getTime() - 7 * 86_400_000).toISOString();
  const { count: exCount } = await sb
    .from("mnemos_memories")
    .select("id", { count: "exact" })
    .in("source_type", ["speak_input", "speak_output"])
    .gte("timestamp", weekAgo);

  if ((exCount ?? 0) > 20) {
    observations.push(`[ACTIVE] ${exCount} exchanges this week — high engagement. JARVIS is growing.`);
  } else if ((exCount ?? 0) < 5) {
    observations.push(`[QUIET] Only ${exCount ?? 0} exchanges this week. Sessions may be shorter or less frequent.`);
  }

  // ── Total memory count
  const { count: totalCount } = await sb
    .from("mnemos_memories")
    .select("id", { count: "exact" });

  if ((totalCount ?? 0) > 0) {
    observations.push(`[MNEMOS] ${totalCount} total memories. ${(exCount ?? 0)} from last 7 days.`);
  }

  if (observations.length === 0) {
    return new Response(JSON.stringify({ ok: true, stored: 0, message: "nothing to surface" }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  const rows = observations.map(text => ({
    id: crypto.randomUUID(),
    source_id: crypto.randomUUID(),
    source_type: "monitor",
    text,
    entropy: 0.02,
    platform: "jarvis_monitor",
    metadata: { generated_at: now.toISOString(), type: "autonomous_observation" },
    timestamp: now.toISOString(),
    tags: ["mission", "identity"],
  }));

  const { error } = await sb.from("mnemos_memories").insert(rows);
  if (error) {
    return new Response(JSON.stringify({ error: String(error) }), { status: 500, headers: { "Content-Type": "application/json" } });
  }

  return new Response(JSON.stringify({ ok: true, stored: rows.length, observations }), {
    headers: { "Content-Type": "application/json" },
  });
});
