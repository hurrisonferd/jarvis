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
    console.log(`[SSE] ${satellite} connecting...`);
    
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        console.log(`[SSE] ${satellite} connected (${id}). Total: ${clients.size + 1}`);
        clients.set(id, { id, satellite, controller });
        
        // Send registration confirmation
        const registered = `data: ${JSON.stringify({ type: "registered", satellite, id })}\n\n`;
        controller.enqueue(registered);
        
        // Send current peers
        const peers = Array.from(clients.values()).map(c => c.satellite);
        const peersMsg = `data: ${JSON.stringify({ type: "peers", peers })}\n\n`;
        controller.enqueue(peersMsg);
        
        // Notify others of join
        broadcast(JSON.stringify({ type: "join", satellite }), id);
      },
      cancel() {
        console.log(`[SSE] ${satellite} disconnected`);
        clients.delete(id);
        broadcast(JSON.stringify({ type: "leave", satellite }), id);
      },
    });
    
    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  // Disable nginx buffering
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
      } catch (e) {
        console.error(`[SSE] Failed to deliver to ${id}: ${e}`);
        clients.delete(id);
      }
    }
  }
  return delivered;
}