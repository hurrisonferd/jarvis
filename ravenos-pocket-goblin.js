(() => {
'use strict';
const MAX_EPISODES=32;
const state={seq:0,episodes:[],latest:null,listener:null,initialized:false,lastSpoken:[]};
const quietFamilies=new Set(['CURSOR_MOVE','SCROLL']);
const lines={
  BOOT:[
    'Cartridge bus awake. Thirteen tiny departments are now pretending this is a reasonable handheld.',
    'Pocket BIOS is up. Effect budget remains a majestic zero.',
    'Civilization shell awake. Nobody has been granted wizard powers by a loading screen.'
  ],
  CARTRIDGE_OPEN:[
    '{subject} cartridge seated. Tiny machine, extremely unreasonable job description.',
    'Opening {subject}. The Game Boy continues to acquire responsibilities nobody warned Nintendo about.',
    '{subject} online as a view. View, not owner. We have learned at least one lesson.'
  ],
  CARTRIDGE_BACK:[
    'Back to the cartridge rack. Nothing exploded, which is becoming suspicious.',
    'Returning home. The tiny office elevator has completed another shift.'
  ],
  NATIVE_SCENE:[
    'Native scene arrived from {subject}. The tiny office has acquired an actual window.',
    '{subject} handed Pocket a fresh scene packet. Commentary is still downstream of evidence.',
    'Scene accepted from {subject}. Goblin eyesight has paperwork now.'
  ],
  PROVIDER_HOLD:[
    '{subject} provider packet was held. Better a blind goblin than a fictional one.',
    'Native provider hold: {subject}. Sensor proof does not get promoted by enthusiasm.'
  ],
  SYNC_START:[
    'Reseating the public packet and cartridge registry. Please keep arms inside the causality bus.',
    'Sync started. Checking whether reality still agrees with the menu.'
  ],
  SYNC_PASS:[
    'Packet and cartridges agree. No smoke. Suspiciously professional.',
    'Sync settled. The haunted calculator has paperwork now.'
  ],
  SYNC_HOLD:[
    'Sync refused entry. Good. A haunted dashboard should still have locks.',
    'Packet held. We are doing the rare engineering technique called not making things up.'
  ],
  BROWSER_OFFLINE:[
    'Network fell through a trapdoor. Pocket remains read-only and dramatically less omniscient.',
    'Offline. The civilization bus has become a very fancy local brochure.'
  ],
  BROWSER_ONLINE:[
    'Network restored. The brochure has rejoined civilization.',
    'Online again. Please resume pretending the purple Game Boy is normal infrastructure.'
  ],
  DOCUMENT_HIDDEN:[
    'Pocket went into your pocket. Extremely on-brand.',
    'Screen hidden. Goblin goes quiet instead of narrating the void.'
  ],
  DOCUMENT_VISIBLE:[
    'Pocket visible again. The tiny office has reopened.',
    'Screen back. Resuming from observed page state only.'
  ],
  WINDOW_BLUR:['Window focus left. No external screen state inferred.'],
  WINDOW_FOCUS:['Window focus returned. Browser event, not mind reading.']
};
const faces=['(⌐■_■)','( •̀ᴗ•́ )و','(¬‿¬)','(•̀ᴗ•́)و ̑̑','(ಠ‿ಠ)'];
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
function cleanSubject(v){const s=String(v??'POCKET').replace(/[\r\n\t]+/g,' ').trim();return s.slice(0,64)||'POCKET';}
function choose(list,key){return list[hash(key)%list.length];}
function notify(packet){if(typeof state.listener==='function')state.listener(packet);}
function observe(eventFamily,subject='POCKET',evidenceClass='DIRECT_POCKET_UI_EVENT',meta={}){
  const family=String(eventFamily||'UNKNOWN').toUpperCase();
  const observed=cleanSubject(subject);
  const event={id:`PCK-${String(++state.seq).padStart(5,'0')}`,family,subject:observed,evidence_class:String(evidenceClass||'DIRECT_POCKET_UI_EVENT'),at:new Date().toISOString(),meta:meta&&typeof meta==='object'?meta:{}};
  state.episodes.push(event);if(state.episodes.length>MAX_EPISODES)state.episodes.shift();
  if(quietFamilies.has(family))return null;
  const candidates=lines[family];if(!candidates)return null;
  if(state.lastSpoken.slice(-2).includes(family))return null;
  const key=`${family}|${observed}|${state.seq}`;
  const line=choose(candidates,key).replaceAll('{subject}',observed);
  const packet=Object.freeze({schema:'ravenos.pocket.reaction-packet.v1',event_id:event.id,event_family:family,observed_subject:observed,speaker:'RAVENOS',kaomoji:choose(faces,key+'|face'),line,evidence_class:event.evidence_class,effect_authority:false});
  state.latest=packet;state.lastSpoken.push(family);if(state.lastSpoken.length>8)state.lastSpoken.shift();notify(packet);return packet;
}
function init(listener){
  if(typeof listener==='function')state.listener=listener;
  if(state.initialized)return;state.initialized=true;
  document.addEventListener('visibilitychange',()=>observe(document.hidden?'DOCUMENT_HIDDEN':'DOCUMENT_VISIBLE','POCKET PAGE','BROWSER_STATE'));
  window.addEventListener('focus',()=>observe('WINDOW_FOCUS','POCKET PAGE','BROWSER_STATE'));
  window.addEventListener('blur',()=>observe('WINDOW_BLUR','POCKET PAGE','BROWSER_STATE'));
  window.addEventListener('online',()=>observe('BROWSER_ONLINE','NETWORK','BROWSER_STATE'));
  window.addEventListener('offline',()=>observe('BROWSER_OFFLINE','NETWORK','BROWSER_STATE'));
  window.addEventListener('ravenos:native-scene',ev=>{const x=ev&&ev.detail;if(!x||!x.scene)return;observe('NATIVE_SCENE',`${x.provider} · ${x.scene.task||'SCENE'}`,'NATIVE_PROVIDER_SCENE',{provider:x.provider,sequence:x.sequence,confidence:x.scene.confidence,source:x.scene.source});});
}
function snapshot(){const native=window.RavenOSPocketNative?window.RavenOSPocketNative.snapshot():null;return {episode_count:state.episodes.length,latest:state.latest,episodes:state.episodes.slice(),browser:{online:navigator.onLine,visible:!document.hidden,focused:document.hasFocus()},external_providers:{android_connected:!!(native&&native.android&&native.android.connected),windows_connected:!!(native&&native.windows&&native.windows.connected)},native_provider_state:native};}
window.RavenOSPocketGoblin=Object.freeze({schema:'ravenos.pocket.goblin-web.v2',init,observe,snapshot});
})();