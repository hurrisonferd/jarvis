#!/usr/bin/env node

import http from "node:http";
import { createGaiaOSBridgeClient, GAIAOS_TOOL_ALLOWLIST } from "./client.mjs";
import { buildCouncilConversationContract, buildCouncilHostPrompt } from "./conversation.mjs";

const BRIDGE_VERSION = "0.3.0";
const host = process.env.RAVENOS_GAIA_BRIDGE_BIND || "0.0.0.0";
const port = Number(process.env.PORT || process.env.RAVENOS_GAIA_BRIDGE_PORT || 8787);
const gatewayToken = process.env.RAVENOS_GAIA_BRIDGE_TOKEN || "";

function send(res, status, body) {
  const payload = JSON.stringify(body, null, 2);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "x-ravenos-gaiaos-bridge": BRIDGE_VERSION,
  });
  res.end(payload);
}

function authorized(req) {
  return !gatewayToken || req.headers.authorization === `Bearer ${gatewayToken}`;
}

async function readJson(req) {
  const chunks = [];
  let total = 0;
  for await (const chunk of req) {
    total += chunk.length;
    if (total > 64 * 1024) throw new Error("request body too large");
    chunks.push(chunk);
  }
  if (!chunks.length) return {};
  const text = Buffer.concat(chunks).toString("utf8");
  return text ? JSON.parse(text) : {};
}

function compactTool(tool) {
  return {
    name: tool?.name,
    title: tool?.title ?? null,
    description: tool?.description ?? null,
    inputSchema: tool?.inputSchema ?? null,
  };
}

function wrapped(result, extra = {}) {
  return {
    bridge: "RavenOS/GaiaOSBridge",
    bridge_version: BRIDGE_VERSION,
    authority_boundary: "NAOMI",
    read_only: true,
    ...extra,
    result: result.value,
  };
}

async function gaiaFrontDoor(client, body) {
  const request = String(body.request || "").trim();
  if (!request) return { error: "request is required", status: 422 };
  const result = await client.gaia(
    request,
    Array.isArray(body.requested_members) ? body.requested_members : [],
    Number(body.max_members || 3),
    body.include_context !== false,
    Number(body.context_limit || 6),
    Number(body.context_depth || 1),
  );
  return { request, result, status: 200 };
}

const server = http.createServer(async (req, res) => {
  try {
    if (!authorized(req)) return send(res, 401, { error: "unauthorized" });
    const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);
    const client = createGaiaOSBridgeClient({ timeoutMs: 30000 });

    if (req.method === "GET" && url.pathname === "/health") {
      const serverInfo = await client.initialize();
      const tools = await client.listTools();
      const names = (tools?.tools || []).map((tool) => tool.name).sort();
      const missing = GAIAOS_TOOL_ALLOWLIST.filter((name) => !names.includes(name));
      return send(res, missing.length ? 503 : 200, {
        status: missing.length ? "degraded" : "ok",
        bridge: "RavenOS/GaiaOSBridge",
        bridge_version: BRIDGE_VERSION,
        remote_mcp: client.url,
        remote_server: serverInfo,
        authority_boundary: "NAOMI",
        read_only: true,
        preferred_human_surface: "POST /gaiaos/conversation",
        tools_discovered: names,
        missing_expected_tools: missing,
      });
    }

    if (req.method === "GET" && url.pathname === "/gaiaos/tools") {
      const tools = await client.listTools();
      return send(res, 200, {
        bridge: "RavenOS/GaiaOSBridge",
        bridge_version: BRIDGE_VERSION,
        authority_boundary: "NAOMI",
        tools: (tools?.tools || []).filter((tool) => GAIAOS_TOOL_ALLOWLIST.includes(tool.name)).map(compactTool),
      });
    }

    if (req.method === "GET" && url.pathname === "/gaiaos/selftest") {
      return send(res, 200, wrapped(await client.selftest(), { tool: "gaia_selftest" }));
    }

    if (req.method === "POST" && url.pathname === "/gaiaos") {
      const body = await readJson(req);
      const front = await gaiaFrontDoor(client, body);
      if (front.error) return send(res, front.status, { error: front.error });
      return send(res, 200, wrapped(front.result, { tool: "gaia" }));
    }

    if (req.method === "POST" && url.pathname === "/gaiaos/conversation") {
      const body = await readJson(req);
      const front = await gaiaFrontDoor(client, body);
      if (front.error) return send(res, front.status, { error: front.error });
      const contract = buildCouncilConversationContract(front.result.value, front.request);
      const renderPrompt = buildCouncilHostPrompt(contract);
      return send(res, 200, {
        schema: "ravenos.gaiaos.conversation-envelope.v1",
        bridge: "RavenOS/GaiaOSBridge",
        bridge_version: BRIDGE_VERSION,
        authority: "NAOMI",
        mode: "READ_ONLY",
        render_contract: contract,
        host_render_prompt: renderPrompt,
        receipt: contract.hidden_receipt,
      });
    }

    if (req.method === "POST" && url.pathname === "/gaiaos/call") {
      const body = await readJson(req);
      const name = String(body.name || "");
      if (!GAIAOS_TOOL_ALLOWLIST.includes(name)) {
        return send(res, 400, { error: "tool_not_allowed", name, allowlist: GAIAOS_TOOL_ALLOWLIST });
      }
      const result = await client.callTool(name, body.arguments || {});
      return send(res, 200, wrapped(result, { tool: name }));
    }

    if (req.method === "POST" && url.pathname === "/gaiaos/dispatch") {
      const body = await readJson(req);
      if (!Array.isArray(body.signals) || !body.signals.length) {
        return send(res, 422, { error: "signals must be a non-empty array" });
      }
      const result = await client.dispatch(
        body.signals,
        Array.isArray(body.requested_members) ? body.requested_members : [],
        Number(body.max_members || 3),
      );
      return send(res, 200, wrapped(result, { tool: "gaia_dispatch" }));
    }

    if (req.method === "POST" && url.pathname === "/gaiaos/context") {
      const body = await readJson(req);
      const subject = String(body.subject || "").trim();
      if (!subject) return send(res, 422, { error: "subject is required" });
      const result = await client.context(subject, Number(body.limit || 10), Number(body.depth || 1));
      return send(res, 200, wrapped(result, { tool: "gaia_context" }));
    }

    return send(res, 404, {
      error: "not_found",
      routes: [
        "GET /health",
        "GET /gaiaos/tools",
        "GET /gaiaos/selftest",
        "POST /gaiaos/conversation",
        "POST /gaiaos",
        "POST /gaiaos/call",
        "POST /gaiaos/dispatch",
        "POST /gaiaos/context",
      ],
    });
  } catch (error) {
    return send(res, 502, {
      error: "gaiaos_bridge_error",
      message: error?.message || String(error),
    });
  }
});

server.listen(port, host, () => {
  console.log(`RavenOS GaiaOSBridge ${BRIDGE_VERSION} listening on http://${host}:${port}`);
  console.log("Authority boundary: NAOMI");
  console.log("Preferred human surface: POST /gaiaos/conversation");
});
