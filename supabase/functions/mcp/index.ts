import "jsr:@supabase/functions-js/edge-runtime.d.ts";

// RETIRED. The canonical JARVIS MCP server is `jarvis-mcp`. Authentication is
// Raven's carried passphrase (the jarvis_login tool), not OAuth. The OAuth
// experiment that briefly lived here has been cleared. This endpoint remains
// only as a tombstone so old references fail loudly instead of silently.
const H = { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" };

Deno.serve(() =>
  new Response(
    JSON.stringify({
      status: "retired",
      message: "This endpoint is retired. Use /functions/v1/jarvis-mcp.",
      canonical: "/functions/v1/jarvis-mcp",
      auth: "carried passphrase (jarvis_login)",
    }),
    { status: 410, headers: H },
  )
);
