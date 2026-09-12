const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const LAYERS=['system','crew','vehicle'];

function vehicleBody(store){
  const inst=store.instrument;
  const fresh=store.instrumentFreshness||{state:'UNKNOWN',age_hours:null};
  if(!inst)return '<div class="panel"><div class="warn">NO VEHICLE INSTRUMENT FEED</div><div class="sub">Public command authority remains blocked.</div></div>';
  const v=inst.vehicle||{},p=inst.performance||{},c=inst.capacity||{},proof=inst.proof||{},safe=inst.safety||{},loop=inst.god_loop||{},gf=inst.godframe||{};
  const age=fresh.age_hours===null?'?':fresh.age_hours;
  const checks=p.onboard_checks_run??p.onboard_check_contract??0;
  const organs=loop.organ_count??p.god_loop_organs??0;
  const stages=loop.loop_stage_count??p.god_loop_stages??0;
  return `<div class="panel">
    <div class="identity">${esc(v.name||'OMNI RV')} · ${esc(v.god_vehicle_version||'UNKNOWN')}</div>
    <div class="${fresh.state==='FRESH'?'ok':fresh.state==='AGING'?'warn':'bad'}">INSTRUMENT ${esc(fresh.state)} · AGE ${esc(age)}h</div>
    <div>HEALTH ${esc(v.health||'UNKNOWN')} · HANDLING ${esc(v.handling||'UNKNOWN')}</div>
    <div>ENGINE ${esc(v.engine_version||'?')} · BUS ${esc(v.universal_bus_version||'?')}</div>
    <div>ACCESS ${Number(p.access_domains_resolved||0)}/${Number(p.access_domains_expected||0)} · CHECK CONTRACT ${Number(checks||0)}</div>
    <div>GOD LOOP ${Number(organs)}/8 · STAGES ${Number(stages)}/10 · SIGHT ${Number(p.sight_layers||0)}/7</div>
    <div>GODFRAME ${Number(gf.active_nodes??c.active_armor_stations??0)}×${Number(gf.socket_count??c.armor_socket_denominator??0)} · BESPOKE ${Number(gf.bespoke_employee_suits||0)} · FALLBACK ${Number(gf.forged_fallback_employee_suits||0)}</div>
    <div>ARMOR GAPS ${Number(gf.active_armor_gaps??p.active_armor_gaps??0)} · CUBICLES ${Number(c.physical_cubicle_partitions||0)} · GOD OBJECTS ${Number(c.effective_live_god_objects||0)}</div>
    <div>OS ${Number(c.formal_core_os_owners||0)} · WEAPONS ${Number(c.tracked_weapons||0)} · OMNI ${Number(c.explicit_omni_sockets||0)}</div>
    <div class="sub">TYPED BUS ${loop.typed_observation_bus===true?'BOUND':'UNKNOWN'} · WORLD LEDGER ${esc(loop.persistent_world_ledger||'UNKNOWN')} · FORECAST FACT ${loop.forecast_is_fact===true?'YES':loop.forecast_is_fact===false?'NO':'UNKNOWN'}</div>
    <div class="sub">PROOF ${esc(proof.onboard_selftest||'UNKNOWN')} · CHECKOUT ${esc(proof.checked_out_execution||'UNKNOWN')}</div>
    <div class="sub">PUBLIC MUTATION ${esc(safe.public_mutation||'UNKNOWN')} · EFFECT ${esc(safe.effect_authority||'UNKNOWN')}</div>
    <div class="sub">INSTRUMENT RECEIPT ${esc((inst.receipt_hash||'').slice(0,12))}</div>
  </div>`;
}

