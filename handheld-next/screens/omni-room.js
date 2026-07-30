const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
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
      const attention=(room.interventions||[]).length;
      const layer=router.context.layer||'system';
      const body=layer==='crew'
        ? `<div class="panel"><div class="${p.system_id==='LILITH'?'identity':''}">${esc(p.system_id||'NO SYSTEM')} · ${esc(presence?.station||'UNASSIGNED')}</div><div class="${presence?.state==='PRESENT'?'ok':'warn'}">${esc(presence?.state||'UNOBSERVED')}</div><div>${esc(presence?.focus||'NO ACTIVE FOCUS')}</div><div>${esc(presence?.opinion||'NO PUBLIC OPINION')}</div><div class="sub">CURSOR ${esc(cursor?.last_observed_receipt||'NONE')}</div><div class="sub">DRAFTS ${drafts.length}</div></div>`
        : `<div class="panel"><div class="${p.system_id==='LILITH'?'identity':''}">${esc(p.system_id||'NO SYSTEM')}</div><div>${esc(p.role||'')}</div><div class="${p.state==='PRESENT'?'ok':p.state==='UNOBSERVED'?'warn':'bad'}">${esc(p.state||'UNKNOWN')}</div><div>UNREAD ${Number(p.unread_work||0)}</div><div>${esc(p.last_delta||'NO DELTA')}</div>${p.identity_note?`<div class="identity">${esc(p.identity_note)}</div>`:''}</div>`;
      return `<div class="header"><span>OMNI ROOM · ${layer.toUpperCase()}</span><span class="${attention?'warn':'ok'}">${attention?attention+' ALERTS':'FIELD STABLE'}</span></div>${body}<div class="sub">${i+1}/${panels.length} · CREW ${crew.state.crew.length} · RECEIPT ${esc((room.receipt_hash||'').slice(0,12))}</div><div class="footer">↑↓:SYSTEM · ←→:LAYER · A:INSPECT · SELECT:REFRESH · B:BACK</div>`;
    },
    command(cmd,router){
      const panels=store.room?.panels||[];
      if(cmd==='up'&&panels.length)router.context.cursor=(router.context.cursor+panels.length-1)%panels.length;
      if(cmd==='down'&&panels.length)router.context.cursor=(router.context.cursor+1)%panels.length;
      if(cmd==='left'||cmd==='right')router.context.layer=router.context.layer==='crew'?'system':'crew';
      if(cmd==='select')Promise.allSettled([store.load(),crew.load()]).then(()=>router.render());
      if(cmd==='confirm'){
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
