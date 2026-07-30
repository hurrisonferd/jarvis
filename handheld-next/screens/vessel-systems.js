const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const back=(cmd,router)=>{if(cmd==='back'||cmd==='start')router.go('menu');};
const listScreen=({title,subtitle,items,empty='NO SIGNAL'})=>({
  render(router){const rows=items(router)||[];return `<div class="header"><span>${title}</span><span>${subtitle}</span></div>${rows.length?rows.map((row,index)=>`<div class="row ${index===router.context.cursor?'selected':''}">${index===router.context.cursor?'▶':' '} ${esc(row.label)} <span class="sub">${esc(row.value)}</span></div>`).join(''):`<div class="panel warn">${empty}</div>`}<div class="footer">↑↓:SCAN · B:BACK · START:BRIDGE</div>`;},
  command(cmd,router){const rows=items(router)||[];if(cmd==='up'&&rows.length)router.context.cursor=(router.context.cursor+rows.length-1)%rows.length;if(cmd==='down'&&rows.length)router.context.cursor=(router.context.cursor+1)%rows.length;back(cmd,router);}
});
export const bridgeScreen=listScreen({title:'BRIDGE COMMS',subtitle:'READ-ONLY',items:router=>[
  {label:'CAPTAIN',value:'RAVEN'},
  {label:'SHIP INTELLIGENCE',value:'JARVIS'},
  {label:'ARCHITECT',value:'ATOM'},
  {label:'FIELD MODE',value:router.store?.source?.toUpperCase?.()||'FIXTURE'},
  {label:'UPLINK',value:navigator.onLine?'AVAILABLE':'OFFLINE'}
]});
export const intelligenceScreen={render(router){const c=router.store?.room?.compression||{};return `<div class="header"><span>SHIP INTELLIGENCE</span><span>JARVIS</span></div><div class="panel"><div class="blue">WHY IT MATTERS</div>${esc(c.why_it_matters||'NO SYNTHESIS')}</div><div class="panel"><div class="blue">OWNERS</div>${esc((c.owners||[]).join(' · ')||'UNASSIGNED')}</div><div class="panel"><div class="blue">UNCERTAINTY</div>${esc((c.uncertainty||[]).join(' · ')||'NONE DECLARED')}</div><div class="footer">B:BACK · START:BRIDGE</div>`;},command:back};
export const mnemosScreen=listScreen({title:'MNEMOS VAULT',subtitle:'MEMORY',items:router=>{
  const room=router.store?.room||{};return [
    {label:'SNAPSHOT',value:room.generated_at||'UNKNOWN'},
    {label:'RECEIPT',value:(room.receipt_hash||'NONE').slice(0,14)},
    {label:'SYSTEMS',value:String((room.panels||[]).length)},
    {label:'INTERVENTIONS',value:String((room.interventions||[]).length)},
    {label:'IDENTITY FLATTENING',value:room.compression?.flattening_prevented?'BLOCKED':'UNKNOWN'}
  ];
}});
export const telemetryScreen=listScreen({title:'SENSOR ARRAY',subtitle:'TELEMETRY',items:router=>(router.store?.room?.panels||[]).map(panel=>({label:panel.system_id,value:`${panel.state} / ${panel.unread_work||0}`}))});
export const godFieldScreen={render(router){const panels=router.store?.room?.panels||[];return `<div class="header"><span>ENGINE ROOM</span><span>GOD FIELD</span></div>${panels.slice(0,8).map((panel,index)=>{const load=Math.min(100,20+(panel.unread_work||0)*15+(panel.state==='PRESENT'?35:5));return `<div class="metric"><span>${esc(panel.system_id)}</span><span>${load}%</span></div><div class="bar"><i style="width:${load}%"></i></div>`;}).join('')}<div class="footer">FIELD IS SYMBOLIC · B:BACK</div>`;},command:back};
export const fleetScreen=listScreen({title:'HANGAR',subtitle:'FLEET',items:()=>[
  {label:'WORLD-001',value:'PRODUCTION / PRESERVED'},
  {label:'WORLD-002',value:'VESSEL TWO / ONLINE'},
  {label:'OMNI COMMAND ROOM',value:'OBSERVER LINK'},
  {label:'PRIVATE DECK',value:'LOCKED'},
  {label:'HOLODECK',value:'PARITY PENDING'}
]});
export const shipMapScreen={render(router){const decks=[['BRIDGE','bridge'],['OMNI DECK','omni'],['MNEMOS VAULT','mnemos'],['ENGINE ROOM','godfield'],['SENSOR ARRAY','telemetry'],['HANGAR','fleet'],['SHIP CORE','intelligence'],['HOLODECK','legacy']];return `<div class="header"><span>SHIP MAP</span><span>WORLD-002</span></div><div class="ship-map">${decks.map((deck,index)=>`<div class="deck ${index===router.context.cursor?'active':''}">${deck[0]}</div>`).join('')}</div><div class="footer">←→↑↓:MOVE · A:ENTER · B:BACK</div>`;},command(cmd,router){const routes=['bridge','omni','mnemos','godfield','telemetry','fleet','intelligence','legacy'];if(cmd==='left')router.context.cursor=(router.context.cursor+7)%8;if(cmd==='right')router.context.cursor=(router.context.cursor+1)%8;if(cmd==='up')router.context.cursor=(router.context.cursor+6)%8;if(cmd==='down')router.context.cursor=(router.context.cursor+2)%8;if(cmd==='confirm')router.go(routes[router.context.cursor]);back(cmd,router);}};