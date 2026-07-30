const REQUIRED=['schema_version','generated_at','receipt_hash','compression','interventions','panels'];
const FORBIDDEN=/service_role|SUPABASE_SERVICE_ROLE_KEY|approval_digest|rpc_function|channel_body|private_relationship/i;
export class ObserverStore{
  constructor({bus,led,net}){this.bus=bus;this.led=led;this.net=net;this.room=null;this.source='none';}
  validate(data){for(const key of REQUIRED)if(!(key in data))throw new Error(`MISSING_${key.toUpperCase()}`);const text=JSON.stringify(data);if(FORBIDDEN.test(text))throw new Error('PRIVILEGED_MATERIAL_REJECTED');return data;}
  async load(){const candidates=['./data/observer-live.json','./data/observer-snapshot.json'];let lastError;
    for(const url of candidates){try{const response=await fetch(url,{cache:'no-store'});if(!response.ok)throw new Error(`HTTP_${response.status}`);this.room=this.validate(await response.json());this.source=url.includes('live')?'live':'fixture';this.bus.emit('omni_snapshot_loaded',{receipt_hash:this.room.receipt_hash,interventions:this.room.interventions.length,source:this.source});this.setState(true);return this.room;}catch(error){lastError=error;}}
    this.setState(false);this.bus.emit('omni_snapshot_failed',{error:String(lastError)});throw lastError;
  }
  setState(online){const attention=(this.room?.interventions||[]).length>0;this.led.classList.toggle('attention',attention);this.led.classList.toggle('offline',!online);this.net.textContent=online?this.source.toUpperCase():'OFFLINE';}
}