import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const BASE = Deno.env.get("BIFROST_BASE") || "https://generativelanguage.googleapis.com";
const MODEL = Deno.env.get("BIFROST_MODEL") || "gemini-2.0-flash";
const KEY = Deno.env.get("BIFROST_KEY") || Deno.env.get("LLM_API_KEY") || Deno.env.get("GEMINI_API_KEY") || "";
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || Deno.env.get("SUPABASE_SERVICE_KEY") || "";
const ALLOWED_ORIGIN = (Deno.env.get("RAVEN_ALLOWED_ORIGIN") || "").trim();
const MAX_QUERY_CHARS = 3000;
const MAX_BODY_BYTES = 16 * 1024;

type Source = { title: string; uri: string };
type Reach = { answer: string; sources: Source[]; grounded: boolean };

function headers(): Record<string,string> {
  const h: Record<string,string> = {
    "Access-Control-Allow-Headers":"authorization, content-type",
    "Access-Control-Allow-Methods":"POST, OPTIONS",
    "Content-Type":"application/json; charset=utf-8",
    "Cache-Control":"no-store",
  };
  if (ALLOWED_ORIGIN) h["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN;
  return h;
}
function json(status:number, body:Record<string,unknown>) { return new Response(JSON.stringify(body), {status, headers:headers()}); }
function bearer(req:Request):string { const raw=req.headers.get("authorization")??""; return raw.toLowerCase().startsWith("bearer ")?raw.slice(7).trim():""; }
function safeEqual(a:string,b:string):boolean { if(!a||!b||a.length!==b.length)return false; let d=0; for(let i=0;i<a.length;i++) d|=a.charCodeAt(i)^b.charCodeAt(i); return d===0; }
function internalAuthorized(req:Request):boolean { return !!SERVICE_KEY && safeEqual(bearer(req), SERVICE_KEY); }
function endpoint():string { return `${BASE.replace(/\/$/,"")}/v1beta/models/${MODEL}:generateContent`; }
function buildRequest(query:string):Record<string,unknown> { return { contents:[{role:"user",parts:[{text:query.slice(0,MAX_QUERY_CHARS)}]}], tools:[{google_search:{}}] }; }
function parseGrounded(resp:any):Reach {
  const cand=resp?.candidates?.[0];
  const answer=(cand?.content?.parts??[]).map((p:any)=>p?.text).filter((t:unknown):t is string=>typeof t==="string"&&t.length>0).join("").trim().slice(0,12000);
  const chunks=cand?.groundingMetadata?.groundingChunks??[];
  const seen=new Set<string>(); const sources:Source[]=[];
  for(const c of chunks){const uri=c?.web?.uri;if(typeof uri==="string"&&uri&&uri.startsWith("http")&&!seen.has(uri)){seen.add(uri);sources.push({title:String(c?.web?.title??uri).slice(0,120),uri:uri.slice(0,2000)});if(sources.length>=8)break;}}
  return {answer,sources,grounded:sources.length>0};
}
function summary(r:Reach,maxChars=1200):string { const body=r.answer.slice(0,maxChars); const src=r.sources.slice(0,4).map((s,i)=>`[${i+1}] ${s.title} — ${s.uri}`).join("\n"); return src?`${body}\n\nSOURCES:\n${src}`:body; }

Deno.serve(async(req:Request)=>{
  if(req.method==="OPTIONS")return new Response(null,{status:204,headers:headers()});
  if(req.method!=="POST")return json(405,{ok:false,error:"METHOD_NOT_ALLOWED"});
  if(!internalAuthorized(req))return json(SERVICE_KEY?403:503,{ok:false,error:SERVICE_KEY?"FORBIDDEN":"SERVER_AUTH_NOT_CONFIGURED"});
  if(!KEY)return json(503,{ok:false,error:"PROVIDER_NOT_CONFIGURED"});
  const declared=Number(req.headers.get("content-length")??0);if(declared>MAX_BODY_BYTES)return json(413,{ok:false,error:"REQUEST_TOO_LARGE"});
  const body=await req.json().catch(()=>null) as Record<string,unknown>|null;if(!body)return json(400,{ok:false,error:"INVALID_JSON"});
  const query=String(body.query??"").trim();if(!query)return json(400,{ok:false,error:"QUERY_REQUIRED"});if(query.length>MAX_QUERY_CHARS)return json(413,{ok:false,error:"QUERY_TOO_LARGE"});
  try{
    const r=await fetch(endpoint(),{method:"POST",headers:{"x-goog-api-key":KEY,"Content-Type":"application/json"},body:JSON.stringify(buildRequest(query))});
    if(!r.ok)return json(502,{ok:false,error:"UPSTREAM_REJECTED",provider_status:r.status});
    const reach=parseGrounded(await r.json());
    return json(200,{ok:true,query,answer:reach.answer,sources:reach.sources,grounded:reach.grounded,summary:summary(reach)});
  }catch{return json(502,{ok:false,error:"UPSTREAM_FAILURE"});}
});
