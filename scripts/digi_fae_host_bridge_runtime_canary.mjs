#!/usr/bin/env node

import crypto from 'node:crypto';

const base = String(process.env.DIGI_FAE_BRIDGE_URL || '').replace(/\/+$/, '');
if (!base) throw new Error('DIGI_FAE_BRIDGE_URL is required');

const MCP = `${base}/mcp`;
const EXPECTED_VERSION = '0.3.4';
const EXPECTED_ATLAS_SHA = '7a0c73ef61c686731ec6c53d518ec5544d9178c7ab2ea5d2f2ed32a4029a0dee';
const EXPECTED_TOOLS = ['digi_fae_health', 'show_fae_council', 'show_fae_hud'].sort();
const EXPECTED_RESOURCES = [
  'digi-fae://fairyos/current',
  'digi-fae://health',
  'digi-fae://manifest',
  'digi-fae://members',
  'ui://digi-fae/hud/v3.html',
].sort();

let id = 1;

function decodeRpc(text) {
  const trimmed = text.trim();
  if (trimmed.startsWith('{')) return JSON.parse(trimmed);
  for (const line of text.split(/\r?\n/)) {
    if (!line.startsWith('data:')) continue;
    const payload = line.slice(5).trim();
    if (payload.startsWith('{')) return JSON.parse(payload);
  }
  throw new Error(`No JSON-RPC payload found: ${text.slice(0, 240)}`);
}

async function fetchWithRetry(url, init, label) {
  let last;
  for (let attempt = 1; attempt <= 6; attempt++) {
    try {
      const response = await fetch(url, init);
      if (response.ok) return response;
      last = new Error(`${label} HTTP ${response.status}: ${(await response.text()).slice(0, 500)}`);
    } catch (error) {
      last = error;
    }
    if (attempt < 6) await new Promise((resolve) => setTimeout(resolve, attempt * 3000));
  }
  throw last;
}

async function rpc(method, params = undefined) {
  const payload = { jsonrpc: '2.0', id: id++, method };
  if (params !== undefined) payload.params = params;
  const response = await fetchWithRetry(MCP, {
    method: 'POST',
    headers: {
      accept: 'application/json, text/event-stream',
      'content-type': 'application/json',
      'cache-control': 'no-cache',
    },
    body: JSON.stringify(payload),
  }, method);
  const text = await response.text();
  const decoded = decodeRpc(text);
  if (decoded.error) throw new Error(`${method} RPC error: ${JSON.stringify(decoded.error)}`);
  return decoded.result;
}

function firstText(result) {
  const contents = result?.contents || [];
  for (const item of contents) {
    if (typeof item?.text === 'string') return item.text;
  }
  return '';
}

const initialized = await rpc('initialize', {
  protocolVersion: '2025-06-18',
  capabilities: {},
  clientInfo: { name: 'digi-fae-host-bridge-runtime-canary', version: '1.0.0' },
});
if (initialized?.serverInfo?.version !== EXPECTED_VERSION) {
  throw new Error(`version mismatch: ${initialized?.serverInfo?.version}`);
}

const tools = await rpc('tools/list');
const toolNames = (tools?.tools || []).map((tool) => tool.name).sort();
if (JSON.stringify(toolNames) !== JSON.stringify(EXPECTED_TOOLS)) {
  throw new Error(`tool denominator mismatch: ${JSON.stringify(toolNames)}`);
}

const resources = await rpc('resources/list');
const resourceUris = (resources?.resources || []).map((resource) => resource.uri).sort();
if (JSON.stringify(resourceUris) !== JSON.stringify(EXPECTED_RESOURCES)) {
  throw new Error(`resource denominator mismatch: ${JSON.stringify(resourceUris)}`);
}

const healthCall = await rpc('tools/call', { name: 'digi_fae_health', arguments: {} });
const health = healthCall?.structuredContent || {};
if (health.version !== EXPECTED_VERSION || health.writes !== false) {
  throw new Error(`health mismatch: ${JSON.stringify(health)}`);
}

const ui = await rpc('resources/read', { uri: 'ui://digi-fae/hud/v3.html' });
const html = firstText(ui);
if (!html) throw new Error('UI resource missing text/html body');
if (!html.includes('SOURCE_CELL=104')) throw new Error('UI marker SOURCE_CELL=104 missing');
if (!html.includes('window.openai')) throw new Error('window.openai bridge marker missing');

const match = html.match(/data:image\/webp;base64,([A-Za-z0-9+/=]+)/);
if (!match) throw new Error('embedded WebP data URI not found');
const atlas = Buffer.from(match[1], 'base64');
if (atlas.length < 12 || atlas.subarray(0, 4).toString('ascii') !== 'RIFF' || atlas.subarray(8, 12).toString('ascii') !== 'WEBP') {
  throw new Error('embedded atlas is not RIFF/WEBP');
}
const atlasSha = crypto.createHash('sha256').update(atlas).digest('hex');
if (atlasSha !== EXPECTED_ATLAS_SHA) throw new Error(`atlas SHA mismatch: ${atlasSha}`);

console.log('DIGI_FAE_HOST_BRIDGE_RUNTIME_CANARY PASS');
console.log(JSON.stringify({
  schema: 'digi-fae.host-bridge.runtime-canary.v1',
  state: 'PASS',
  bridge: base,
  mcp: MCP,
  version: initialized.serverInfo.version,
  tools: toolNames,
  resources: resourceUris,
  writes: health.writes,
  atlas_bytes: atlas.length,
  atlas_sha256: atlasSha,
  effect_authority: false,
  chatgpt_visible_render_proven: false,
  automatic_host_invocation_proven: false,
}, null, 2));
