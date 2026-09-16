(() => {
'use strict';
const SCHEMA='ravenos.pocket.native-scene.v1';
const REQUEST_SCHEMA='ravenos.pocket.host-request.v1';
const MAX_FUTURE_MS=30000,MAX_FRESH_MS=15000,ANDROID_POLL_MS=1500;
const PROVIDERS={
  ANDROID_LAUNCHER:new Set(['NOTIFICATION_SENSE','MEDIA_SESSION_SENSE','USAGE_SENSE','OWNER_ARMED_ACCESSIBILITY_READ','WHOLE_PHONE_SCENE']),
  WINDOWS_GOBLIN_VISION:new Set(['WGC_CAPTURE','UIA_CONTROL_VIEW','WINDOWS_OCR','DESKTOP_DELTA','PROCESS_AUDIO_SCOPE','NATIVE_PRESENCE','RESOURCE_PRESSURE','HDR_SENSE','OWNER_MODEL_VISUAL_CRITIC','GAME_BAR_SURFACE'])
};
const TOP=new Set(['schema','provider','provider_version','sequence','captured_at_ms','fresh_for_ms','effect_authority','capabilities','scene','proof']);
const SCENE=new Set(['available','sensitive','quiet_zone','task','subject','summary','confidence','source']);
const PROOF=new Set(['transport','host_attested','source_current','effect_authority']);
const state={initialized:false,lastSeq:{ANDROID_LAUNCHER:-1,WINDOWS_GOBLIN_VISION:-1},latest:{},accepted:0,rejected:0,lastReject:'',timer:null};
const exact=(o,keys)=>o&&typeof o==='object'&&!Array.isArray(o)&&Object.keys(o).length===keys.size&&Object.keys(o).every(k=>keys.has(k));
const bounded=s=>typeof s==='string'&&s.length<=512;
function reject(reason){state.rejected++;state.lastReject=String(reason||'REJECTED').slice(0,160);return {ok:false,reason:state.lastReject};}
function validate(raw,transport){
  let x=raw;try{if(typeof raw==='string')x=JSON.parse(raw);}catch{return reject('INVALID_JSON');}
  if(!exact(x,TOP))return reject('TOP_KEYS');
  if(x.schema!==SCHEMA)return reject('SCHEMA');
  if(!PROVIDERS[x.provider])return reject('PROVIDER');
  if(x.effect_authority!==false)return reject('EFFECT_AUTHORITY');
  if(typeof x.provider_version!=='string'||x.provider_version.length<1||x.provider_version.length>40)return reject('PROVIDER_VERSION');
  if(!Number.isSafeInteger(x.sequence)||x.sequence<0)return reject('SEQUENCE');
  if(x.sequence<=state.lastSeq[x.provider])return reject('REPLAY_OR_REORDER');
  if(!Number.isSafeInteger(x.captured_at_ms)||!Number.isSafeInteger(x.fresh_for_ms)||x.fresh_for_ms<1||x.fresh_for_ms>MAX_FRESH_MS)return reject('FRESHNESS');
  const now=Date.now(),age=now-x.captured_at_ms;if(age>x.fresh_for_ms||age<-MAX_FUTURE_MS)return reject('STALE_OR_FUTURE');
  if(!Array.isArray(x.capabilities)||x.capabilities.length>24||!x.capabilities.every(c=>typeof c==='string'&&PROVIDERS[x.provider].has(c)))return reject('CAPABILITIES');
  if(!exact(x.scene,SCENE))return reject('SCENE_KEYS');
  const s=x.scene;if(typeof s.available!=='boolean'||typeof s.sensitive!=='boolean'||typeof s.quiet_zone!=='boolean')return reject('SCENE_FLAGS');
  if(!Number.isInteger(s.confidence)||s.confidence<0||s.confidence>100)return reject('CONFIDENCE');
  if(![s.task,s.subject,s.summary,s.source].every(bounded))return reject('SCENE_TEXT');
  if(s.sensitive&&(s.available||s.subject||s.summary))return reject('SENSITIVE_CONTENT');
  if(!exact(x.proof,PROOF)||x.proof.effect_authority!==false||x.proof.host_attested!==true)return reject('PROOF');
  if(typeof x.proof.transport!=='string'||x.proof.transport!==transport)return reject('TRANSPORT');
  if(!bounded(x.proof.source_current))return reject('SOURCE_CURRENT');
  if(transport==='ANDROID_JS_INTERFACE'&&x.provider!=='ANDROID_LAUNCHER')return reject('ANDROID_PROVIDER_MISMATCH');
  if(transport==='WEBVIEW2_WEB_MESSAGE'&&x.provider!=='WINDOWS_GOBLIN_VISION')return reject('WINDOWS_PROVIDER_MISMATCH');
  return {ok:true,value:Object.freeze(x)};
}
function ingest(raw,transport){const r=validate(raw,transport);if(!r.ok)return r;const x=r.value;state.lastSeq[x.provider]=x.sequence;state.latest[x.provider]=x;state.accepted++;window.dispatchEvent(new CustomEvent('ravenos:native-scene',{detail:x}));return {ok:true,provider:x.provider,sequence:x.sequence};}
function webview2(){return !!(window.chrome&&window.chrome.webview&&typeof window.chrome.webview.postMessage==='function'&&typeof window.chrome.webview.addEventListener==='function');}
function android(){return !!(window.RavenOSPocketAndroid&&typeof window.RavenOSPocketAndroid.snapshot==='function');}
function requestWindowsHello(){if(!webview2())return;try{window.chrome.webview.postMessage({schema:REQUEST_SCHEMA,type:'HELLO',effect_authority:false});}catch{reject('WEBVIEW2_HELLO_FAILED');}}
function pollAndroid(){if(!android()||document.hidden)return;try{const raw=window.RavenOSPocketAndroid.snapshot();if(raw)ingest(raw,'ANDROID_JS_INTERFACE');}catch{reject('ANDROID_SNAPSHOT_FAILED');}}
function init(){if(state.initialized)return;state.initialized=true;if(webview2()){window.chrome.webview.addEventListener('message',ev=>ingest(ev.data,'WEBVIEW2_WEB_MESSAGE'));requestWindowsHello();}if(android()){pollAndroid();state.timer=setInterval(pollAndroid,ANDROID_POLL_MS);}document.addEventListener('visibilitychange',()=>{if(!document.hidden)pollAndroid();});}
function snapshot(){const a=state.latest.ANDROID_LAUNCHER,w=state.latest.WINDOWS_GOBLIN_VISION;return {schema:'ravenos.pocket.native-provider-state.v1',accepted:state.accepted,rejected:state.rejected,last_reject:state.lastReject,android:{bridge_present:android(),connected:!!a,latest:a||null},windows:{bridge_present:webview2(),connected:!!w,latest:w||null},effect_authority:false};}
window.RavenOSPocketNative=Object.freeze({schema:'ravenos.pocket.native-provider-bridge.v1',init,ingest,snapshot});
})();