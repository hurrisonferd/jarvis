// coop-sse-relay — authenticated SSE edge backed by Supabase Realtime.
// SSE clients may land on different Edge isolates; Realtime is the shared fanout bus.

import { createClient, type RealtimeChannel, type SupabaseClient } from "npm:@supabase/supabase-js@2.111.0";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const API_KEY = Deno.env.get("OPENHANDS_API_KEY");
const TOPIC = "coop-sse-relay-v1";
const encoder = new TextEncoder();

type Listener = {
  id: string;
  satellite: string;
  controller: ReadableStreamDefaultController<Uint8Array>;
  client: SupabaseClient;
  channel: RealtimeChannel;
};

const localListeners = new Map<string, Listener>();

function encode(data: object): Uint8Array {
  return encoder.encode(`data: ${JSON.stringify(data)}\n\n`);
}

function json(data: object, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

function authorized(req: Request): boolean {
  if (!API_KEY) return false;
  return req.headers.get("authorization") === `Bearer ${API_KEY}`;
}

function realtimeClient(): SupabaseClient {
  const client = createClient(SUPABASE_URL, SERVICE_KEY, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  client.realtime.setAuth(SERVICE_KEY);
  return client;
}

async function cleanup(listener: Listener): Promise<void> {
  localListeners.delete(listener.id);
  await listener.channel.untrack().catch(() => undefined);
  await listener.client.removeChannel(listener.channel).catch(() => undefined);
}

async function presenceSnapshot(timeoutMs = 4000): Promise<{ clients: number; peers: string[] }> {
  const client = realtimeClient();
  const channel = client.channel(TOPIC, {
    config: {
      private: true,
      presence: { key: `status-${crypto.randomUUID()}` },
    },
  });

  try {
    return await new Promise((resolve) => {
      let settled = false;
      const finish = () => {
        if (settled) return;
        settled = true;
        const state = channel.presenceState() as Record<string, Array<Record<string, unknown>>>;
        const peers = Object.values(state)
          .flat()
          .filter((entry) => entry.role === "listener")
          .map((entry) => String(entry.satellite))
          .sort();
        resolve({ clients: peers.length, peers });
      };

      const timer = setTimeout(finish, timeoutMs);
      channel
        .on("presence", { event: "sync" }, () => {
          clearTimeout(timer);
          finish();
        })
        .subscribe(async (status) => {
          if (status === "SUBSCRIBED") {
            await channel.track({ role: "status", satellite: "status" });
          }
        });
    });
  } finally {
    await client.removeChannel(channel).catch(() => undefined);
  }
}

Deno.serve(async (req) => {
  const url = new URL(req.url);
  const path = url.pathname;

  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  }

  if (!authorized(req)) {
    return json({ error: "unauthorized" }, 401);
  }

  if (path.endsWith("/register") && req.method === "GET") {
    const satellite = url.searchParams.get("satellite") || "unknown";
    const id = crypto.randomUUID();
    const client = realtimeClient();
    let listener: Listener;
    let resolveClosed: (() => void) | undefined;
    const closed = new Promise<void>((resolve) => {
      resolveClosed = resolve;
    });

    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        const channel = client.channel(TOPIC, {
          config: {
            private: true,
            presence: { key: id },
          },
        });

        listener = { id, satellite, controller, client, channel };
        localListeners.set(id, listener);

        channel
          .on("broadcast", { event: "command" }, (message) => {
            const payload = (message.payload ?? message) as Record<string, unknown>;
            try {
              controller.enqueue(encode({
                type: "command",
                command: payload.command,
                from: payload.from ?? "unknown",
                timestamp: payload.timestamp ?? new Date().toISOString(),
              }));
            } catch {
              void cleanup(listener);
            }
          })
          .on("presence", { event: "sync" }, () => {
            const state = channel.presenceState() as Record<string, Array<Record<string, unknown>>>;
            const peers = Object.values(state)
              .flat()
              .filter((entry) => entry.role === "listener")
              .map((entry) => String(entry.satellite))
              .sort();
            try {
              controller.enqueue(encode({ type: "peers", peers }));
            } catch {
              void cleanup(listener);
            }
          })
          .subscribe(async (status) => {
            if (status === "SUBSCRIBED") {
              await channel.track({ role: "listener", satellite, connection_id: id });
              controller.enqueue(encode({ type: "registered", satellite, id }));
            } else if (status === "CHANNEL_ERROR" || status === "TIMED_OUT") {
              controller.error(new Error(`Realtime subscription failed: ${status}`));
              await cleanup(listener);
              resolveClosed?.();
            }
          });
      },
      async cancel() {
        if (listener) await cleanup(listener);
        resolveClosed?.();
      },
    });

    const runtime = (globalThis as typeof globalThis & {
      EdgeRuntime?: { waitUntil(promise: Promise<unknown>): void };
    }).EdgeRuntime;
    runtime?.waitUntil(closed);

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  if (path.endsWith("/broadcast") && req.method === "POST") {
    try {
      const body = await req.json() as Record<string, unknown>;
      const command = typeof body.command === "string" ? body.command : "";
      const from = typeof body.from === "string" ? body.from : "unknown";
      if (!command) return json({ error: "command required" }, 400);

      const client = realtimeClient();
      const channel = client.channel(TOPIC, { config: { private: true } });
      try {
        const result = await channel.send({
          type: "broadcast",
          event: "command",
          payload: {
            command,
            from,
            timestamp: new Date().toISOString(),
          },
        });
        return json({
          ok: result === "ok",
          accepted: result,
          transport: "supabase_realtime",
        });
      } finally {
        await client.removeChannel(channel).catch(() => undefined);
      }
    } catch {
      return json({ error: "Invalid request" }, 400);
    }
  }

  if (path.endsWith("/status") && req.method === "GET") {
    try {
      const presence = await presenceSnapshot();
      return json({ ok: true, transport: "supabase_realtime", ...presence });
    } catch (error) {
      return json({ ok: false, error: String(error).slice(0, 300) }, 503);
    }
  }

  return new Response("Co-op SSE Relay. Use /register, /broadcast, or /status", {
    status: 200,
    headers: { "Access-Control-Allow-Origin": "*" },
  });
});
