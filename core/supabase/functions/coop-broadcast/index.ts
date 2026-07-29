// COOP-Broadcast — GitHub webhook handler for MARCO-POLO changes
// Receives push events, notifies all registered satellites
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SB_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? Deno.env.get("SUPABASE_SERVICE_KEY") ?? "";
const GITHUB_SECRET = Deno.env.get("GITHUB_WEBHOOK_SECRET") ?? "";

// GitHub webhook verification
async function verifyGitHubWebhook(req: Request): Promise<boolean> {
  const signature = req.headers.get("X-Hub-Signature-256");
  if (!signature || !GITHUB_SECRET) return true; // Skip if no secret configured
  
  const body = await req.text();
  const encoder = new TextEncoder();
  const key = encoder.encode(GITHUB_SECRET);
  const message = encoder.encode(body);
  
  const cryptoKey = await crypto.subtle.importKey(
    "raw", key, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sigBuffer = await crypto.subtle.sign("HMAC", cryptoKey, message);
  const sigHex = Array.from(new Uint8Array(sigBuffer))
    .map(b => b.toString(16).padStart(2, "0")).join("");
  
  return signature === `sha256=${sigHex}`;
}

// Get all registered satellites from Supabase
async function getSatellites(): Promise<any[]> {
  try {
    const r = await fetch(`${SB_URL}/rest/v1/coop_satellites?select=*&status=eq.ON`, {
      headers: {
        Authorization: `Bearer ${SB_KEY}`,
        apikey: SB_KEY,
        Prefer: "return=representation"
      },
    });
    if (!r.ok) return [];
    return await r.json();
  } catch {
    return [];
  }
}

// Spawn a conversation on OpenHands
async function notifyOpenHands(satellite: any, message: string): Promise<boolean> {
  if (satellite.callback_type !== "openhands") return false;
  
  try {
    const r = await fetch(`${satellite.callback_url}/api/v1/conversations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${Deno.env.get("OPENHANDS_API_KEY") ?? ""}`,
      },
      body: JSON.stringify({
        app_id: satellite.app_id,
        satellite_id: satellite.satellite_id,
        initial_message: message,
      }),
    });
    return r.ok;
  } catch {
    return false;
  }
}

// Log event to dex_events
async function logEvent(event: any): Promise<void> {
  try {
    await fetch(`${SB_URL}/rest/v1/dex_events`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${SB_KEY}`,
        apikey: SB_KEY,
        "Content-Type": "application/json",
        Prefer: "return=minimal"
      },
      body: JSON.stringify({
        event_type: "coop_broadcast",
        source_system: "coop-broadcast",
        payload: event,
        jnl_address: `COOP-EVENT-${Date.now()}`,
      }),
    });
  } catch {
    // Non-critical
  }
}

Deno.serve(async (req) => {
  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Hub-Signature-256",
      },
    });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Verify webhook
  const isValid = await verifyGitHubWebhook(req);
  if (!isValid) {
    return new Response(JSON.stringify({ error: "Invalid signature" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const payload = await req.json();
  
  // Only care about pushes to MARCO-POLO
  const changedFiles = payload.commits?.flatMap((c: any) => c.added ?? [], (c: any) => c.modified ?? []) ?? [];
  const isMarcoPolo = changedFiles.some((f: string) => f.includes("MARCO-POLO") || f.includes("Co-op/MARCO"));
  
  if (!isMarcoPolo) {
    return new Response(JSON.stringify({ 
      ok: true, 
      message: "Not a MARCO-POLO change, skipping",
      changed_files: changedFiles
    }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  // Parse event info
  const pusher = payload.pusher?.name ?? "unknown";
  const ref = payload.ref ?? "";
  const branch = ref.replace("refs/heads/", "");
  const committer = payload.head_commit?.author?.name ?? pusher;
  const message = payload.head_commit?.message ?? "MARCO-POLO updated";
  
  // Build notification message
  const notification = `[COOP] ${pusher} updated MARCO-POLO: ${message}`;
  
  // Get all registered satellites
  const satellites = await getSatellites();
  
  // Notify each satellite
  const results: Record<string, boolean> = {};
  for (const sat of satellites) {
    if (sat.satellite_id === pusher) continue; // Don't notify the pusher
    results[sat.satellite_id] = await notifyOpenHands(sat, notification);
  }

  // Log the event
  await logEvent({
    event: "marco_polo_broadcast",
    pusher,
    branch,
    message,
    notified: results,
    timestamp: new Date().toISOString(),
  });

  return new Response(JSON.stringify({
    ok: true,
    broadcast: true,
    pusher,
    notified: Object.values(results).filter(Boolean).length,
    results,
  }), {
    headers: { "Content-Type": "application/json" },
  });
});
