const ROOM_REQUIRED=['schema_version','generated_at','receipt_hash','compression','interventions','panels'];
const INSTRUMENT_REQUIRED=['schema_version','generated_at','receipt_hash','vehicle','performance','capacity','proof','safety','access_domains','public_safe'];
const FORBIDDEN=/service_role|SUPABASE_SERVICE_ROLE_KEY|approval_digest|rpc_function|channel_body|message_body|private_relationship|authorization|secret|password|token/i;
const SIX_HOURS=6*60*60*1000;
const DAY=24*60*60*1000;

export function classifyFreshness(generatedAt,now=Date.now()){
  const ts=Date.parse(generatedAt||'');
  if(!Number.isFinite(ts))return{state:'UNKNOWN',age_ms:null,age_hours:null};
  const age=now-ts;
  if(age < -5*60*1000)return{state:'FUTURE',age_ms:age,age_hours:Number((age/3600000).toFixed(2))};
  if(age<=SIX_HOURS)return{state:'FRESH',age_ms:Math.max(0,age),age_hours:Number((Math.max(0,age)/3600000).toFixed(2))};
  if(age<=DAY)return{state:'AGING',age_ms:age,age_hours:Number((age/3600000).toFixed(2))};
  return{state:'STALE',age_ms:age,age_hours:Number((age/3600000).toFixed(2))};
}

export class ObserverStore{
  constructor({bus,led,net}){
    this.bus=bus;this.led=led;this.net=net;
    this.room=null;this.source='none';
    this.instrument=null;this.instrumentSource='none';
    this.instrumentFreshness={state:'UNKNOWN',age_ms:null,age_hours:null};
  }
  validate(data){
    for(const key of ROOM_REQUIRED)if(!(key in data))throw new Error(`MISSING_${key.toUpperCase()}`);
    const text=JSON.stringify(data);if(FORBIDDEN.test(text))throw new Error('PRIVILEGED_MATERIAL_REJECTED');
    return data;
  }
  validateInstrument(data){
    for(const key of INSTRUMENT_REQUIRED)if(!(key in data))throw new Error(`MISSING_INSTRUMENT_${key.toUpperCase()}`);
    if(data.schema_version!=='omni.instrument.v2')throw new Error('UNSUPPORTED_INSTRUMENT_SCHEMA');
    if(data.public_safe!==true)throw new Error('INSTRUMENT_NOT_PUBLIC_SAFE');
    if(data.safety?.public_mutation!=='BLOCKED'||data.safety?.effect_authority!=='NONE')throw new Error('INSTRUMENT_AUTHORITY_BOUNDARY_FAILED');
    if(!Array.isArray(data.access_domains)||data.access_domains.length!==16)throw new Error('INSTRUMENT_DOMAIN_COUNT_INVALID');
    const text=JSON.stringify(data);if(FORBIDDEN.test(text))throw new Error('PRIVILEGED_INSTRUMENT_MATERIAL_REJECTED');
    return data;
  }
  async loadRoom(){
    const candidates=['./data/observer-live.json','./data/observer-snapshot.json'];let lastError;
    for(const url of candidates){
      try{
        const response=await fetch(url,{cache:'no-store'});if(!response.ok)throw new Error(`HTTP_${response.status}`);
        this.room=this.validate(await response.json());this.source=url.includes('live')?'live':'fixture';
        this.bus.emit('omni_snapshot_loaded',{receipt_hash:this.room.receipt_hash,interventions:this.room.interventions.length,source:this.source});
        return this.room;
      }catch(error){lastError=error;}
    }
    this.bus.emit('omni_snapshot_failed',{error:String(lastError)});throw lastError;
  }
  async loadInstrument(){
    try{
      const response=await fetch('./data/instrument-live.json',{cache:'no-store'});
      if(!response.ok)throw new Error(`HTTP_${response.status}`);
      this.instrument=this.validateInstrument(await response.json());
      this.instrumentSource='live';
      this.instrumentFreshness=classifyFreshness(this.instrument.generated_at);
      this.bus.emit('omni_instrument_loaded',{
        receipt_hash:this.instrument.receipt_hash,
        freshness:this.instrumentFreshness.state,
        age_hours:this.instrumentFreshness.age_hours
      });
      return this.instrument;
    }catch(error){
      this.instrument=null;this.instrumentSource='none';
      this.instrumentFreshness={state:'UNKNOWN',age_ms:null,age_hours:null};
      this.bus.emit('omni_instrument_failed',{error:String(error)});
      return null;
    }
  }
  async load(){
    await this.loadRoom();
    await this.loadInstrument();
    this.setState(true);
    return this.room;
  }
  setState(online){
    const attention=(this.room?.interventions||[]).length>0||['STALE','FUTURE','UNKNOWN'].includes(this.instrumentFreshness.state);
    this.led.classList.toggle('attention',attention);
    this.led.classList.toggle('offline',!online);
    const inst=this.instrument?` · INST ${this.instrumentFreshness.state}`:' · INST NONE';
    this.net.textContent=online?`${this.source.toUpperCase()}${inst}`:'OFFLINE';
  }
}
