(() => {
'use strict';
const TOP=['schema','effect_authority','effect_budget','browser_scene_scope','cartridges','providers','laws'];
const CART=['id','label','icon','class','order','status','owner_label','copy','packet_sections','views','actions','proof'];
const PROVIDERS=['browser','android','windows'];
const PROVIDER=['connected','label','capabilities'];
const CLASSES=new Set(['PLATFORM','CIVILIZATION','VEHICLE','CAPABILITY','COGNITION','PERCEPTION','CREATIVE','GAME','PROOF','RECOVERY','BOUNDARY']);
const ACTIONS=new Set(['READ','INSPECT','SIMULATE']);
function exact(obj,keys){if(!obj||typeof obj!=='object'||Array.isArray(obj))return false;const got=Object.keys(obj).sort();const want=[...keys].sort();return got.length===want.length&&got.every((x,i)=>x===want[i]);}
function strings(v){return Array.isArray(v)&&v.every(x=>typeof x==='string'&&x.length>0);}
function validateRegistry(r){
  if(!exact(r,TOP))return {ok:false,reason:'TOP_LEVEL_KEYS'};
  if(r.schema!=='ravenos.pocket.cartridge-registry.public.v1')return {ok:false,reason:'SCHEMA'};
  if(r.effect_authority!==false||r.effect_budget!==0)return {ok:false,reason:'EFFECT_BOUNDARY'};
  if(r.browser_scene_scope!=='POCKET_PAGE_ONLY')return {ok:false,reason:'SCENE_SCOPE'};
  if(!Array.isArray(r.cartridges)||r.cartridges.length<1||r.cartridges.length>64)return {ok:false,reason:'CARTRIDGE_COUNT'};
  const ids=new Set();let last=-Infinity;
  for(const c of r.cartridges){
    if(!exact(c,CART))return {ok:false,reason:'CARTRIDGE_KEYS'};
    if(typeof c.id!=='string'||!/^[a-z0-9_]+$/.test(c.id)||ids.has(c.id))return {ok:false,reason:'CARTRIDGE_ID'};ids.add(c.id);
    if(typeof c.label!=='string'||typeof c.icon!=='string'||typeof c.owner_label!=='string'||typeof c.copy!=='string'||typeof c.status!=='string'||typeof c.proof!=='string')return {ok:false,reason:'CARTRIDGE_TEXT'};
    if(!CLASSES.has(c.class))return {ok:false,reason:'CARTRIDGE_CLASS'};
    if(!Number.isInteger(c.order)||c.order<0||c.order<=last)return {ok:false,reason:'CARTRIDGE_ORDER'};last=c.order;
    if(!strings(c.packet_sections)||!strings(c.views)||!strings(c.actions)||!c.actions.every(a=>ACTIONS.has(a)))return {ok:false,reason:'CARTRIDGE_ARRAY'};
    if(c.actions.includes('REQUEST_EFFECT'))return {ok:false,reason:'PUBLIC_EFFECT_ACTION'};
  }
  if(!exact(r.providers,PROVIDERS))return {ok:false,reason:'PROVIDER_KEYS'};
  for(const name of PROVIDERS){const p=r.providers[name];if(!exact(p,PROVIDER)||typeof p.connected!=='boolean'||typeof p.label!=='string'||!strings(p.capabilities))return {ok:false,reason:'PROVIDER_'+name.toUpperCase()};}
  if(r.providers.browser.connected!==true||r.providers.android.connected!==false||r.providers.windows.connected!==false)return {ok:false,reason:'PROVIDER_CONNECTION_CLAIM'};
  if(!strings(r.laws))return {ok:false,reason:'LAWS'};
  return {ok:true,reason:'PASS',count:r.cartridges.length};
}
window.RavenOSPocketContract=Object.freeze({schema:'ravenos.pocket.cartridge-contract.v1',validateRegistry});
})();
