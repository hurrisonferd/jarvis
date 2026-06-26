// jarvis-jcs — JCS (JC + SL) write surface.
// Called by sl.py at session-start (jc_open) and session-close (jc_seal + sl_write).
// Uses jarvis-dex as internal relay (same Deno runtime, service auth works).
// All writes logged to dex_events (GL5 spine).

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function fail(msg: string, status = 400) {
  return json({ ok: false, error: msg }, status);
}

function stardate(): string {
  const now = new Date();
  const yearStart = new Date(now.getUTCFullYear(), 0, 1);
  const dayOfYear = Math.floor((now.getTime() - yearStart.getTime()) / 86400000);
  const fracDay = (now.getUTCHours() * 3600 + now.getUTCMinutes() * 60 + now.getUTCSeconds()) / 86400;
  return `${now.getUTCFullYear()}.${(dayOfYear + 1).toString().padStart(3, "0")}.${Math.floor(fracDay * 1000).toString().padStart(3, "0")}`;
}

function toISO(v: unknown): string {
  if (!v) return new Date().toISOString();
  try { return new Date(String(v)).toISOString(); } catch { return new Date().toISOString(); }
}

function arr(a: unknown): unknown[] { return Array.isArray(a) ? a : []; }
function str(a: unknown, def = ""): string { return a != null ? String(a) : def; }

// Call jarvis-dex internally (same Deno runtime — service auth works)
async function relayDex(tool: string, args: Record<string, unknown>): Promise<unknown> {
  const res = await fetch(`${SUPABASE_URL}/functions/v1/jarvis-dex`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool, args }),
  });
  return res.json();
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return fail("POST only", 405);
  let body: any;
  try { body = await req.json(); } catch { return fail("invalid JSON"); }
  if (!body?.tool) return fail("{ tool, args } required");

  const { tool, args = {} } = body;

  switch (tool) {
    case "jc_open": {
      const alias = str(args.alias, "");
      const subject = str(args.subject, "");
      const stream = str(args.stream, "jarvis-ayre");
      const m = alias.match(/^JC-(\d{2})(\d{2})(\d{2})-/);
      const yyyy = m ? `20${m[1]}` : new Date().getUTCFullYear().toString();
      const mm = m ? m[2] : String(new Date().getUTCMonth() + 1).padStart(2, "0");
      const dd = m ? m[3] : String(new Date().getUTCDate()).padStart(2, "0");
      const result = await relayDex("log_event", {
        type: "jc_open",
        actor: "jarvis-jcs",
        jnl: `LOG-JC-JC-${yyyy}${mm}${dd}`,
        detail: {
          alias, subject, stream,
          stardate: args.stardate ? str(args.stardate) : stardate(),
          repo_url: str(args.repo_url, "https://github.com/hurrisonferd/jarvis"),
          participants: arr(args.participants).length > 0 ? arr(args.participants) : ["raven", "jarvis-c", "ayre-c"],
          when_start: toISO(args.when_start),
        },
      }) as { ok?: boolean; logged?: boolean; error?: string };
      if (!result?.ok) return fail(`jc_open: ${result?.error ?? "relay failed"}`, 500);
      return json({ ok: true, action: "open", alias, stream });
    }

    case "jc_seal": {
      const alias = str(args.alias, "");
      const result = await relayDex("log_event", {
        type: "jc_seal",
        actor: "jarvis-jcs",
        jnl: `LOG-JC-JC-SEAL`,
        detail: {
          alias,
          stream: str(args.stream, "jarvis-ayre"),
          stardate: args.stardate ? str(args.stardate) : stardate(),
          summary: str(args.summary, ""),
          banter: arr(args.banter),
          decisions: arr(args.decisions),
          open: arr(args.open),
          keystones: arr(args.keystones),
          task_summary: arr(args.task_summary),
          when_end: toISO(args.when_end),
        },
      }) as { ok?: boolean; error?: string };
      if (!result?.ok) return fail(`jc_seal: ${result?.error ?? "relay failed"}`, 500);
      return json({ ok: true, action: "seal", alias });
    }

    case "sl_write": {
      const result = await relayDex("log_event", {
        type: "sl_write",
        actor: "jarvis-jcs",
        jnl: `LOG-SL-SL`,
        detail: {
          alias: str(args.alias, ""),
          stream: str(args.stream, "jarvis-ayre"),
          log_type: str(args.log_type, "SESSION"),
          stardate: args.stardate ? str(args.stardate) : stardate(),
          repo_url: str(args.repo_url, "https://github.com/hurrisonferd/jarvis"),
          events: arr(args.events),
          related: arr(args.related),
          digest: str(args.digest, ""),
          status: str(args.status, "SEALED"),
          decisions: arr(args.decisions),
          participants: arr(args.participants).length > 0 ? arr(args.participants) : ["raven", "jarvis-c", "ayre-c"],
          started_at: toISO(args.started_at),
          ended_at: toISO(args.ended_at),
          task_summary: arr(args.task_summary),
        },
      }) as { ok?: boolean; error?: string };
      if (!result?.ok) return fail(`sl_write: ${result?.error ?? "relay failed"}`, 500);
      return json({ ok: true, action: "insert", alias: args.alias });
    }

    default:
      return fail(`unknown tool: ${tool}`);
  }
});
