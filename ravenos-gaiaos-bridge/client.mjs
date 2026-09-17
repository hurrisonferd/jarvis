const DEFAULT_URL = "https://gaiaos-loader-api.onrender.com/mcp";
export const GAIAOS_TOOL_ALLOWLIST = Object.freeze(["gaia","gaia_selftest","load_gaiaos","gaia_council","gaia_dispatch","gaia_operator","gaia_brain","gaia_context"]);
function decodeRpcBody(text){const t=String(text??"").trim();if(!t)return null;if(t.startsWith("{"))return JSON.parse(t);for(const line of t.split(/\r?\n/)){if(!line.startsWith("data:"))continue;const p=line.slice(5).trim();if(p.startsWith("{"))return JSON.parse(p);}throw new Error(`No JSON-RPC payload found: ${t.slice(0,240)}`);}
export function unwrapToolResult(result){if(!result||typeof result!=="object")return result;if(result.structuredContent!==undefined)return result.structuredContent;for(const item of Array.isArray(result.content)?result.content:[]){if(item?.type!=="text"||typeof item.text!=="string")continue;const text=item.text.trim();if(!text)continue;try{return JSON.parse(text);}catch{return text;}}return result;}
export class GaiaOSBridgeClient{
constructor(options={}){this.url=String(options.url||process.env.GAIAOS_MCP_URL||DEFAULT_URL).replace(/\/+$/,"");this.bearerToken=options.bearerToken||process.env.GAIAOS_MCP_BEARER_TOKEN||"";this.timeoutMs=Number(options.timeoutMs||process.env.GAIAOS_MCP_TIMEOUT_MS||20000);this.sessionId="";this.nextId=1;this.initialized=false;this.serverInfo=null;}
headers(){const h={accept:"application/json, text/event-stream","content-type":"application/json"};if(this.bearerToken)h.authorization=`Bearer ${this.bearerToken}`;if(this.sessionId)h["mcp-session-id"]=this.sessionId;return h;}
async rpc(method,params=undefined){const c=new AbortController();const timer=setTimeout(()=>c.abort(),this.timeoutMs);const payload={jsonrpc:"2.0",id:this.nextId++,method};if(params!==undefined)payload.params=params;try{const r=await fetch(this.url,{method:"POST",headers:this.headers(),body:JSON.stringify(payload),signal:c.signal});const sid=r.headers.get("mcp-session-id");if(sid)this.sessionId=sid;const text=await r.text();if(!r.ok)throw new Error(`${method} HTTP ${r.status}: ${text.slice(0,500)}`);const d=decodeRpcBody(text);if(!d)throw new Error(`${method} returned an empty MCP response`);if(d.error)throw new Error(`${method} RPC error: ${JSON.stringify(d.error)}`);return d.result;}catch(e){if(e?.name==="AbortError")throw new Error(`${method} timed out after ${this.timeoutMs}ms`);throw e;}finally{clearTimeout(timer);}}
async initialize(){if(this.initialized)return this.serverInfo;const r=await this.rpc("initialize",{protocolVersion:"2025-06-18",capabilities:{},clientInfo:{name:"ravenos-gaiaos-bridge",version:"0.2.0"}});this.initialized=true;this.serverInfo=r?.serverInfo||null;return this.serverInfo;}
async listTools(){await this.initialize();return this.rpc("tools/list");}
async callTool(name,args={}){await this.initialize();if(!GAIAOS_TOOL_ALLOWLIST.includes(name))throw new Error(`GaiaOSBridge refuses non-allowlisted tool: ${name}`);const raw=await this.rpc("tools/call",{name,arguments:args??{}});return{raw,value:unwrapToolResult(raw)};}
gaia(request,requestedMembers=[],maxMembers=3,includeContext=true,contextLimit=6,contextDepth=1){return this.callTool("gaia",{request,requested_members:requestedMembers,max_members:maxMembers,include_context:includeContext,context_limit:contextLimit,context_depth:contextDepth});}
selftest(){return this.callTool("gaia_selftest");}
load(){return this.callTool("load_gaiaos");}
council(){return this.callTool("gaia_council");}
dispatch(signals,requestedMembers=[],maxMembers=3){return this.callTool("gaia_dispatch",{signals,requested_members:requestedMembers,max_members:maxMembers});}
operator(member){return this.callTool("gaia_operator",{member});}
brain(){return this.callTool("gaia_brain");}
context(subject,limit=10,depth=1){return this.callTool("gaia_context",{subject,limit,depth});}
}
export function createGaiaOSBridgeClient(options={}){return new GaiaOSBridgeClient(options);}
