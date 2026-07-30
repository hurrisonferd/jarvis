const REQUIRED=['schema_version','generated_at','crew','drafts','read_cursors'];
const SAFE_CREW_FIELDS=['system_id','state','station','last_seen','focus','opinion'];
const SAFE_DRAFT_FIELDS=['draft_id','author','title','summary','risk','status','requires_raven'];
const SAFE_CURSOR_FIELDS=['system_id','stream','last_observed_receipt'];
const pick=(row,keys)=>Object.fromEntries(keys.filter(k=>k in (row||{})).map(k=>[k,row[k]]));
export class CrewBridge{
  constructor({bus}){this.bus=bus;this.state={schema_version:'omni.crew.v1',generated_at:null,crew:[],drafts:[],read_cursors:[],source:'none'};}
  validate(payload){for(const key of REQUIRED)if(!(key in payload))throw new Error(`CREW_MISSING_${key.toUpperCase()}`);return {schema_version:'omni.crew.v1',generated_at:String(payload.generated_at),crew:(payload.crew||[]).map(x=>pick(x,SAFE_CREW_FIELDS)),drafts:(payload.drafts||[]).map(x=>pick(x,SAFE_DRAFT_FIELDS)),read_cursors:(payload.read_cursors||[]).map(x=>pick(x,SAFE_CURSOR_FIELDS))};}
  async load(){let lastError;for(const url of ['./data/crew-live.json','./data/crew-snapshot.json']){try{const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP_${r.status}`);this.state={...this.validate(await r.json()),source:url.includes('live')?'live':'fixture'};this.bus.emit('omni_crew_loaded',{source:this.state.source,crew:this.state.crew.length,drafts:this.state.drafts.length});return this.state;}catch(error){lastError=error;}}this.bus.emit('omni_crew_failed',{error:String(lastError)});return this.state;}
  propose(draft){const safe=pick(draft,SAFE_DRAFT_FIELDS);safe.status='LOCAL_DRAFT_ONLY';safe.requires_raven=true;this.bus.emit('omni_draft_created',safe);return safe;}
  requestAck(){const blocked='PRIVATE_ACK_TRANSPORT_NOT_CONFIGURED';this.bus.emit('omni_ack_blocked',{reason:blocked});return {ok:false,blocked};}
}
