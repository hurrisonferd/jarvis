import fs from 'node:fs';
import assert from 'node:assert/strict';
import {classifyFreshness} from '../core/observer-store.js';
import {createOmniScreen} from '../screens/omni-room.js';

const instrument=JSON.parse(fs.readFileSync(new URL('../data/instrument-live.json',import.meta.url),'utf8'));
assert.equal(instrument.schema_version,'omni.instrument.v2');
assert.equal(instrument.public_safe,true);
assert.equal(instrument.safety.public_mutation,'BLOCKED');
assert.equal(instrument.safety.effect_authority,'NONE');
assert.equal(instrument.access_domains.length,16);
assert.equal(instrument.performance.access_domains_resolved,16);
assert.equal(instrument.performance.active_armor_gaps,0);
assert.equal(instrument.capacity.formal_core_os_owners,76);
assert.equal(instrument.capacity.tracked_weapons,108);
assert.equal(instrument.capacity.explicit_omni_sockets,10);
assert.equal(instrument.capacity.active_armor_stations,29);
assert.equal(instrument.capacity.armor_socket_denominator,17);
assert.equal(instrument.capacity.effective_live_god_objects,31);

const t=Date.parse(instrument.generated_at);
assert.equal(classifyFreshness(instrument.generated_at,t+60*60*1000).state,'FRESH');
assert.equal(classifyFreshness(instrument.generated_at,t+12*60*60*1000).state,'AGING');
assert.equal(classifyFreshness(instrument.generated_at,t+30*60*60*1000).state,'STALE');
assert.equal(classifyFreshness(instrument.generated_at,t-60*60*1000).state,'FUTURE');

const store={
  room:{receipt_hash:'observer-canary',interventions:[],panels:[{system_id:'ATOM',role:'canary',state:'PRESENT',unread_work:0,last_delta:'OK'}]},
  instrument,
  instrumentFreshness:{state:'FRESH',age_hours:1},
  load:async()=>null
};
const crew={state:{crew:[],drafts:[],read_cursors:[]},load:async()=>null,propose:x=>({...x,status:'DRAFT'})};
const bus={emit:()=>({ok:true})};
const screen=createOmniScreen({store,crew,bus});
const html=screen.render({context:{cursor:0,layer:'vehicle'}});
assert.match(html,/Omni RV/);
assert.match(html,/ACCESS 16\/16/);
assert.match(html,/PUBLIC MUTATION BLOCKED/);
assert.match(html,/INSTRUMENT FRESH/);

const encoded=JSON.stringify(instrument).toLowerCase();
for(const bad of ['service_role','supabase_service_role_key','approval_digest','message_body','private_relationship']){
  assert.equal(encoded.includes(bad),false,bad);
}

console.log('PUBLIC_OMNI_INSTRUMENT_CANARY_PASS');
