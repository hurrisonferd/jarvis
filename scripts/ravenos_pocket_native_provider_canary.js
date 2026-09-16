'use strict';
const path=require('path');
global.CustomEvent=class CustomEvent{constructor(type,init={}){this.type=type;this.detail=init.detail;}};
const listeners={};
global.document={hidden:false,addEventListener:(name,fn)=>{listeners[name]=fn;}};
global.window={
  dispatchEvent:()=>{},
  addEventListener:(name,fn)=>{listeners[name]=fn;},
  chrome:undefined,
  RavenOSPocketAndroid:undefined
};
require(path.join(__dirname,'..','ravenos-pocket-native-provider.js'));
const bridge=window.RavenOSPocketNative;
if(!bridge||bridge.schema!=='ravenos.pocket.native-provider-bridge.v1')throw new Error('BRIDGE_MISSING');
const now=Date.now();
const base={
  schema:'ravenos.pocket.native-scene.v1',
  provider:'WINDOWS_GOBLIN_VISION',
  provider_version:'0.69.6',
  sequence:1,
  captured_at_ms:now,
  fresh_for_ms:10000,
  effect_authority:false,
  capabilities:['UIA_CONTROL_VIEW','DESKTOP_DELTA'],
  scene:{available:true,sensitive:false,quiet_zone:false,task:'PLAYING',subject:'TEST GAME',summary:'owner-safe semantic scene',confidence:92,source:'UIA'},
  proof:{transport:'WEBVIEW2_WEB_MESSAGE',host_attested:true,source_current:'GoblinVision/CURRENT-ROUTER.v1.json',effect_authority:false}
};
function clone(x){return JSON.parse(JSON.stringify(x));}
function expectOk(x,transport){const r=bridge.ingest(x,transport);if(!r.ok)throw new Error('EXPECTED_OK:'+r.reason);}
function expectReject(x,transport,reason){const r=bridge.ingest(x,transport);if(r.ok||r.reason!==reason)throw new Error(`EXPECTED_${reason}:${JSON.stringify(r)}`);}
expectOk(clone(base),'WEBVIEW2_WEB_MESSAGE');
expectReject(clone(base),'WEBVIEW2_WEB_MESSAGE','REPLAY_OR_REORDER');
let x=clone(base);x.sequence=2;x.effect_authority=true;expectReject(x,'WEBVIEW2_WEB_MESSAGE','EFFECT_AUTHORITY');
x=clone(base);x.sequence=2;x.capabilities.push('ARBITRARY_PROCESS_CONTROL');expectReject(x,'WEBVIEW2_WEB_MESSAGE','CAPABILITIES');
x=clone(base);x.sequence=2;x.provider='ANDROID_LAUNCHER';x.capabilities=['WHOLE_PHONE_SCENE'];x.proof.transport='WEBVIEW2_WEB_MESSAGE';expectReject(x,'WEBVIEW2_WEB_MESSAGE','WINDOWS_PROVIDER_MISMATCH');
x=clone(base);x.sequence=2;x.scene.sensitive=true;x.scene.available=true;expectReject(x,'WEBVIEW2_WEB_MESSAGE','SENSITIVE_CONTENT');
x=clone(base);x.sequence=2;x.captured_at_ms=now-20000;x.fresh_for_ms=1000;expectReject(x,'WEBVIEW2_WEB_MESSAGE','STALE_OR_FUTURE');
x=clone(base);x.sequence=2;x.extra='NOPE';expectReject(x,'WEBVIEW2_WEB_MESSAGE','TOP_KEYS');
const state=bridge.snapshot();
if(!state.windows.connected||state.android.connected||state.effect_authority!==false)throw new Error('STATE_CEILING_BROKEN');
console.log('RAVENOS_POCKET_NATIVE_PROVIDER_CANARY PASS');
console.log(JSON.stringify({accepted:state.accepted,rejected:state.rejected,windows_connected:state.windows.connected,android_connected:state.android.connected,effect_authority:state.effect_authority}));
