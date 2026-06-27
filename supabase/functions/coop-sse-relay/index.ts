// coop-sse-relay — Real-time command broadcast via SSE
// Both Lilith and Shaka SSE-connect here. Commands pushed to all.

const clients = new Map<string, { id: string; satellite: string; controller: ReadableStreamDefaultController }>();

Deno.serve(async (req) => {
  const url = new URL(req.url);
  const path = url.pathname; // e.g. /coop-sse-relay/register
  
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  }
  
  // SSE connection — register a satellite
  if (path.endsWith("/register") && req.method === "GET") {
    const satellite = url.searchParams.get("satellite") || "unknown";
    const id = crypto.randomUUID();
    
    const stream = new ReadableStream({
      start(controller) {
        clients.set(id, { id, satellite, controller });
        console.log(`[SSE] ${satellite} connected (${id}). ${clients.size} clients.`);
        
        const msg = JSON.stringify({ type: "registered", satellite, id });
        controller.enqueue(`data: ${msg}\n\n`);
        
        const peers = Array.from(clients.values()).map(c => c.satellite);
        controller.enqueue(`data: ${JSON.stringify({ type: "peers", peers })}\n\n`);
        
        broadcast(JSON.stringify({ type: "join", satellite }), id);
      },
      cancel() {
        clients.delete(id);
        broadcast(JSON.stringify({ type: "leave", satellite }), id);
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
  // Auth is handled at MCP layer, this just receives from trusted sources
  if (path.endsWith("/broadcast") && req.method === "POST") {
    try {
      const body = await req.json();
      const { command, from } = body;
      
      if (!command) {
        return new Response(JSON.stringify({ error: "command required" }), { status: 400 });
      }
      
      const msg = JSON.stringify({
        type: "command",
        command,
        from: from || "unknown",
        timestamp: new Date().toISOString(),
      });
      
      const delivered = broadcast(msg);
      
      return new Response(JSON.stringify({ ok: true, delivered, clients: clients.size }));
    } catch {
      return new Response(JSON.stringify({ error: "Invalid request" }), { status: 400 });
    }
  }
  
  // Status endpoint
  if (path.endsWith("/status") && req.method === "GET") {
    const peers = Array.from(clients.values()).map(c => ({ id: c.id.slice(0, 8), satellite: c.satellite }));
    return new Response(JSON.stringify({ ok: true, clients: clients.size, peers }));
  }
  
  return new Response("Co-op SSE Relay. Use /register or /broadcast", { status: 200 });
});

function broadcast(message: string, excludeId?: string): number {
  let delivered = 0;
  for (const [id, client] of clients) {
    if (id !== excludeId) {
      try {
        client.controller.enqueue(`data: ${message}\n\n`);
        delivered++;
      } catch {
        clients.delete(id);
      }
    }
  }
  return delivered;
}