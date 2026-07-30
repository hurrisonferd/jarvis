export class EventBus {
  constructor({gate=()=>null,sink=()=>{}}={}){this.handlers=new Map();this.gate=gate;this.sink=sink;}
  on(event,handler){const list=this.handlers.get(event)||[];list.push(handler);this.handlers.set(event,list);return()=>this.handlers.set(event,(this.handlers.get(event)||[]).filter(h=>h!==handler));}
  emit(event,data={}){const envelope={event,data:{...data,_ts:Date.now()},id:crypto.randomUUID()};const blocked=this.gate(envelope);if(blocked)return{ok:false,blocked};for(const h of this.handlers.get(event)||[])h(envelope);for(const h of this.handlers.get('*')||[])h(envelope);this.sink(envelope);return{ok:true,envelope};}
}

export const aegisGate=({event,data})=>{
  if(event==='omni_private_snapshot_loaded'&&!data.authenticated)return'PRIVATE_STATE_REQUIRES_AUTH';
  if(event==='omni_mutation_requested')return'PUBLIC_HANDHELD_IS_READ_ONLY';
  return null;
};
