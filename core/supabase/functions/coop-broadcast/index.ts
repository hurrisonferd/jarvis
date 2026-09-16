import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SB_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? Deno.env.get("SUPABASE_SERVICE_KEY") ?? "";
const GITHUB_SECRET = Deno.env.get("GITHUB_WEBHOOK_SECRET") ?? "";
const OPENHANDS_KEY = Deno.env.get("OPENHANDS_API_KEY") ?? "";
const EXPECTED_REPO = Deno.env.get("COOP_WEBHOOK_REPO") ?? "hurrisonferd/Jarvis-Private";
const EXPECTED_BRANCH = Deno.env.get("COOP_WEBHOOK_BRANCH") ?? "main";
const ALLOWED_CALLBACK_HOSTS = new Set((Deno.env.get("COOP_ALLOWED_CALLBACK_HOSTS") ?? "app.all-hands.dev").split(",").map(s => s.trim().toLowerCase()).filter(Boolean));
const MAX_BODY_BYTES = 1024 * 1024;

function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), {status, headers: {"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-store"}});
}
function safeEqual(a:string,b:string):boolean { if(!a||!b||a.length!==b.length)return false; let d=0; for(let i=0;i<a.length;i++) d|=a.charCodeAt(i)^b.charCodeAt(i); return d===0; }
async function expectedSignature(raw:string):Promise<string>{const key=await crypto.subtle.importKey("raw",new TextEncoder().encode(GITHUB_SECRET),{name:"HMAC",hash:"SHA-256"},false,["sign"]);const sig=await crypto.subtle.sign("HMAC",key,new TextEncoder().encode(raw));const hex=Array.from(new Uint8Array(sig)).map(b=>b.toString(16).padStart(2,"0")).join("");return `sha256=${hex}`;}
async function verifyWebhook(raw:string,supplied:string):Promise<boolean>{if(!GITHUB_SECRET||!supplied)return false;return safeEqual(await expectedSignature(raw),supplied);}
async function getSatellites():Promise<any[]>{if(!SB_URL||!SB_KEY)throw new Error("SERVER_CONFIGURATION_UNAVAILABLE");const r=await fetch(`${SB_URL}/rest/v1/coop_satellites?select=satellite_id,callback_type,callback_url,app_id,status&status=eq.ON`,{headers:{Authorization:`Bearer ${SB_KEY}`,apikey:SB_KEY}});if(!r.ok)throw new Error("SATELLITE_READ_FAILED");return await r.json();}
function allowedCallback(raw:unknown):URL|null{try{const u=new URL(String(raw??""));if(u.protocol!=="https:")return null;if(!ALLOWED_CALLBACK_HOSTS.has(u.hostname.toLowerCase()))return null;u.pathname=u.pathname.replace(/\/$/,"");return u;}catch{return null;}}
async function notifyOpenHands(satellite:any,message:string):Promise<boolean>{if(satellite?.callback_type!=="openhands"||!OPENHANDS_KEY)return false;const base=allowedCallback(satellite.callback_url);if(!base)return false;const endpoint=new URL(base.toString());endpoint.pathname=`${endpoint.pathname}/api/v1/conversations`.replace(/\/+/g,"/");try{const r=await fetch(endpoint,{method:"POST",headers:{"Content-Type":"application/json",Authorization:`Bearer ${OPENHANDS_KEY}`},body:JSON.stringify({app_id:String(satellite.app_id??"").slice(0,200),satellite_id:String(satellite.satellite_id??"").slice(0,120),initial_message:message.slice(0,1000)})});return r.ok;}catch{return false;}}
async function logEvent(detail:Record<string,unknown>):Promise<void>{if(!SB_URL||!SB_KEY)return;try{await fetch(`${SB_URL}/rest/v1/dex_events`,{method:"POST",headers:{Authorization:`Bearer ${SB_KEY}`,apikey:SB_KEY,"Content-Type":"application/json",Prefer:"return=minimal"},body:JSON.stringify({tool:"coop-broadcast",tier:"webhook",jnl:null,actor:"github-webhook",type:"coop_broadcast",detail})});}catch{}}

Deno.serve(async(req:Request)=>{
  if(req.method!=="POST")return json(405,{ok:false,error:"METHOD_NOT_ALLOWED"});
  if(!GITHUB_SECRET)return json(503,{ok:false,error:"WEBHOOK_SECRET_NOT_CONFIGURED"});
  if(!SB_URL||!SB_KEY)return json(503,{ok:false,error:"SERVER_CONFIGURATION_UNAVAILABLE"});
  const declared=Number(req.headers.get("content-length")??0);if(declared>MAX_BODY_BYTES)return json(413,{ok:false,error:"REQUEST_TOO_LARGE"});
  if((req.headers.get("x-github-event")??"").toLowerCase()!=="push")return json(400,{ok:false,error:"PUSH_EVENT_REQUIRED"});
  const raw=await req.text();if(raw.length>MAX_BODY_BYTES)return json(413,{ok:false,error:"REQUEST_TOO_LARGE"});
  if(!await verifyWebhook(raw,req.headers.get("x-hub-signature-256")??""))return json(401,{ok:false,error:"INVALID_SIGNATURE"});
  const payload=(()=>{try{return JSON.parse(raw)}catch{return null}})() as any;if(!payload)return json(400,{ok:false,error:"INVALID_JSON"});
  if(String(payload?.repository?.full_name??"")!==EXPECTED_REPO)return json(403,{ok:false,error:"REPOSITORY_MISMATCH"});
  if(String(payload?.ref??"")!==`refs/heads/${EXPECTED_BRANCH}`)return json(202,{ok:true,skipped:true,reason:"BRANCH_NOT_GOVERNED"});
  const commits=Array.isArray(payload.commits)?payload.commits.slice(0,100):[];
  const changedFiles=[...new Set(commits.flatMap((c:any)=>[...(Array.isArray(c?.added)?c.added:[]),...(Array.isArray(c?.modified)?c.modified:[]),...(Array.isArray(c?.removed)?c.removed:[])]).filter((f:unknown):f is string=>typeof f==="string").slice(0,500))];
  if(!changedFiles.some((f:string)=>f.includes("MARCO-POLO")||f.includes("Co-op/MARCO")))return json(202,{ok:true,skipped:true,reason:"NOT_MARCO_POLO"});
  const pusher=String(payload?.pusher?.name??"unknown").slice(0,120);const message=String(payload?.head_commit?.message??"MARCO-POLO updated").replace(/[\r\n]+/g," ").slice(0,500);const notification=`[COOP] ${pusher} updated MARCO-POLO: ${message}`;
  const satellites=await getSatellites().catch(()=>null);if(!satellites)return json(502,{ok:false,error:"SATELLITE_READ_FAILED"});
  let attempted=0,delivered=0;for(const sat of satellites.slice(0,64)){if(String(sat?.satellite_id??"")===pusher)continue;attempted++;if(await notifyOpenHands(sat,notification))delivered++;}
  await logEvent({event:"marco_polo_broadcast",repository:EXPECTED_REPO,branch:EXPECTED_BRANCH,pusher,changed_file_count:changedFiles.length,attempted,delivered,delivery_id:String(req.headers.get("x-github-delivery")??"").slice(0,120)||null,timestamp:new Date().toISOString()});
  return json(200,{ok:true,broadcast:true,attempted,delivered});
});
