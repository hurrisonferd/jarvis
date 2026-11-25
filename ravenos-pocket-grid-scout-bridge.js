(() => {
'use strict';
const SCHEMA='ravenos.pocket.grid-scout-result.v1';
const MAX_AGE_MS=15000,MAX_FUTURE_MS=30000,MAX_CANDIDATES=40;
const state={latest:null,accepted:0,rejected:0,lastReject:'',lastSeq:-1};
const TOP=['schema','provider','provider_version','sequence','captured_at_ms','fresh_for_ms','effect_authority','state','sources','candidates','proof'];
const SOURCE_KEYS=['mcp_registry','huggingface_hub'];
const CANDIDATE_KEYS=['participant_type','name','version','author','license','description','pipeline_tag','library_name','downloads','likes','last_modified','gated','access_mode','source_uri','discovery_state','trust_state','contact_state','invocation_state'];
const exact=(o,keys)=>!!o&&typeof o==='object'&&!Array.isArray(o)&&Object.keys(o).length===keys.length&&Object.keys(o).every(k=>keys.includes(k));
const bounded=(s,n=500)=>typeof s==='string'&&s.length<=n;
function reject(reason){state.rejected++;state.lastReject=reason;return {ok:false,reason};}
function safeUri(raw){
 try{const u=new URL(raw);return u.protocol==='https:'&&['registry.modelcontextprotocol.io','huggingface.co'].includes(u.hostname)&&!u.username&&!u.password?u.href:'';}catch{return '';}
}
function validate(raw,transport){
 let x=raw;try{if(typeof raw==='string')x=JSON.parse(raw);}catch{return reject('INVALID_JSON');}
 if(!exact(x,TOP))return reject('TOP_KEYS');
 if(x.schema!==SCHEMA||x.provider!=='RAVENOS_POCKET_GRID_SCOUT')return reject('SCHEMA_OR_PROVIDER');
 if(!['ANDROID_JS_INTERFACE','WEBVIEW2_WEB_MESSAGE'].includes(transport))return reject('TRANSPORT');
 if(x.effect_authority!==false)return reject('EFFECT_AUTHORITY');
 if(typeof x.provider_version!=='string'||!bounded(x.provider_version,40))return reject('VERSION');
 if(!Number.isSafeInteger(x.sequence)||x.sequence<=state.lastSeq)return reject('REPLAY_OR_REORDER');
 if(!Number.isSafeInteger(x.captured_at_ms)||!Number.isSafeInteger(x.fresh_for_ms)||x.fresh_for_ms<1||x.fresh_for_ms>MAX_AGE_MS)return reject('FRESHNESS_FIELDS');
 const age=Date.now()-x.captured_at_ms;if(age>x.fresh_for_ms||age<-MAX_FUTURE_MS)return reject('STALE_OR_FUTURE');
 if(!['READY','PARTIAL','UNAVAILABLE','HOLD'].includes(x.state))return reject('STATE');
 if(!exact(x.sources,SOURCE_KEYS))return reject('SOURCE_KEYS');
 for(const k of SOURCE_KEYS){const s=x.sources[k];if(!exact(s,['status','count'])||!['READ_OK','UNAVAILABLE','NOT_QUERIED'].includes(s.status)||!Number.isInteger(s.count)||s.count<0||s.count>MAX_CANDIDATES)return reject('SOURCE_STATE');}
 if(!Array.isArray(x.candidates)||x.candidates.length>MAX_CANDIDATES)return reject('CANDIDATE_COUNT');
 for(const c of x.candidates){
  if(!exact(c,CANDIDATE_KEYS))return reject('CANDIDATE_KEYS');
  if(!['EXTERNAL_MCP_SERVER','OPEN_WEIGHT_MODEL'].includes(c.participant_type)||!bounded(c.name,180)||!bounded(c.version,80)||!bounded(c.author,120)||!bounded(c.license,80)||!bounded(c.description,700)||!bounded(c.pipeline_tag,100)||!bounded(c.library_name,100)||!bounded(c.last_modified,80))return reject('CANDIDATE_TEXT');
  if(c.downloads!==null&&(!Number.isSafeInteger(c.downloads)||c.downloads<0))return reject('DOWNLOADS');
  if(c.likes!==null&&(!Number.isSafeInteger(c.likes)||c.likes<0))return reject('LIKES');
  if(typeof c.gated!=='boolean'||!['GATED','PUBLIC_READ','UNKNOWN'].includes(c.access_mode))return reject('ACCESS_MODE');
  if(!safeUri(c.source_uri))return reject('SOURCE_URI');
  if(c.discovery_state!=='DISCOVERED'||c.trust_state!=='UNASSESSED'||c.contact_state!=='NOT_CONTACTED'||c.invocation_state!=='NOT_INVOKED')return reject('TRUST_BOUNDARY');
 }
 if(!exact(x.proof,['transport','host_attested','source_current'])||x.proof.transport!==transport||x.proof.host_attested!==true||!bounded(x.proof.source_current,160))return reject('PROOF');
 return {ok:true,value:Object.freeze(x)};
}
function ingest(raw,transport){const r=validate(raw,transport);if(!r.ok)return r;state.lastSeq=r.value.sequence;state.latest=r.value;state.accepted++;window.dispatchEvent(new CustomEvent('ravenos:grid-scout', {detail:r.value}));return {ok:true,sequence:r.value.sequence};}
function snapshot(){return {schema:'ravenos.pocket.grid-scout-bridge-state.v1',latest:state.latest,accepted:state.accepted,rejected:state.rejected,last_reject:state.lastReject,effect_authority:false};}
window.RavenOSGridScout=Object.freeze({schema:SCHEMA,ingest,snapshot});
})();