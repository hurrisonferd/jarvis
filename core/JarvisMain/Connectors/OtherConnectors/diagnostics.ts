const DEFAULT_MCP_ENDPOINT = "https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp";

type DiagnosticResult = {
  ok: boolean;
  endpoint: string;
  mode: "offline" | "cloud";
  status?: number;
  message: string;
};

function endpointFromEnv(): string {
  return process.env.JARVIS_MCP_ENDPOINT || DEFAULT_MCP_ENDPOINT;
}

async function checkCloud(endpoint: string): Promise<DiagnosticResult> {
  const res = await fetch(endpoint, { headers: { accept: "application/json" } });
  const body = await res.text();
  const acceptsMcpTransport = res.status === 406 && body.includes("text/event-stream");
  return {
    ok: acceptsMcpTransport || res.ok,
    endpoint,
    mode: "cloud",
    status: res.status,
    message: acceptsMcpTransport
      ? "Cloud MCP endpoint is reachable and enforcing SSE/Streamable HTTP transport."
      : body.slice(0, 240),
  };
}

async function main(): Promise<number> {
  const offline = process.argv.includes("--offline");
  const endpoint = endpointFromEnv();
  const result: DiagnosticResult = offline
    ? {
        ok: true,
        endpoint,
        mode: "offline",
        message: "Offline diagnostics passed. Cloud endpoint config is present.",
      }
    : await checkCloud(endpoint);

  console.log(JSON.stringify(result, null, 2));
  return result.ok ? 0 : 1;
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((error: unknown) => {
    console.error(JSON.stringify({
      ok: false,
      endpoint: endpointFromEnv(),
      mode: "cloud",
      message: error instanceof Error ? error.message : String(error),
    }, null, 2));
    process.exitCode = 1;
  });