export function createOmniScreen({store,crew,bus}){
  return {
    render(router){
      const room=store.room;
      if(!room)return '<div class="warn">NO OBSERVER SNAPSHOT</div><div class="footer">SELECT:REFRESH · B:BACK</div>';
      const panels=room.panels||[];
      const i=Math.min(router.context.cursor,Math.max(0,panels.length-1));
      const p=panels[i]||{};
      const presence=(crew.state.crew||[]).find(x=>x.system_id===p.system_id);
      const drafts=(crew.state.drafts||[]).filter(x=>x.author===p.system_id);
      const cursor=(crew.state.read_cursors||[]).find(x=>x.system_id===p.system_id);
      const layer=LAYERS.includes(router.context.layer)?router.context.layer:'system';
      const stale=['STALE','FUTURE','UNKNOWN'].includes(store.instrumentFreshness?.state);
      const attention=(room.interventions||[]).length+(stale?1:0);
      let body;
      if(layer==='vehicle'){
        body=vehicleBody(store);
      }else if(layer==='crew'){
        body=`<div class="panel"><div class="${p.system_id==='LILITH'?'identity':''}">${esc(p.system_id||'NO SYSTEM')} · ${esc(presence?.station||'UNASSIGNED')}</div><div class="${presence?.state==='PRESENT'?'ok':'warn'}">${esc(presence?.state||'UNOBSERVED')}</div><div>${esc(presence?.focus||'NO ACTIVE FOCUS')}</div><div>${esc(presence?.opinion||'NO PUBLIC OPINION')}</div><div class="sub">CURSOR ${esc(cursor?.last_observed_receipt||'NONE')}</div><div class="sub">DRAFTS ${drafts.length}</div></div>`;
      }else{
        body=`<div class="panel"><div class="${p.system_id==='LILITH'?'identity':''}">${esc(p.system_id||'NO SYSTEM')}</div><div>${esc(p.role||'')}</div><div class="${p.state==='PRESENT'?'ok':p.state==='UNOBSERVED'?'warn':'bad'}">${esc(p.state||'UNKNOWN')}</div><div>UNREAD ${Number(p.unread_work||0)}</div><div>${esc(p.last_delta||'NO DELTA')}</div>${p.identity_note?`<div class="identity">${esc(p.identity_note)}</div>`:''}</div>`;
      }
      const idx=layer==='vehicle'?'VEHICLE':`${i+1}/${panels.length}`;
      return `<div class="header"><span>OMNI ROOM · ${layer.toUpperCase()}</span><span class="${attention?'warn':'ok'}">${attention?attention+' ATTENTION':'FIELD STABLE'}</span></div>${body}<div class="sub">${idx} · CREW ${crew.state.crew.length} · OBS ${esc((room.receipt_hash||'').slice(0,12))}</div><div class="footer">↑↓:SYSTEM · ←→:SYSTEM/CREW/VEHICLE · A:INSPECT · SELECT:REFRESH · B:BACK</div>`;
    },
    command(cmd,router){
      const panels=store.room?.panels||[];
      if(cmd==='up'&&panels.length)router.context.cursor=(router.context.cursor+panels.length-1)%panels.length;
      if(cmd==='down'&&panels.length)router.context.cursor=(router.context.cursor+1)%panels.length;
      if(cmd==='left'||cmd==='right'){
        const current=LAYERS.includes(router.context.layer)?LAYERS.indexOf(router.context.layer):0;
        const delta=cmd==='right'?1:-1;
        router.context.layer=LAYERS[(current+delta+LAYERS.length)%LAYERS.length];
      }
      if(cmd==='select')Promise.allSettled([store.load(),crew.load()]).then(()=>router.render());
      if(cmd==='confirm'){
        if(router.context.layer==='vehicle'){
          bus.emit('omni_vehicle_instrument_inspected',{
            receipt_hash:store.instrument?.receipt_hash||null,
            freshness:store.instrumentFreshness?.state||'UNKNOWN'
          });
          router.context.notice=`VEHICLE ${store.instrumentFreshness?.state||'UNKNOWN'}`;
          return;
        }
        const p=panels[router.context.cursor];
        if(router.context.layer==='crew'){
          const draft=crew.propose({draft_id:`local-${Date.now()}`,author:p?.system_id,title:'Inspect recovery path',summary:`Review public-safe recovery evidence for ${p?.system_id}.`,risk:'LOW'});
          router.context.notice=`DRAFT ${draft.status}`;
        }else{
          bus.emit('omni_recovery_inspected',{system_id:p?.system_id,evidence:p?.recent_receipts||[]});
          router.context.recovery=p?.recovery||null;
        }
      }
      if(cmd==='back'||cmd==='start')router.go('menu');
    }
  };
}
