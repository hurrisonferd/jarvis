(() => {
'use strict';
const URL='./ravenos-public-haunt.json';
const menu=[
  {name:'OVERVIEW',copy:'house state, counts and public posture',id:'overview',icon:'◈'},
  {name:'GOD CONTROL',copy:'coarse system denominator telemetry',id:'control',icon:'◎'},
  {name:'GOD MAP',copy:'public topology and coverage snapshot',id:'map',icon:'⌘'},
  {name:'FAIRYOS',copy:'sanitized material-fae projection',id:'fae',icon:'✦'},
  {name:'RAVENOS HOME',copy:'public room atmosphere only',id:'office',icon:'⌂'},
  {name:'PUBLIC BOUNDARY',copy:'privacy, proof and effect ceiling',id:'boundary',icon:'◇'},
  {name:'PUBLIC HAUNT',copy:'open the projection diagnostic surface',id:'public',icon:'↗'}
];
let data=null,view='boot',cursor=0,holdReason='CHECKING',lastLoadAt=null;
const q=id=>document.getElementById(id);
const e=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const gc=()=>data?data.god_control:{};
const fl=()=>data?data.fae:[];
const rl=()=>data?data.rooms:[];
const pct=(n,d)=>Math.max(0,Math.min(100,d?Math.round((Number(n)||0)*100/d):0));
const statusLabel=()=>data?(data.state==='HOLD'?'VALID HOLD':data.state):'PUBLIC HOLD';
const stateClass=()=>data&&data.state==='HOLD'?'warn':'good';
function foot(help){return `<div class="foot"><div class="keys">${help}</div><div class="foot-state">RAVENOS // READ ONLY</div></div>`;}
function key(k,label){return `<span class="key">${e(k)}</span><span>${e(label)}</span>`;}
function frame(name,html,crumb='PUBLIC / RAVENOS',help='A OPEN · B BACK'){
  q('ui').innerHTML=`<div class="head"><div class="head-main"><div class="crumb">${e(crumb)}</div><div class="head-title">${e(name)}</div></div><div class="state-chip ${stateClass()}">${e(statusLabel())}</div></div><div class="body" id="screenBody">${html}</div>${foot(help==='HOME'?`${key('↑↓','MOVE')}${key('A','OPEN')}${key('B','BOOT')}`:`${key('↑↓','SCROLL')}${key('B','BACK')}`)}`;
  bindScroll();
}
function bindScroll(){
  const body=q('screenBody');if(!body){updateScrollRail(null);return;}
  body.addEventListener('scroll',()=>updateScrollRail(body),{passive:true});
  requestAnimationFrame(()=>updateScrollRail(body));
}
function updateScrollRail(body){
  const thumb=q('scrollThumb');if(!thumb)return;
  if(!body||body.scrollHeight<=body.clientHeight+2){thumb.style.opacity='0';return;}
  const ratio=body.clientHeight/body.scrollHeight;
  const rail=Math.max(1,body.clientHeight-2);
  const h=Math.max(18,rail*ratio);
  const maxTop=Math.max(0,rail-h);
  const maxScroll=Math.max(1,body.scrollHeight-body.clientHeight);
  thumb.style.height=h+'px';thumb.style.transform=`translateY(${maxTop*(body.scrollTop/maxScroll)}px)`;thumb.style.opacity='.95';
}
function boot(){
  q('ui').innerHTML=`<div class="boot"><div class="raven-mark"><span>R</span></div><div><div class="logo">RAVENOS</div><div class="sub">POCKET SHELL // PUBLIC OBSERVER</div></div><div class="bootlog"><span class="dim">[BIOS]</span> Raven authority <b>LOCKED</b><br><span class="dim">[LINK]</span> public packet ${data?'<b>VALIDATED</b>':'<b>HELD</b>'}<br><span class="dim">[MODE]</span> effect authority <b>NONE</b><br><span class="dim">[SHELL]</span> touch + d-pad + keyboard <b>READY</b>${holdReason?`<div class="hold-reason">${e(holdReason)}</div>`:''}</div><div class="boot-actions"><span class="key">A</span> ENTER <span class="key">START</span> SYNC</div></div>`;
  updateScrollRail(null);
}
function summaryHero(){
  const g=gc();const effective=g.effective_object_count??'—';
  return `<div class="hero"><div class="eyebrow">Public civilization instrument</div><div class="hero-title">RavenOS is ${data?e(data.state):'HELD'}</div><div class="hero-copy">A compact, fail-closed read surface over the sanitized public RavenOS packet. The shell can show state. It cannot manufacture authority.</div><div class="hero-state">${e(effective)} EFFECTIVE OBJECTS · ${e(g.registered_ghost_ports??'—')} PORTS</div></div>`;
}
function metrics(){
  const g=gc();const eff=Number(g.effective_object_count)||0;const base=Number(g.base_object_count)||0;const ports=Number(g.registered_ghost_ports)||0;
  return `<div class="stats"><div class="stat"><div class="n">${e(g.effective_object_count??'—')}</div><div class="k">EFFECTIVE<br>OBJECTS</div><div class="bar"><i style="width:${pct(eff,Math.max(eff,base,1))}%"></i></div></div><div class="stat"><div class="n">${e(g.registered_ghost_ports??'—')}</div><div class="k">GHOST<br>PORTS</div><div class="bar"><i style="width:${pct(ports,Math.max(ports,31))}%"></i></div></div><div class="stat"><div class="n">${e(g.active_hold_count??'—')}</div><div class="k">ACTIVE<br>HOLDS</div><div class="bar"><i style="width:${pct(g.active_hold_count,g.active_hold_count+g.resolved_hold_count)}%"></i></div></div></div>`;
}
function menuHtml(){return `<div class="section-label">RavenOS surfaces</div><div class="menu" id="menu">${menu.map((m,i)=>`<div class="item ${i===cursor?'sel':''}" data-index="${i}" role="button" tabindex="${i===cursor?'0':'-1'}"><div class="item-icon">${m.icon}</div><div><div class="item-name">${e(m.name)}</div><div class="item-copy">${e(m.copy)}</div></div><div class="item-arrow">›</div></div>`).join('')}</div>`;}
function home(){
  frame('HOME',`${summaryHero()}${metrics()}${menuHtml()}`,'PUBLIC / POCKET','HOME');
  document.querySelectorAll('.item').forEach(el=>{el.addEventListener('click',()=>{cursor=Number(el.dataset.index)||0;enter(menu[cursor].id);});});
  ensureSelection(false);
}
function overview(){
  const g=gc();
  frame('OVERVIEW',`${summaryHero()}${metrics()}<div class="section-label">Current public posture</div><div class="card"><div class="row"><span>HOUSE STATE</span><b class="${data&&data.state==='HOLD'?'warn':'good'}">${e(data?data.state:'HOLD')}</b></div><div class="row"><span>PROVEN NATIVE OWNERS</span><b>${e(g.proven_native_owners??'—')}</b></div><div class="row"><span>STAGED NATIVE CANDIDATES</span><b>${e(g.staged_native_candidates??'—')}</b></div><div class="row"><span>RESOLVED HOLDS</span><b>${e(g.resolved_hold_count??'—')}</b></div></div><div class="notice safe">PUBLIC PACKET ONLY · SAME-ORIGIN VALIDATION · PRIVATE SOURCE FALLBACK DISABLED · EFFECT AUTHORITY = NONE</div>`,'PUBLIC / HOME');
}
function control(){
  const g=gc(),max=Math.max(Number(g.effective_object_count)||1,1);
  frame('GOD CONTROL',`<div class="section-label">Object denominator</div><div class="card"><div class="meter"><span>BASE OBJECTS</span><div class="meter-track"><div class="meter-fill" style="width:${pct(g.base_object_count,max)}%"></div></div><span class="meter-val">${e(g.base_object_count??'—')}</span></div><div class="meter"><span>EFFECTIVE</span><div class="meter-track"><div class="meter-fill" style="width:${pct(g.effective_object_count,max)}%"></div></div><span class="meter-val">${e(g.effective_object_count??'—')}</span></div><div class="meter"><span>GHOST PORTS</span><div class="meter-track"><div class="meter-fill" style="width:${pct(g.registered_ghost_ports,Math.max(Number(g.registered_ghost_ports)||1,31))}%"></div></div><span class="meter-val">${e(g.registered_ghost_ports??'—')}</span></div></div><div class="section-label">Owner posture</div><div class="card"><div class="row"><span>PROVEN NATIVE</span><b class="good">${e(g.proven_native_owners??'—')}</b></div><div class="row"><span>STAGED</span><b class="cyan">${e(g.staged_native_candidates??'—')}</b></div><div class="row"><span>ACTIVE HOLDS</span><b class="warn">${e(g.active_hold_count??'—')}</b></div><div class="row"><span>RESOLVED HOLDS</span><b>${e(g.resolved_hold_count??'—')}</b></div></div><div class="notice">COUNTS ARE TELEMETRY, NOT PRIVATE RECORDS. PUBLIC GOD CONTROL DOES NOT OWN OR EXECUTE THE OBJECTS IT DESCRIBES.</div>`,'PUBLIC / SYSTEMS');
}
function map(){
  const g=gc();
  frame('GOD MAP',`<div class="hero"><div class="eyebrow">Public topology</div><div class="hero-title">${e(g.base_object_count??'—')} → ${e(g.effective_object_count??'—')}</div><div class="hero-copy">Base denominator expands into the current effective public projection. Private paths, causal edges and object identities remain outside this surface.</div></div><div class="grid2"><div class="tile"><b>BASE</b><div class="meta">${e(g.base_object_count??'—')} public base objects</div></div><div class="tile"><b>EFFECTIVE</b><div class="meta">${e(g.effective_object_count??'—')} effective objects</div></div><div class="tile"><b>PORTS</b><div class="meta">${e(g.registered_ghost_ports??'—')} registered ghost ports</div></div><div class="tile"><b>HOLDS</b><div class="meta">${e(g.active_hold_count??'—')} active / ${e(g.resolved_hold_count??'—')} resolved</div></div></div><div class="notice safe">MAP VIEW IS A PUBLIC INSTRUMENT. MAP HIT ≠ OWNER AUTHORITY.</div>`,'PUBLIC / TOPOLOGY');
}
function fae(){
  const list=fl();
  frame('FAIRYOS',`<div class="section-label">Material public fae</div>${list.length?`<div class="grid2">${list.map(x=>`<div class="tile" style="border-color:${e(x.accent)}66"><div class="stamp">${e(x.stamp||x.member)}</div><b>${e(x.member)}</b><div class="meta">${e(x.glyph)} · ${e(x.color_emoji)}</div></div>`).join('')}</div>`:`<div class="empty"><div class="empty-glyph">✦</div>NO MATERIAL FAE ARE PUBLISHED IN THE CURRENT PACKET.<br>SOURCE-BOUND ROSTER PRESENCE DOES NOT IMPLY CURRENT MATERIAL PRESENCE.</div>`}`,'PUBLIC / CREATE');
}
function office(){
  const rooms=rl();
  frame('RAVENOS HOME',`<div class="section-label">Public room atmosphere</div>${rooms.length?`<div class="grid2">${rooms.map(x=>`<div class="tile"><b>${e(x.room)}</b><div class="meta">${e(x.state)} · ${e(x.atmosphere)}<br>ghosts ${e(x.ghost_count)} · holds ${e(x.hold_count)} · absences ${e(x.absence_count)}</div></div>`).join('')}</div>`:`<div class="empty"><div class="empty-glyph">⌂</div>ROOM RUNTIME PROJECTION IS HELD.<br>NO ROOM STATE IS INFERRED FROM SOURCE PRESENCE.</div>`}`,'PUBLIC / HOME');
}
function boundary(){
  const pr=data?data.privacy:{},p=data?data.proof:{};
  const no=v=>v===false?'<b class="good">NO</b>':'<b class="warn">HOLD</b>';
  frame('PUBLIC BOUNDARY',`<div class="section-label">Packet identity</div><div class="card"><div class="packet-id">${e(data?data.packet_id:'NONE')}</div>${holdReason?`<div class="hold-reason">${e(holdReason)}</div>`:''}</div><div class="section-label">Privacy whitelist</div><div class="card"><div class="row"><span>SOURCE PATHS</span>${no(pr.source_paths_included)}</div><div class="row"><span>TRANSACTION IDS</span>${no(pr.transaction_ids_included)}</div><div class="row"><span>EVENT / HAUNT / FLIGHT IDS</span>${no(!(pr.source_event_ids_included===false&&pr.haunt_ids_included===false&&pr.flight_ids_included===false)?true:false)}</div><div class="row"><span>SECRETS / TOKENS</span>${no(pr.secrets_or_tokens_included)}</div></div><div class="section-label">Proof ceiling</div><div class="card"><div class="row"><span>HOST RENDER PROVEN</span><b class="${p.public_host_render_proven?'good':'warn'}">${p.public_host_render_proven?'YES':'NO'}</b></div><div class="row"><span>AUTO HOST INVOCATION</span><b class="${p.automatic_host_invocation_proven?'good':'warn'}">${p.automatic_host_invocation_proven?'YES':'NO'}</b></div><div class="row"><span>EFFECT AUTHORITY</span><b class="${p.effect_authority?'bad':'good'}">${p.effect_authority?'YES':'NONE'}</b></div></div><div class="notice">UNKNOWN NESTED FIELDS OR PACKET-ID MISMATCH FAIL CLOSED. VALIDATOR: ravenos.public-handheld.contract-validator.v1</div>`,'PUBLIC / SECURITY');
}
function render(){
  if(view==='boot')return boot();
  if(view==='home')return home();
  ({overview,control,map,fae,office,boundary}[view]||home)();
}
function enter(id){if(id==='public'){location.href='./ravenos-haunt.html';return;}view=id;render();}
function ensureSelection(smooth=true){
  const selected=document.querySelector('.item.sel');const body=q('screenBody');
  if(!selected||!body)return;
  const top=selected.offsetTop-8,bottom=top+selected.offsetHeight;
  if(top<body.scrollTop)body.scrollTo({top,behavior:smooth?'smooth':'auto'});
  else if(bottom>body.scrollTop+body.clientHeight)body.scrollTo({top:bottom-body.clientHeight+8,behavior:smooth?'smooth':'auto'});
  requestAnimationFrame(()=>updateScrollRail(body));
}
function scrollDetail(direction){const body=q('screenBody');if(!body)return;const amount=Math.max(64,Math.round(body.clientHeight*.28));body.scrollBy({top:direction*amount,behavior:'smooth'});}
window.nav=direction=>{
  if(view==='boot')return;
  if(view==='home'){
    cursor=(cursor+direction+menu.length)%menu.length;render();requestAnimationFrame(()=>ensureSelection(true));
  }else scrollDetail(direction);
};
window.ok=()=>{if(view==='boot'){view='home';render();return;}if(view==='home')enter(menu[cursor].id);};
window.back=()=>{if(view==='boot')return;if(view!=='home'){view='home';render();requestAnimationFrame(()=>ensureSelection(false));}else{view='boot';render();}};
window.reloadPacket=async()=>{await load();view='home';cursor=0;render();};
async function load(){
  q('packet').textContent='SYNC';
  try{
    if(!window.RavenOSPublicContract)throw new Error('VALIDATOR_UNAVAILABLE');
    const r=await fetch(URL,{cache:'no-store'});if(!r.ok)throw new Error('NO_PACKET_'+r.status);
    const p=await r.json();const result=await window.RavenOSPublicContract.validatePacket(p);
    if(!result.ok)throw new Error('REJECTED_'+result.reason);
    data=p;holdReason='';lastLoadAt=Date.now();
    q('packet').textContent=p.state==='HOLD'?'VALID HOLD':'CURRENT';
    q('packet').style.color=p.state==='HOLD'?'var(--amber)':'var(--green)';
    q('led').style.background=p.state==='HOLD'?'var(--amber)':'var(--green)';
    q('led').style.boxShadow=`0 0 12px ${p.state==='HOLD'?'var(--amber)':'var(--green)'}`;
  }catch(err){
    data=null;holdReason=String(err&&err.message||'UNKNOWN');lastLoadAt=Date.now();
    q('packet').textContent='HOLD';q('packet').style.color='var(--amber)';
    q('led').style.background='var(--amber)';q('led').style.boxShadow='0 0 12px var(--amber)';
  }
}
document.addEventListener('keydown',ev=>{
  const k=ev.key;
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter','Escape','Backspace','z','Z','x','X','r','R'].includes(k))ev.preventDefault();
  if(k==='ArrowUp')nav(-1);else if(k==='ArrowDown')nav(1);else if(k==='ArrowLeft'||k==='Escape'||k==='Backspace'||k==='x'||k==='X')back();else if(k==='ArrowRight'||k==='Enter'||k==='z'||k==='Z')ok();else if(k==='r'||k==='R')reloadPacket();
},{passive:false});
window.addEventListener('resize',()=>{const body=q('screenBody');if(body)requestAnimationFrame(()=>updateScrollRail(body));},{passive:true});
load().finally(render);
})();
