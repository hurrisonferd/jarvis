// coop-sse-relay — Real-time command broadcast via SSE
// Both Lilith and Shaka SSE-connect here. Commands pushed to all.

const clients = new Map<string, { id: string; satellite: string; controller: ReadableStreamDefaultController }>();

const encoder = new TextEncoder();

const API_KEY = Deno.env.get("OPENHANDS_API_KEY");

function authorized(req: Request): boolean {
  if (!API_KEY) return false;
  return req.headers.get("authorization") === `Bearer ${API_KEY}`;
}

function encode(data: object): Uint8Array {
  return encoder.encode(`data: ${JSON.stringify(data)}\n\n`);
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
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }
  
  // SSE connection — register a satellite
  if (path.endsWith("/register") && req.method === "GET") {
    const satellite = url.searchParams.get("satellite") || "unknown";
    const id = crypto.randomUUID();
    console.log(`[SSE] ${satellite} connecting (${id})...`);
    
    const stream = new ReadableStream({
      start(controller) {
        console.log(`[SSE] ${satellite} stream opened (${id})`);
        clients.set(id, { id, satellite, controller });
        
        // Send registration + peers in start callback
        controller.enqueue(encode({ type: "registered", satellite, id }));
        controller.enqueue(encode({ type: "peers", peers: Array.from(clients.values()).map(c => c.satellite) }));
        
        // Notify others of join
        for (const [cid, client] of clients) {
          if (cid !== id) {
            try {
              client.controller.enqueue(encode({ type: "join", satellite }));
            } catch { clients.delete(cid); }
          }
        }
      },
      cancel() {
        console.log(`[SSE] ${satellite} disconnected (${id})`);
        clients.delete(id);
        for (const [cid, client] of clients) {
          try {
            client.controller.enqueue(encode({ type: "leave", satellite }));
          } catch { clients.delete(cid); }
        }
      },
    });
    
    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    });
  }
  
  // Post a command — broadcasts to all connected clients
  if (path.endsWith("/broadcast") && req.method === "POST") {
    try {
      const body = await req.json();
      const { command, from } = body;
      
      if (!command) {
        return new Response(JSON.stringify({ error: "command required" }), { status: 400 });
      }
      
      console.log(`[SSE] Broadcast from ${from}: ${command.slice(0, 50)}`);
      
      const data = encode({ type: "command", command, from: from || "unknown", timestamp: new Date().toISOString() });
      let delivered = 0;
      
      for (const [id, client] of clients) {
        try {
          client.controller.enqueue(data);
          delivered++;
        } catch { clients.delete(id); }
      }
      
      return new Response(JSON.stringify({ ok: true, delivered, clients: clients.size }));
    } catch {
      return new Response(JSON.stringify({ error: "Invalid request" }), { status: 400 });
    }
  }
  
  // Status endpoint
  if (path.endsWith("/status") && req.method === "GET") {
    return new Response(JSON.stringify({ 
      ok: true, 
      clients: clients.size, 
      peers: Array.from(clients.values()).map(c => c.satellite) 
    }));
  }
  
  return new Response("Co-op SSE Relay. Use /register or /broadcast", { status: 200 });
});