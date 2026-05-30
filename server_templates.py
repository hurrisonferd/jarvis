"""Static HTML/JS templates served by jarvis_mcp_server.

Pure data extracted from the server logic file (GL7: data out of logic).
Byte-identical to the originals; served verbatim by the route handlers.
"""


_GALLERY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>JARVIS GRID — Digital Highway</title>
<style>
:root{--cyan:#00e5ff;--dim:#004a60;--glow:#00e5ff55;--bg:#000008;}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{width:100%;height:100%;overflow:hidden;background:var(--bg);font-family:'Courier New',monospace;color:var(--cyan);}

/* scanline overlay */
body::after{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.07) 2px,rgba(0,0,0,.07) 4px);pointer-events:none;z-index:200;}

/* perspective floor */
.floor{position:fixed;bottom:0;left:0;right:0;height:52vh;
  background:linear-gradient(90deg,var(--dim) 1px,transparent 1px) center/100px 100px,
             linear-gradient(0deg,var(--dim) 1px,transparent 1px) center/100px 100px;
  transform:perspective(500px) rotateX(72deg);transform-origin:bottom center;opacity:.45;}
.floor::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,transparent 0%,var(--bg) 65%);}

/* horizon glow */
.horizon{position:fixed;left:0;right:0;top:46vh;height:1px;
  background:var(--dim);box-shadow:0 0 60px 12px var(--glow),0 0 140px 30px #001a2e;}

/* corner brackets */
.c{position:fixed;width:22px;height:22px;z-index:150;}
.c::before,.c::after{content:'';position:absolute;background:var(--cyan);}
.c::before{width:100%;height:2px;top:0;}.c::after{width:2px;height:100%;}
.tl{top:10px;left:10px;}.tr{top:10px;right:10px;transform:scaleX(-1);}
.bl{bottom:10px;left:10px;transform:scaleY(-1);}.br{bottom:10px;right:10px;transform:scale(-1);}

/* HUD */
.hud{position:fixed;top:0;left:0;right:0;padding:14px 28px;
  display:flex;justify-content:space-between;align-items:center;
  border-bottom:1px solid #001a2e;background:linear-gradient(to bottom,#00000f,transparent);z-index:100;
  font-size:.65rem;letter-spacing:.28em;}
.hud-r{color:var(--dim);}

/* highway stage */
.stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
  perspective:1100px;perspective-origin:50% 42%;}
.lane{display:flex;align-items:center;transform-style:preserve-3d;transition:none;}

/* cards */
.card{position:relative;flex-shrink:0;width:300px;margin:0 28px;cursor:pointer;
  transform-style:preserve-3d;transition:transform .55s cubic-bezier(.4,0,.2,1),opacity .55s ease,filter .55s ease;}
.card img{display:block;width:100%;aspect-ratio:1;object-fit:cover;
  border:1px solid var(--dim);transition:all .4s ease;}
/* corner brackets on card */
.card::before,.card::after{content:'';position:absolute;width:16px;height:16px;z-index:2;pointer-events:none;
  border-style:solid;border-color:var(--dim);transition:border-color .3s;}
.card::before{top:-1px;left:-1px;border-width:2px 0 0 2px;}
.card::after{bottom:-1px;right:-1px;border-width:0 2px 2px 0;}
.card .lbl{position:absolute;bottom:0;left:0;right:0;padding:28px 10px 8px;
  background:linear-gradient(to top,rgba(0,0,0,.9),transparent);
  font-size:.55rem;letter-spacing:.2em;color:var(--dim);text-align:center;opacity:0;transition:opacity .3s;}

/* states */
.card.active{transform:translateZ(80px) scale(1.1);z-index:10;}
.card.active img{border-color:var(--cyan);box-shadow:0 0 28px var(--glow),0 0 80px #00e5ff18;filter:brightness(1) saturate(1.5);}
.card.active::before,.card.active::after{border-color:var(--cyan);}
.card.active .lbl{opacity:1;color:var(--cyan);}
.card.p1,.card.n1{transform:translateZ(-60px) scale(.82);opacity:.55;filter:brightness(.6);}
.card.p2,.card.n2{transform:translateZ(-180px) scale(.62);opacity:.3;filter:brightness(.4);}
.card.p3,.card.n3{transform:translateZ(-320px) scale(.44);opacity:.14;filter:brightness(.3);}
.card.far{transform:translateZ(-460px) scale(.3);opacity:.05;filter:brightness(.2);}
.card.hide{opacity:0;pointer-events:none;transform:translateZ(-600px) scale(.2);}

/* nav */
.nav{position:fixed;top:50%;transform:translateY(-50%);z-index:100;
  background:none;border:none;color:var(--dim);font-size:1.2rem;letter-spacing:.1em;
  cursor:pointer;padding:14px 22px;transition:color .2s;}
.nav:hover{color:var(--cyan);}
.navL{left:12px;}.navR{right:12px;}

/* node info */
.info{position:fixed;bottom:28px;left:50%;transform:translateX(-50%);
  text-align:center;z-index:100;pointer-events:none;min-width:340px;}
.info .dn{font-size:.85rem;letter-spacing:.32em;}
.info .sq{font-size:.55rem;letter-spacing:.18em;color:var(--dim);margin-top:6px;}

/* light trails */
@keyframes tr{0%{transform:translateX(-110vw);opacity:0;}8%{opacity:1;}92%{opacity:1;}100%{transform:translateX(110vw);opacity:0;}}
.trail{position:fixed;height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);
  pointer-events:none;z-index:1;animation:tr linear infinite;}
</style>
</head>
<body>

<div class="floor"></div>
<div class="horizon"></div>
<div class="c tl"></div><div class="c tr"></div><div class="c bl"></div><div class="c br"></div>

<div class="hud">
  <span>&#9632;&nbsp; JARVIS GRID &mdash; DIGITAL HIGHWAY</span>
  <span class="hud-r" id="hcount">&#8213;</span>
</div>

<div class="stage"><div class="lane" id="lane"></div></div>

<button class="nav navL" onclick="move(-1)">&#9664;</button>
<button class="nav navR" onclick="move(1)">&#9654;</button>

<div class="info">
  <div class="dn" id="idn">&nbsp;</div>
  <div class="sq" id="isq">&nbsp;</div>
</div>

<script>
let files=[], cur=0, timer;

function slug(name){
  return name.replace(/\\.png$/,'').replace(/_\\d{4}-\\d{2}-\\d{2}$/,'').replace(/[-_]/g,' ').toUpperCase();
}

function cls(rel){
  if(rel===0)  return 'card active';
  if(rel===1)  return 'card n1';
  if(rel===-1) return 'card p1';
  if(rel===2)  return 'card n2';
  if(rel===-2) return 'card p2';
  if(rel===3)  return 'card n3';
  if(rel===-3) return 'card p3';
  if(Math.abs(rel)===4) return 'card far';
  return 'card hide';
}

function render(){
  const lane=document.getElementById('lane');
  lane.innerHTML=files.map((f,i)=>{
    const rel=i-cur;
    const isActive=rel===0;
    const nodeSlug=f.name.replace(/\\.png$/,'').replace(/_\\d{4}-\\d{2}-\\d{2}$/,'');
    const onclick=isActive?`window.location='/grid/node/${nodeSlug}'`:`activate(${i})`;
    return `<div class="${cls(rel)}" onclick="${onclick}" style="cursor:${isActive?'pointer':'default'}">
      <img src="/grid/img/${f.name}" alt="${f.name}" loading="lazy">
      <div class="lbl">${slug(f.name)}</div>
    </div>`;
  }).join('');
  const f=files[cur];
  if(f){
    document.getElementById('idn').textContent=slug(f.name);
    document.getElementById('isq').textContent=`${cur+1} / ${files.length}  —  CLICK TO ENTER DISTRICT  •  ←→ NAVIGATE`;
  }
  document.getElementById('hcount').textContent=`${files.length} NODE${files.length!==1?'S':''}`;
}

function activate(i){
  if(i===cur){ return; }
  cur=i; render(); resetTimer();
}

function move(d){
  if(!files.length) return;
  cur=(cur+d+files.length)%files.length;
  render(); resetTimer();
}

function resetTimer(){
  clearInterval(timer);
  timer=setInterval(()=>move(1),5000);
}

async function poll(){
  try{
    const r=await fetch('/grid/manifest');
    const d=await r.json();
    if(d.length!==files.length){ files=d; if(cur>=files.length)cur=0; render(); }
  }catch(e){}
}

document.addEventListener('keydown',e=>{
  if(e.key==='ArrowLeft'||e.key==='a') move(-1);
  if(e.key==='ArrowRight'||e.key==='d') move(1);
});

function spawnTrail(){
  const t=document.createElement('div');
  t.className='trail';
  t.style.top=Math.random()*100+'vh';
  t.style.width=(60+Math.random()*220)+'px';
  const dur=3+Math.random()*7;
  t.style.animationDuration=dur+'s';
  t.style.animationDelay=Math.random()*3+'s';
  t.style.opacity=.15+Math.random()*.35;
  document.body.appendChild(t);
  setTimeout(()=>t.remove(),(dur+3)*1000);
}

(async()=>{
  const r=await fetch('/grid/manifest');
  files=await r.json();
  render(); resetTimer();
  setInterval(poll,3000);
  setInterval(spawnTrail,900);
  for(let i=0;i<6;i++) spawnTrail();
})();
</script>
</body>
</html>"""

_LIVE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JARVIS — Live Feed</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');
  :root{--bg:#020408;--surface:#080f18;--card:#0c1520;--border:#0f2035;--amber:#f5a623;--green:#00ff88;--red:#ff3355;--blue:#0af;--dim:#1e3a52;--text:#4a7a99;--bright:#a0c8e0;--mono:'Share Tech Mono',monospace;--display:'Orbitron',sans-serif;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--text);font-family:var(--mono);font-size:11px;height:100vh;display:grid;grid-template-rows:48px 1fr;overflow:hidden;}
  body::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.04) 2px,rgba(0,0,0,.04) 4px);pointer-events:none;z-index:1000;}
  .topbar{background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 20px;gap:20px;}
  .logo{font-family:var(--display);font-size:16px;font-weight:900;letter-spacing:5px;color:var(--amber);text-shadow:0 0 15px rgba(245,166,35,.3);}
  .logo span{color:var(--dim);}
  .live-dot{width:6px;height:6px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green);animation:blink 1.5s infinite;}
  @keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
  .topbar-right{margin-left:auto;display:flex;align-items:center;gap:16px;font-size:9px;color:var(--dim);letter-spacing:2px;}
  .main{display:grid;grid-template-columns:1fr 320px;gap:1px;background:var(--border);overflow:hidden;}
  .feed-panel{background:var(--bg);display:flex;flex-direction:column;overflow:hidden;}
  .feed-header{background:var(--surface);padding:8px 16px;font-size:8px;letter-spacing:4px;color:var(--dim);border-bottom:1px solid var(--border);display:flex;justify-content:space-between;}
  .feed-scroll{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:4px;}
  .feed-scroll::-webkit-scrollbar{width:3px;}.feed-scroll::-webkit-scrollbar-thumb{background:var(--border);}
  .entry{display:grid;grid-template-columns:70px 80px 1fr 60px;gap:8px;padding:6px 8px;border-left:2px solid var(--border);background:var(--card);animation:fadeIn .3s ease;align-items:center;}
  @keyframes fadeIn{from{opacity:0;transform:translateX(-8px)}to{opacity:1}}
  .entry.done{border-left-color:var(--green)}.entry.working{border-left-color:var(--amber);animation:pulse-border 1s infinite}.entry.failed{border-left-color:var(--red)}
  @keyframes pulse-border{0%,100%{border-left-color:var(--amber)}50%{border-left-color:rgba(245,166,35,.3)}}
  .entry-time{color:var(--dim);font-size:9px}.entry-action{color:var(--bright);font-size:10px}.entry-file{color:var(--text);font-size:9px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .entry-status{font-size:8px;letter-spacing:2px;text-align:right}
  .status-done{color:var(--green)}.status-working{color:var(--amber)}.status-failed{color:var(--red)}
  .sidebar{background:var(--surface);padding:16px;display:flex;flex-direction:column;gap:16px;overflow-y:auto;}
  .card{background:var(--card);border:1px solid var(--border);padding:12px;}
  .card-label{font-size:8px;letter-spacing:4px;color:var(--dim);border-bottom:1px solid var(--border);padding-bottom:6px;margin-bottom:10px;text-transform:uppercase;}
  .stat-row{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border);font-size:10px;}.stat-row:last-child{border-bottom:none;}
  .stat-k{color:var(--text)}.stat-v.ok{color:var(--green)}.stat-v.warn{color:var(--amber)}.stat-v.err{color:var(--red)}
  .activity-bar{display:flex;gap:2px;align-items:flex-end;height:40px;}
  .bar{flex:1;background:var(--amber);opacity:.6;min-height:2px;transition:height .3s ease;}
  .empty-state{color:var(--dim);font-size:9px;letter-spacing:2px;text-align:center;padding:40px 20px;line-height:2;}
  .cursor{display:inline-block;width:8px;height:12px;background:var(--amber);animation:cursor-blink 1s step-end infinite;vertical-align:middle;margin-left:4px;}
  @keyframes cursor-blink{0%,100%{opacity:1}50%{opacity:0}}
  .btn{width:100%;padding:8px;background:transparent;border:1px solid #7a4f0a;color:var(--amber);font-family:var(--mono);font-size:9px;letter-spacing:2px;cursor:pointer;text-align:left;}
  .btn:hover{background:var(--amber);color:var(--bg);}
  .instruction{font-size:9px;line-height:1.8;color:var(--text);}
  .instruction code{color:var(--amber);background:var(--bg);padding:1px 4px;}
  .nav-links{display:flex;gap:8px;flex-wrap:wrap;}
  .nav-link{font-size:9px;letter-spacing:2px;color:var(--dim);text-decoration:none;padding:6px 10px;border:1px solid var(--border);}
  .nav-link:hover{color:var(--amber);border-color:var(--amber);}
</style>
</head>
<body>
<div class="topbar">
  <div class="logo">JARVIS <span>LIVE</span></div>
  <div class="live-dot"></div>
  <span style="font-size:9px;color:var(--dim);letter-spacing:2px">CLAUDE CODE FEED</span>
  <div class="topbar-right">
    <span id="entry-count">0 ENTRIES</span>
    <span id="last-update">—</span>
    <span id="connection-status" style="color:var(--amber)">WAITING</span>
  </div>
</div>
<div class="main">
  <div class="feed-panel">
    <div class="feed-header">
      <span>LIVE FEED</span>
      <span id="feed-status">Connecting to /live_log.json...</span>
    </div>
    <div class="feed-scroll" id="feed">
      <div class="empty-state">Waiting for JARVIS activity<span class="cursor"></span><br><br>PROMETHEUS decisions appear here automatically.<br>POST to /live_log to push custom entries.</div>
    </div>
  </div>
  <div class="sidebar">
    <div class="card">
      <div class="card-label">Session Stats</div>
      <div class="stat-row"><span class="stat-k">Total Actions</span><span class="stat-v ok" id="stat-total">0</span></div>
      <div class="stat-row"><span class="stat-k">Completed</span><span class="stat-v ok" id="stat-done">0</span></div>
      <div class="stat-row"><span class="stat-k">In Progress</span><span class="stat-v warn" id="stat-working">0</span></div>
      <div class="stat-row"><span class="stat-k">Failed</span><span class="stat-v err" id="stat-failed">0</span></div>
      <div class="stat-row"><span class="stat-k">Success Rate</span><span class="stat-v ok" id="stat-rate">—</span></div>
    </div>
    <div class="card">
      <div class="card-label">Activity</div>
      <div class="activity-bar" id="activity-bar">
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
      </div>
    </div>
    <div class="card">
      <div class="card-label">Navigate</div>
      <div class="nav-links">
        <a href="/grid" class="nav-link">&#9632; GRID</a>
        <a href="/health" class="nav-link">&#9632; HEALTH</a>
      </div>
    </div>
    <div class="card">
      <div class="card-label">Hook Setup</div>
      <div class="instruction">
        Add to <code>~/.claude/settings.json</code>:<br><br>
        <code>"PostToolUse"</code> hook → POST to<br>
        <code>localhost:7777/live_log</code><br><br>
        Body: <code>{"action":"...","file":"...","status":"done"}</code><br><br>
        PROMETHEUS decisions auto-appear via <code>jarvis_log</code>.
      </div>
    </div>
    <div class="card">
      <div class="card-label">Controls</div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <button class="btn" onclick="clearFeed()">&#9658; CLEAR FEED</button>
        <button class="btn" onclick="testEntry()">&#9658; TEST ENTRY</button>
      </div>
    </div>
  </div>
</div>
<script>
let entries=[], lastLen=0, activityHistory=new Array(10).fill(0);

async function pollLog(){
  try{
    const r=await fetch('/live_log.json?t='+Date.now());
    if(!r.ok) throw new Error();
    const data=await r.json();
    document.getElementById('connection-status').textContent='CONNECTED';
    document.getElementById('connection-status').style.color='var(--green)';
    document.getElementById('feed-status').textContent='Live — /live_log.json';
    if(data.length!==lastLen){entries=data.slice(-100);lastLen=data.length;renderFeed();updateStats();document.getElementById('last-update').textContent=new Date().toLocaleTimeString();}
  }catch{
    document.getElementById('connection-status').textContent='WAITING';
    document.getElementById('connection-status').style.color='var(--amber)';
  }
}

function renderFeed(){
  const feed=document.getElementById('feed');
  if(!entries.length) return;
  feed.innerHTML=[...entries].reverse().map(e=>`
    <div class="entry ${e.status||'done'}">
      <span class="entry-time">${e.time||'—'}</span>
      <span class="entry-action">${(e.action||'').slice(0,24)}</span>
      <span class="entry-file">${e.file||''}</span>
      <span class="entry-status status-${e.status||'done'}">${(e.status||'DONE').toUpperCase()}</span>
    </div>`).join('');
  document.getElementById('entry-count').textContent=`${entries.length} ENTRIES`;
}

function updateStats(){
  const done=entries.filter(e=>e.status==='done').length;
  const working=entries.filter(e=>e.status==='working').length;
  const failed=entries.filter(e=>e.status==='failed').length;
  const total=entries.length;
  document.getElementById('stat-total').textContent=total;
  document.getElementById('stat-done').textContent=done;
  document.getElementById('stat-working').textContent=working;
  document.getElementById('stat-failed').textContent=failed;
  document.getElementById('stat-rate').textContent=total>0?Math.round(done/total*100)+'%':'—';
  activityHistory.push(total);activityHistory=activityHistory.slice(-10);
  const max=Math.max(...activityHistory,1);
  document.querySelectorAll('#activity-bar .bar').forEach((b,i)=>{b.style.height=Math.max(2,activityHistory[i]/max*40)+'px';});
}

function clearFeed(){entries=[];lastLen=0;document.getElementById('feed').innerHTML='<div class="empty-state">Feed cleared<span class="cursor"></span></div>';updateStats();}

function testEntry(){
  entries.push({time:new Date().toLocaleTimeString(),action:'Test entry fired',file:'jarvis_mcp_server.py',status:'done'});
  lastLen=entries.length;renderFeed();updateStats();
}

setInterval(pollLog,1000);
pollLog();
</script>
</body>
</html>"""

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JARVIS — Command Center</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');
  :root{
    --bg:#020408;--surface:#080f18;--card:#0c1520;--border:#0f2035;
    --amber:#f5a623;--green:#00ff88;--red:#ff3355;--blue:#0af;
    --dim:#1e3a52;--text:#4a7a99;--bright:#a0c8e0;
    --mono:'Share Tech Mono',monospace;--display:'Orbitron',sans-serif;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--text);font-family:var(--mono);font-size:11px;
       height:100vh;display:grid;grid-template-rows:48px 1fr;overflow:hidden;}
  body::before{content:'';position:fixed;inset:0;
    background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.04) 2px,rgba(0,0,0,.04) 4px);
    pointer-events:none;z-index:1000;}
  /* ── topbar ── */
  .topbar{background:var(--surface);border-bottom:1px solid var(--border);
          display:flex;align-items:center;padding:0 20px;gap:16px;}
  .logo{font-family:var(--display);font-size:15px;font-weight:900;letter-spacing:5px;
        color:var(--amber);text-shadow:0 0 15px rgba(245,166,35,.3);}
  .logo span{color:var(--dim);}
  .live-dot{width:6px;height:6px;border-radius:50%;background:var(--green);
            box-shadow:0 0 8px var(--green);animation:blink 1.5s infinite;}
  @keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
  .topbar-nav{margin-left:auto;display:flex;gap:12px;}
  .nav-btn{font-family:var(--mono);font-size:9px;letter-spacing:2px;color:var(--dim);
           background:transparent;border:1px solid var(--border);padding:5px 10px;
           cursor:pointer;text-decoration:none;}
  .nav-btn:hover{color:var(--amber);border-color:var(--amber);}
  /* ── 3-column main ── */
  .main{display:grid;grid-template-columns:280px 1fr 260px;gap:1px;background:var(--border);overflow:hidden;}
  /* ── LIVE FEED (left) ── */
  .feed-col{background:var(--bg);display:flex;flex-direction:column;overflow:hidden;}
  .col-header{background:var(--surface);padding:7px 12px;font-size:8px;letter-spacing:4px;
              color:var(--dim);border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;}
  .feed-scroll{flex:1;overflow-y:auto;padding:8px;display:flex;flex-direction:column;gap:3px;}
  .feed-scroll::-webkit-scrollbar{width:2px;}.feed-scroll::-webkit-scrollbar-thumb{background:var(--border);}
  .entry{display:grid;grid-template-columns:58px 1fr 48px;gap:6px;padding:5px 7px;
         border-left:2px solid var(--border);background:var(--card);animation:fadeIn .3s ease;align-items:center;}
  @keyframes fadeIn{from{opacity:0;transform:translateX(-6px)}to{opacity:1}}
  .entry.done{border-left-color:var(--green)}.entry.working{border-left-color:var(--amber)}.entry.failed{border-left-color:var(--red)}
  .e-time{color:var(--dim);font-size:8px;}
  .e-action{color:var(--bright);font-size:9px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .e-status{font-size:7px;letter-spacing:2px;text-align:right;}
  .s-done{color:var(--green)}.s-working{color:var(--amber)}.s-failed{color:var(--red)}
  .empty-state{color:var(--dim);font-size:9px;letter-spacing:2px;text-align:center;padding:30px 12px;line-height:2;}
  .cursor{display:inline-block;width:7px;height:11px;background:var(--amber);
          animation:cblink 1s step-end infinite;vertical-align:middle;margin-left:3px;}
  @keyframes cblink{0%,100%{opacity:1}50%{opacity:0}}
  /* ── IMAGE (center) ── */
  .img-col{background:var(--bg);display:flex;flex-direction:column;overflow:hidden;}
  .img-stage{flex:1;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;}
  .img-stage img{max-width:100%;max-height:100%;object-fit:contain;display:block;
                 border:1px solid var(--border);image-rendering:pixelated;}
  .img-overlay{position:absolute;inset:0;pointer-events:none;
    background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,200,255,.015) 3px,rgba(0,200,255,.015) 4px);}
  .img-controls{background:var(--surface);border-top:1px solid var(--border);
                padding:8px 16px;display:flex;align-items:center;gap:12px;}
  .img-name{flex:1;color:var(--bright);font-size:9px;letter-spacing:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .img-counter{color:var(--dim);font-size:8px;white-space:nowrap;}
  .ctrl-btn{background:transparent;border:1px solid var(--border);color:var(--dim);
            font-family:var(--mono);font-size:11px;padding:4px 10px;cursor:pointer;}
  .ctrl-btn:hover{border-color:var(--amber);color:var(--amber);}
  .auto-badge{font-size:7px;letter-spacing:2px;padding:3px 6px;border:1px solid var(--border);color:var(--dim);}
  .auto-badge.on{border-color:var(--green);color:var(--green);}
  .no-images{color:var(--dim);text-align:center;padding:40px;font-size:10px;line-height:2;}
  /* ── GRID NAV (right) ── */
  .grid-col{background:var(--surface);display:flex;flex-direction:column;overflow-y:auto;}
  .grid-col::-webkit-scrollbar{width:2px;}.grid-col::-webkit-scrollbar-thumb{background:var(--border);}
  .district-card{border-bottom:1px solid var(--border);padding:10px 12px;cursor:pointer;transition:background .15s;}
  .district-card:hover{background:var(--card);}
  .district-card a{text-decoration:none;display:block;}
  .d-region{font-size:7px;letter-spacing:3px;color:var(--dim);margin-bottom:3px;}
  .d-name{color:var(--bright);font-size:10px;margin-bottom:4px;}
  .d-keywords{color:var(--text);font-size:8px;line-height:1.6;overflow:hidden;
              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;}
  .d-img-thumb{width:100%;height:60px;object-fit:cover;margin-bottom:6px;border:1px solid var(--border);display:block;}
  .grid-footer{padding:12px;border-top:1px solid var(--border);}
  .grid-all-btn{display:block;text-align:center;font-size:8px;letter-spacing:3px;color:var(--dim);
               padding:8px;border:1px solid var(--border);text-decoration:none;}
  .grid-all-btn:hover{color:var(--amber);border-color:var(--amber);}
  /* ── stat strip ── */
  .stat-strip{background:var(--card);border-top:1px solid var(--border);
              display:flex;gap:1px;padding:0;}
  .stat-cell{flex:1;padding:5px 8px;border-right:1px solid var(--border);font-size:8px;letter-spacing:1px;}
  .stat-cell:last-child{border-right:none;}
  .stat-cell .sk{color:var(--dim)}.stat-cell .sv{color:var(--green);}
  .stat-cell .sv.warn{color:var(--amber)}.stat-cell .sv.err{color:var(--red)}
</style>
</head>
<body>
<div class="topbar">
  <div class="logo">JARVIS <span>CMD</span></div>
  <div class="live-dot"></div>
  <span style="font-size:9px;color:var(--dim);letter-spacing:3px">COMMAND CENTER</span>
  <div class="topbar-nav">
    <a href="/grid" class="nav-btn">GRID</a>
    <a href="/live" class="nav-btn">LIVE</a>
    <a href="/health" class="nav-btn">HEALTH</a>
  </div>
</div>

<div class="main">

  <!-- ── LEFT: LIVE FEED ── -->
  <div class="feed-col">
    <div class="col-header">
      <span>LIVE FEED</span>
      <span id="feed-ts" style="color:var(--dim);font-size:7px">—</span>
    </div>
    <div class="feed-scroll" id="feed">
      <div class="empty-state" id="feed-empty">
        Waiting for activity<span class="cursor"></span>
      </div>
    </div>
    <div class="stat-strip">
      <div class="stat-cell"><div class="sk">TOTAL</div><div class="sv" id="s-total">0</div></div>
      <div class="stat-cell"><div class="sk">DONE</div><div class="sv" id="s-done">0</div></div>
      <div class="stat-cell"><div class="sk">WORK</div><div class="sv warn" id="s-work">0</div></div>
      <div class="stat-cell"><div class="sk">FAIL</div><div class="sv err" id="s-fail">0</div></div>
    </div>
  </div>

  <!-- ── CENTER: PILLOW IMAGE DISPLAY ── -->
  <div class="img-col">
    <div class="col-header">
      <span>GRID IMAGES</span>
      <span id="img-status" style="font-size:7px;color:var(--dim)">Polling /grid/manifest…</span>
    </div>
    <div class="img-stage" id="img-stage">
      <div class="no-images" id="no-images">
        No images yet.<br>Run <span style="color:var(--amber)">jarvis_image</span> to generate grid cards.
      </div>
      <img id="main-img" src="" alt="" style="display:none">
      <div class="img-overlay"></div>
    </div>
    <div class="img-controls">
      <button class="ctrl-btn" id="btn-prev">&#8592;</button>
      <button class="ctrl-btn" id="btn-next">&#8594;</button>
      <div class="img-name" id="img-name">—</div>
      <div class="img-counter" id="img-counter">0 / 0</div>
      <div class="auto-badge on" id="auto-badge">AUTO</div>
    </div>
  </div>

  <!-- ── RIGHT: GRID NAV ── -->
  <div class="grid-col">
    <div class="col-header" style="position:sticky;top:0;z-index:10;">
      <span>GRID DISTRICTS</span>
      <span style="font-size:7px" id="district-count">—</span>
    </div>
    <div id="district-list"></div>
    <div class="grid-footer">
      <a href="/grid" class="grid-all-btn">&#9632; FULL GRID HIGHWAY</a>
    </div>
  </div>

</div>

<script>
// ── LIVE FEED ──────────────────────────────────────────────────────────────
let lastFeedLen = 0;
function renderFeed(entries) {
  const feed  = document.getElementById('feed');
  const empty = document.getElementById('feed-empty');
  if (!entries.length) { empty.style.display=''; return; }
  empty.style.display = 'none';

  const existing = feed.querySelectorAll('.entry').length;
  entries.slice(existing).forEach(e => {
    const el = document.createElement('div');
    el.className = 'entry ' + (e.status || 'done');
    const action = (e.action || '').substring(0, 38);
    el.innerHTML = `
      <div class="e-time">${e.time || '--:--:--'}</div>
      <div class="e-action" title="${e.action || ''}">${action}</div>
      <div class="e-status s-${e.status || 'done'}">${(e.status||'done').toUpperCase()}</div>
    `;
    feed.appendChild(el);
  });
  feed.scrollTop = feed.scrollHeight;

  document.getElementById('s-total').textContent = entries.length;
  document.getElementById('s-done').textContent  = entries.filter(e=>e.status==='done').length;
  document.getElementById('s-work').textContent  = entries.filter(e=>e.status==='working').length;
  document.getElementById('s-fail').textContent  = entries.filter(e=>e.status==='failed').length;
  document.getElementById('feed-ts').textContent = new Date().toLocaleTimeString();
}
async function pollFeed() {
  try {
    const r = await fetch('/live_log.json');
    if (r.ok) renderFeed(await r.json());
  } catch(e) {}
}
setInterval(pollFeed, 2000);
pollFeed();

// ── IMAGE CAROUSEL ─────────────────────────────────────────────────────────
let images   = [];
let imgIdx   = 0;
let autoPlay = true;
let autoTimer = null;

function showImage(idx) {
  if (!images.length) return;
  imgIdx = ((idx % images.length) + images.length) % images.length;
  const img   = document.getElementById('main-img');
  const name  = document.getElementById('img-name');
  const ctr   = document.getElementById('img-counter');
  const noImg = document.getElementById('no-images');
  const entry = images[imgIdx];
  img.style.display = 'block';
  noImg.style.display = 'none';
  // Use /grid/frame for Pillow-annotated version
  img.src = '/grid/frame/' + entry.name + '?t=' + Date.now();
  name.textContent = entry.name.replace(/_/g,' ').replace(/-/g,' ').replace('.png','');
  ctr.textContent  = (imgIdx + 1) + ' / ' + images.length;
  resetAutoTimer();
}

function resetAutoTimer() {
  if (autoTimer) clearInterval(autoTimer);
  if (autoPlay) autoTimer = setInterval(() => showImage(imgIdx + 1), 4000);
}

document.getElementById('btn-prev').onclick = () => { showImage(imgIdx - 1); };
document.getElementById('btn-next').onclick = () => { showImage(imgIdx + 1); };
document.getElementById('auto-badge').onclick = function() {
  autoPlay = !autoPlay;
  this.textContent = autoPlay ? 'AUTO' : 'PAUSED';
  this.className   = 'auto-badge' + (autoPlay ? ' on' : '');
  resetAutoTimer();
};

async function pollImages() {
  try {
    const r = await fetch('/grid/manifest');
    if (!r.ok) return;
    const data = await r.json();
    document.getElementById('img-status').textContent = data.length + ' images';
    if (data.length !== images.length) {
      images = data.sort((a,b) => b.mtime - a.mtime);
      if (data.length) showImage(0);
    }
  } catch(e) {}
}
setInterval(pollImages, 5000);
pollImages();

// ── GRID DISTRICTS ─────────────────────────────────────────────────────────
async function loadDistricts() {
  try {
    const r = await fetch('/grid/districts');
    if (!r.ok) return;
    const districts = await r.json();
    document.getElementById('district-count').textContent = districts.length + ' nodes';
    const list = document.getElementById('district-list');
    list.innerHTML = '';
    districts.forEach(d => {
      const slug  = d.file.replace('.md','');
      const imgs  = d.images || [];
      const thumb = imgs.length ? `<img class="d-img-thumb" src="/grid/frame/${imgs[0]}" loading="lazy">` : '';
      const el    = document.createElement('div');
      el.className = 'district-card';
      el.innerHTML = `<a href="/grid/node/${slug}">
        ${thumb}
        <div class="d-region">${d.region || ''}</div>
        <div class="d-name">${d.district || slug}</div>
        <div class="d-keywords">${(d.keywords||[]).slice(0,6).join(', ')}</div>
      </a>`;
      list.appendChild(el);
    });
  } catch(e) {}
}
loadDistricts();
</script>
</body>
</html>"""

_GAMEBOY_SW_JS = """
const CACHE = 'jarvis-gb-v3';
const STATIC = ['/gameboy'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC)));
  self.skipWaiting();
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
self.addEventListener('push', e => {
  const d = e.data ? e.data.json() : {title:'JARVIS',body:'Alert',url:'/gameboy'};
  e.waitUntil(self.registration.showNotification(d.title, {
    body: d.body,
    data: {url: d.url || '/gameboy'},
    tag: 'jarvis-alert',
    renotify: true,
  }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(clients.openWindow(e.notification.data.url || '/gameboy'));
});
"""

_GAMEBOY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JARVIS HANDHELD</title>
<link rel="manifest" href="/gameboy/manifest.json">
<meta name="theme-color" content="#f5a623">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="JARVIS">
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
:root {
  --pixel: 'Press Start 2P', monospace;
  --amber: #f5a623; --green: #00ff88; --blue: #0af; --red: #ff3355;
  --dim: #1e3a52; --text: #4a7a99; --bright: #a0c8e0;
  --bg: #020408; --surface: #080f18;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  background: radial-gradient(ellipse at center, #0a0f1a 0%, #020408 100%);
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; font-family: var(--pixel); user-select: none;
}

/* ── DEVICE SHELL ── */
.device {
  width: 340px;
  background: linear-gradient(160deg, #4a4a4a 0%, #2d2d2d 60%, #222 100%);
  border-radius: 14px 14px 52px 52px;
  padding: 18px 18px 32px;
  position: relative;
  box-shadow: 5px 5px 0 #111, 9px 9px 0 #0a0a0a,
    inset 0 1px 0 rgba(255,255,255,.13), inset 0 -2px 0 rgba(0,0,0,.5);
  background-image:
    repeating-linear-gradient(0deg, rgba(0,0,0,.05) 0, rgba(0,0,0,.05) 1px, transparent 1px, transparent 4px),
    repeating-linear-gradient(90deg, rgba(0,0,0,.05) 0, rgba(0,0,0,.05) 1px, transparent 1px, transparent 4px);
}

.led {
  position: absolute; top: 18px; right: 22px;
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green); box-shadow: 0 0 8px var(--green);
  animation: led-blink 2s infinite;
}
@keyframes led-blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ── SCREEN HOUSING (Minecraft item-frame) ── */
.screen-housing {
  background: #120a02;
  border: 6px solid #6b4420;
  box-shadow: inset 0 0 0 2px #2e1a08, inset 0 0 0 4px #8a5a30,
    0 0 0 1px #1a0a00, 0 4px 14px rgba(0,0,0,.7);
  border-radius: 3px; padding: 8px; margin-bottom: 4px;
}
.screen-label {
  text-align: center; font-size: 5px; letter-spacing: 4px;
  color: #5a3d1c; margin-bottom: 6px;
}

/* ── LCD SCREEN ── */
.screen {
  width: 100%; height: 216px;
  background: var(--bg); border: 2px solid #0a0f1a;
  position: relative; overflow: hidden;
}
.screen::before {
  content: ''; position: absolute; inset: 0; z-index: 100; pointer-events: none;
  background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,.09) 2px, rgba(0,0,0,.09) 4px);
}
.screen::after {
  content: ''; position: absolute; top: 0; left: 0; right: 50%; height: 45%;
  background: linear-gradient(135deg, rgba(255,255,255,.04), transparent);
  z-index: 101; pointer-events: none;
}
#screen-inner { position: absolute; inset: 0; overflow: hidden; font-family: var(--pixel); font-size: 7px; color: var(--text); }

/* ── SCREEN PANELS ── */
.panel { display: flex; flex-direction: column; height: 100%; }
.s-header {
  background: var(--surface); border-bottom: 1px solid #0f2035;
  padding: 5px 8px; font-size: 7px; color: var(--amber); letter-spacing: 2px;
  display: flex; justify-content: space-between; flex-shrink: 0;
}
.s-body { flex: 1; padding: 6px 8px; overflow: hidden; }
.s-body.scroll { overflow-y: auto; }
.s-body.scroll::-webkit-scrollbar { width: 2px; }
.s-body.scroll::-webkit-scrollbar-thumb { background: var(--dim); }
.s-footer {
  background: var(--surface); border-top: 1px solid #0f2035;
  padding: 4px 8px; font-size: 5px; color: var(--dim); letter-spacing: 1px; flex-shrink: 0;
}
.row {
  padding: 3px 4px; font-size: 7px; line-height: 1.7;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  color: var(--bright); display: flex; align-items: center; gap: 4px;
}
.row.sel { color: var(--amber); background: rgba(245,166,35,.07); }
.row .sub { color: var(--dim); font-size: 5px; }
.dl { color: var(--dim); font-size: 5px; letter-spacing: 2px; margin: 6px 0 2px; }
.dv { color: var(--bright); font-size: 6px; line-height: 1.8; word-break: break-word; margin-bottom: 4px; }
.rule { padding: 2px 0; border-bottom: 1px solid #0f2035; font-size: 6px; line-height: 1.9; }
.rule.sel { color: var(--amber); }
.live-e { display: flex; gap: 5px; padding: 2px 0; border-bottom: 1px solid #080f18; font-size: 6px; }
.lt { color: var(--dim); flex-shrink: 0; }
.la { color: var(--bright); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ls-done { color: var(--green); flex-shrink: 0; }
.ls-working { color: var(--amber); flex-shrink: 0; }
.ls-failed { color: var(--red); flex-shrink: 0; }

/* ── BOOT ── */
.boot-panel {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; gap: 10px; padding: 0 16px;
}
.boot-logo {
  font-size: 22px; color: var(--amber); letter-spacing: 10px;
  text-shadow: 0 0 20px rgba(245,166,35,.5); animation: gbglow 2s ease-in-out infinite;
}
@keyframes gbglow { 0%,100%{text-shadow:0 0 10px rgba(245,166,35,.3)} 50%{text-shadow:0 0 30px rgba(245,166,35,.8)} }
.boot-sub { font-size: 5px; color: var(--dim); letter-spacing: 3px; }
.boot-lines { width: 100%; min-height: 72px; font-size: 6px; line-height: 2; }
.boot-line { color: var(--green); animation: gbfade .3s ease; }
@keyframes gbfade { from{opacity:0} to{opacity:1} }
.boot-hint { font-size: 5px; color: var(--dim); animation: gblink 1s step-end infinite; }
@keyframes gblink { 0%,100%{opacity:1} 50%{opacity:0} }

/* ── BRAND + CONTROLS ── */
.brand { text-align: center; font-size: 6px; letter-spacing: 7px; color: #3a3a3a; padding: 6px 0 10px; text-shadow: 0 1px 0 #555; }

.ctrl-row { display: flex; align-items: center; justify-content: space-between; padding: 0 8px; margin-bottom: 14px; }

/* D-pad */
.dpad { position: relative; width: 78px; height: 78px; flex-shrink: 0; }
.dph, .dpv { position: absolute; background: #1e1e1e; border-radius: 2px; }
.dph { width: 78px; height: 26px; top: 26px; left: 0; box-shadow: 0 3px 0 #111, inset 0 1px 0 rgba(255,255,255,.08); }
.dpv { width: 26px; height: 78px; left: 26px; top: 0; box-shadow: 2px 0 0 #111; }
.dpc { position: absolute; width: 26px; height: 26px; background: #161616; top: 26px; left: 26px; z-index: 2; }
.dpb { position: absolute; background: transparent; border: none; cursor: pointer; z-index: 3;
       color: #3a3a3a; font-size: 9px; display: flex; align-items: center; justify-content: center; }
.dpb:active { background: rgba(255,255,255,.08); }
.dpb.up    { width: 26px; height: 26px; top: 0; left: 26px; }
.dpb.dn    { width: 26px; height: 26px; bottom: 0; left: 26px; }
.dpb.lf    { width: 26px; height: 26px; left: 0; top: 26px; }
.dpb.rt    { width: 26px; height: 26px; right: 0; top: 26px; }

/* Face buttons */
.face { position: relative; width: 88px; height: 78px; flex-shrink: 0; }
.fb { position: absolute; width: 34px; height: 34px; border-radius: 50%; border: none; cursor: pointer;
      font-family: var(--pixel); font-size: 9px; }
.fb:active { transform: translateY(2px); }
.fb.a { background: linear-gradient(145deg, #c83322, #881811); box-shadow: 0 4px 0 #550f00, 0 4px 10px rgba(0,0,0,.5); color: #ffccaa; right: 0; top: 22px; }
.fb.b { background: linear-gradient(145deg, #223caa, #111e66); box-shadow: 0 4px 0 #001040, 0 4px 10px rgba(0,0,0,.5); color: #aac8ff; left: 0; top: 22px; }
.fbl { position: absolute; font-size: 5px; color: #4a4a4a; letter-spacing: 1px; }
.fbl.a { right: 6px; top: 6px; }
.fbl.b { left: 8px; top: 6px; }

/* Select/Start */
.menu-row { display: flex; justify-content: center; gap: 22px; margin-bottom: 18px; }
.mb { background: #1e1e1e; border: 1px solid #2e2e2e; border-radius: 10px; padding: 5px 14px;
      color: #4a4a4a; font-family: var(--pixel); font-size: 5px; letter-spacing: 1px;
      cursor: pointer; box-shadow: 0 2px 0 #111; transform: rotate(-12deg); }
.mb:active { transform: rotate(-12deg) translateY(1px); box-shadow: none; }

/* Speaker */
.speaker { position: absolute; bottom: 22px; right: 20px;
           display: grid; grid-template-columns: repeat(5, 4px); grid-template-rows: repeat(3, 4px); gap: 3px; }
.sp { width: 4px; height: 4px; border-radius: 50%; background: #1a1a1a; box-shadow: inset 0 1px 0 rgba(0,0,0,.9); }
</style>
</head>
<body>
<div class="device">
  <div class="led"></div>

  <div class="screen-housing">
    <div class="screen-label">JARVIS GRID INTERFACE &nbsp;<span id="sse-dot" style="color:#333">●</span></div>
    <div class="screen">
      <div id="screen-inner"></div>
    </div>
  </div>

  <div class="brand">JARVIS</div>

  <div class="ctrl-row">
    <div class="dpad">
      <div class="dph"></div>
      <div class="dpv"></div>
      <div class="dpc"></div>
      <button class="dpb up" onclick="nav(-1)">&#9650;</button>
      <button class="dpb dn" onclick="nav(1)">&#9660;</button>
      <button class="dpb lf" onclick="back()">&#9664;</button>
      <button class="dpb rt" onclick="ok()">&#9654;</button>
    </div>
    <div class="face">
      <span class="fbl b">B</span>
      <span class="fbl a">A</span>
      <button class="fb b" onclick="back()">B</button>
      <button class="fb a" onclick="ok()">A</button>
    </div>
  </div>

  <div class="menu-row">
    <button class="mb" onclick="back()">SELECT</button>
    <button class="mb" onclick="start()">START</button>
  </div>

  <div class="speaker" id="spk"></div>
</div>

<script>
// ── speaker dots
(function(){ const s=document.getElementById('spk'); for(let i=0;i<15;i++){const d=document.createElement('div');d.className='sp';s.appendChild(d);} })();

// ── state
let S='boot', cur=0, detail=null, gdata=null, lives=[];
let sseConnected=false, _sse=null;
const PG=7;

const MENU=[
  {label:'GOD SYSTEMS', state:'god'},
  {label:'GOLD LAW',    state:'gold'},
  {label:'THE GRID',    state:'grid'},
  {label:'LIVE FEED',   state:'live'},
  {label:'ALERTS',      state:'alerts'},
  {label:'GITHUB',      state:'github'},
];

// ── render
function draw(){
  const el=document.getElementById('screen-inner');
  if(S==='menu')       el.innerHTML=rMenu();
  else if(S==='god')   el.innerHTML=rGodList();
  else if(S==='godD')  el.innerHTML=rGodDetail();
  else if(S==='gold')  el.innerHTML=rGold();
  else if(S==='grid')  el.innerHTML=rGrid();
  else if(S==='gridD') el.innerHTML=rGridDetail();
  else if(S==='live')  el.innerHTML=rLive();
  else if(S==='alerts') el.innerHTML=rAlerts();
  else if(S==='github') el.innerHTML=rGithub();
  else if(S==='ghIssue') el.innerHTML=rGhIssue();
}

function cursor(i,sel){ return `<span style="color:${sel?'var(--amber)':'var(--dim)'}">${sel?'&#9658;':' '}</span>`; }

function rMenu(){
  const subs=[
    gdata?gdata.god_systems.length+' NODES':'...',
    gdata?gdata.gold_law.length+' RULES':'...',
    gdata?gdata.districts.length+' DISTRICTS':'...',
    lives.length+' ENTRIES',
    pushSubbed?'ON':'OFF',
  ];
  return `<div class="panel">
    <div class="s-header"><span>JARVIS v2.5</span><span style="color:var(--green)">&#9632; ONLINE</span></div>
    <div class="s-body" style="padding-top:10px">
      ${MENU.map((m,i)=>`<div class="row ${cur===i?'sel':''}">${cursor(i,cur===i)} ${m.label} <span class="sub">${subs[i]}</span></div>`).join('')}
    </div>
    <div class="s-footer">A:SELECT &nbsp; &#8593;&#8595;:MOVE &nbsp; START:MENU</div>
  </div>`;
}

function rGodList(){
  if(!gdata) return rLoad();
  const sys=gdata.god_systems, pip=gdata.pipeline||[];
  const st=Math.floor(cur/PG)*PG, pg=sys.slice(st,st+PG);
  return `<div class="panel">
    <div class="s-header"><span>GOD SYSTEMS</span><span>${cur+1}/${sys.length}</span></div>
    <div class="s-body">
      ${pg.map((s,i)=>{const idx=st+i,inP=pip.includes(s.name);return `<div class="row ${cur===idx?'sel':''}">${cursor(idx,cur===idx)}<span style="color:${inP?'var(--green)':'var(--bright)'}">${s.name}</span><span class="sub">${(s.description||'').substring(0,18)}</span></div>`;}).join('')}
    </div>
    <div class="s-footer">A:VIEW &nbsp; B:BACK &nbsp; &#8593;&#8595;:SCROLL</div>
  </div>`;
}

function rGodDetail(){
  if(!detail) return rLoad();
  const d=detail;
  const desc=(d.description||'—').substring(0,180);
  const dom=(d.domain||'—').substring(0,80);
  const ins=(d.inputs||[]).join(', ').substring(0,60)||'—';
  const outs=(d.outputs||[]).join(', ').substring(0,60)||'—';
  const forb=(d.forbidden||[]).join(', ')||'none';
  return `<div class="panel">
    <div class="s-header"><span style="color:var(--amber)">${d.name}</span><span style="color:var(--dim)">SYS</span></div>
    <div class="s-body scroll">
      <div class="dl">DOMAIN</div><div class="dv">${dom}</div>
      <div class="dl">DESCRIPTION</div><div class="dv">${desc}</div>
      <div class="dl">INPUTS</div><div class="dv">${ins}</div>
      <div class="dl">OUTPUTS</div><div class="dv">${outs}</div>
      <div class="dl">FORBIDDEN EDGES</div><div class="dv" style="color:var(--red)">${forb}</div>
    </div>
    <div class="s-footer">B:BACK &nbsp; &#8593;&#8595;:SCROLL</div>
  </div>`;
}

function rGold(){
  if(!gdata) return rLoad();
  const rules=gdata.gold_law, st=Math.floor(cur/PG)*PG, pg=rules.slice(st,st+PG);
  return `<div class="panel">
    <div class="s-header"><span>GOLD LAW</span><span>${rules.length} RULES</span></div>
    <div class="s-body">
      ${pg.map((r,i)=>{const idx=st+i;return `<div class="rule ${cur===idx?'sel':''}"><span style="color:var(--amber);margin-right:3px">${cur===idx?'&#9658;':String(idx+1).padStart(2,'0')}</span>${r.substring(0,52)}</div>`;}).join('')}
    </div>
    <div class="s-footer">B:BACK &nbsp; &#8593;&#8595;:SCROLL</div>
  </div>`;
}

function rGrid(){
  if(!gdata) return rLoad();
  const ds=gdata.districts, st=Math.floor(cur/PG)*PG, pg=ds.slice(st,st+PG);
  return `<div class="panel">
    <div class="s-header"><span>THE GRID</span><span>${cur+1}/${ds.length}</span></div>
    <div class="s-body">
      ${pg.map((d,i)=>{const idx=st+i;return `<div class="row ${cur===idx?'sel':''}">${cursor(idx,cur===idx)}<span style="color:var(--blue)">${d.district}</span><span class="sub">[${(d.region||'').split(' ').pop()}]</span></div>`;}).join('')}
    </div>
    <div class="s-footer">A:VIEW &nbsp; B:BACK &nbsp; &#8593;&#8595;:SCROLL</div>
  </div>`;
}

function rGridDetail(){
  if(!detail) return rLoad();
  const d=detail, kw=(d.keywords||[]).join(', ')||'—';
  const warns=(d.warnings||[]).slice(0,2);
  return `<div class="panel">
    <div class="s-header"><span style="color:var(--blue)">${d.district}</span><span style="color:var(--dim)">NODE</span></div>
    <div class="s-body scroll">
      <div class="dl">REGION</div><div class="dv">${d.region}</div>
      <div class="dl">KEYWORDS</div><div class="dv">${kw}</div>
      ${warns.length?`<div class="dl">WARNINGS</div>${warns.map(w=>`<div class="dv" style="color:var(--amber)">${w.substring(0,80)}</div>`).join('')}`:''}
      <div style="margin-top:10px"><a href="/grid/node/${d.slug}" style="color:var(--blue);font-size:6px;text-decoration:none">&#9654; OPEN IN GRID</a></div>
    </div>
    <div class="s-footer">B:BACK &nbsp; A:OPEN</div>
  </div>`;
}

function rLive(){
  const ents=lives.slice(-PG);
  return `<div class="panel">
    <div class="s-header"><span>LIVE FEED</span><span style="color:var(--green)">&#9632; LIVE</span></div>
    <div class="s-body">
      ${ents.length?ents.map(e=>`<div class="live-e"><span class="lt">${(e.time||'').substring(0,5)}</span><span class="la">${(e.action||'').substring(0,28)}</span><span class="ls-${e.status||'done'}">${(e.status||'OK').toUpperCase().substring(0,4)}</span></div>`).join(''):'<div style="color:var(--dim);font-size:6px;padding:20px;text-align:center">NO ACTIVITY YET</div>'}
    </div>
    <div class="s-footer">B:BACK &nbsp; AUTO-REFRESH 3S</div>
  </div>`;
}

function rLoad(){ return `<div class="panel"><div class="s-body" style="display:flex;align-items:center;justify-content:center;height:100%"><span style="color:var(--dim);font-size:6px">LOADING...</span></div></div>`; }

// ── navigation
function nav(d){
  let mx=0;
  if(S==='menu') mx=MENU.length;
  if(S==='god'&&gdata)  mx=gdata.god_systems.length;
  if(S==='gold'&&gdata) mx=gdata.gold_law.length;
  if(S==='grid'&&gdata) mx=gdata.districts.length;
  if(S==='alerts') return;
  if(S==='github'){ ghNav(d); return; }
  if(S==='ghIssue') return;
  if(mx>0){ cur=((cur+d)%mx+mx)%mx; draw(); beep(d>0?440:400,40); }
}

function ok(){
  beep(880,60);
  if(S==='boot'){ S='menu'; cur=0; draw(); return; }
  if(S==='menu'){ S=MENU[cur].state; cur=0; draw(); return; }
  if(S==='god'&&gdata){ detail=gdata.god_systems[cur]; S='godD'; draw(); return; }
  if(S==='grid'&&gdata){ detail=gdata.districts[cur]; S='gridD'; draw(); return; }
  if(S==='gridD'&&detail){ window.open('/grid/node/'+detail.slug,'_blank'); return; }
  if(S==='alerts'){ subscribePush(); return; }
  if(S==='github'){ ghOk(); return; }
  if(S==='ghIssue'){ ghSubmitIssue(); return; }
}

function back(){
  beep(220,40);
  if(S==='godD')  { S='god';  draw(); return; }
  if(S==='gridD') { S='grid'; draw(); return; }
  if(['god','gold','grid','live','alerts','github'].includes(S)){ S='menu'; cur=0; draw(); return; }
  if(S==='ghIssue'){ S='github'; ghIssueTitle=''; ghIssueBody=''; draw(); return; }
}

function start(){
  beep(660,80);
  S='menu'; cur=0; draw();
}

// ── 8-bit beep
let actx=null;
function beep(f,ms){
  try{
    if(!actx) actx=new(window.AudioContext||window.webkitAudioContext)();
    const o=actx.createOscillator(), g=actx.createGain();
    o.connect(g); g.connect(actx.destination);
    o.type='square'; o.frequency.value=f;
    g.gain.setValueAtTime(0.07,actx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001,actx.currentTime+ms/1000);
    o.start(); o.stop(actx.currentTime+ms/1000);
  }catch(e){}
}

// ── keyboard
document.addEventListener('keydown',e=>{
  const k=e.key;
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(k)||k==='Enter') e.preventDefault();
  if(k==='ArrowUp')   nav(-1);
  if(k==='ArrowDown') nav(1);
  if(k==='ArrowRight'||k==='z'||k==='Z'||k==='Enter') ok();
  if(k==='ArrowLeft' ||k==='x'||k==='X'||k==='Escape') back();
  if(k===' ') start();
});

// ── push alerts
let pushSub=null, pushAvail=false;

function urlB64ToUint8Array(b64){
  const pad='='.repeat((4-b64.length%4)%4);
  const b=(b64+pad).replace(/-/g,'+').replace(/_/g,'/');
  const raw=atob(b); const out=new Uint8Array(raw.length);
  for(let i=0;i<raw.length;i++) out[i]=raw.charCodeAt(i);
  return out;
}

async function checkPushSupport(){
  if(!('serviceWorker' in navigator)||!('PushManager' in window)) return;
  try{
    const r=await fetch('/push/vapid-public'); const d=await r.json();
    if(!d.enabled) return;
    pushAvail=true;
    const reg=await navigator.serviceWorker.ready;
    pushSub=await reg.pushManager.getSubscription();
    if(S==='alerts') draw();
  }catch(e){}
}

async function subscribePush(){
  if(!pushAvail){ beep(220,60); return; }
  if(pushSub){ beep(880,60); draw(); return; }
  try{
    const r=await fetch('/push/vapid-public'); const {publicKey}=await r.json();
    const reg=await navigator.serviceWorker.ready;
    const sub=await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:urlB64ToUint8Array(publicKey)});
    await fetch('/push/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(sub)});
    pushSub=sub; beep(880,100); draw();
  }catch(e){ beep(220,80); }
}

function rAlerts(){
  const perm=('Notification' in window)?Notification.permission:'unsupported';
  const active=!!pushSub;
  const col=active?'var(--green)':'var(--red)';
  const subs=active?'ACTIVE':'NONE';
  const hint=!pushAvail?'NOT AVAILABLE':active?'ONLINE':'A:SUBSCRIBE';
  return `<div class="panel">
    <div class="s-header"><span>ALERTS</span><span style="color:${col}">${subs}</span></div>
    <div class="s-body" style="padding-top:10px">
      <div class="dl">PERMISSION</div>
      <div class="dv">${perm.toUpperCase()}</div>
      <div class="dl">PUSH SUBSCRIPTION</div>
      <div class="dv" style="color:${col}">${active?'ACTIVE — delivery online':'NONE — press A to enable'}</div>
      <div class="dl">SOURCES</div>
      <div class="dv">PROMETHEUS decisions<br>Heartbeat events<br>Failures &amp; violations</div>
    </div>
    <div class="s-footer">${hint} &nbsp; B:BACK</div>
  </div>`;
}

// ── GitHub state & renderers ──────────────────────────────────────────────
let ghData=null, ghTab=0, ghLoading=false, ghError='';
let ghIssueTitle='', ghIssueBody='', ghIssueField='title', ghSubmitting=false, ghResult='';

const GH_TABS=['COMMITS','PRS','ISSUES','NEW ISSUE'];

async function loadGithub(){
  ghLoading=true; ghError=''; if(S==='github') draw();
  try{
    const r=await fetch('/github/summary');
    if(!r.ok){ ghError='HTTP '+r.status; ghLoading=false; if(S==='github') draw(); return; }
    ghData=await r.json();
    if(ghData.error){ ghError=ghData.error; ghData=null; }
  }catch(e){ ghError=e.message; }
  ghLoading=false;
  if(S==='github') draw();
}

function ghNav(d){
  ghTab=((ghTab+d)%GH_TABS.length+GH_TABS.length)%GH_TABS.length;
  if(ghTab===3){ S='ghIssue'; ghIssueTitle=''; ghIssueBody=''; ghIssueField='title'; ghResult=''; }
  draw(); beep(d>0?440:400,40);
}

function ghOk(){
  if(ghTab===3){ S='ghIssue'; ghIssueTitle=''; ghIssueBody=''; ghIssueField='title'; ghResult=''; draw(); return; }
  loadGithub();
}

function rGithub(){
  if(ghLoading) return `<div class="boot-panel"><div class="boot-logo">GITHUB</div><div style="color:var(--amber);margin-top:8px">LOADING...</div></div>`;
  let h=`<div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--dim);padding-bottom:4px;margin-bottom:6px">`;
  GH_TABS.forEach((t,i)=>{
    h+=`<span style="color:${i===ghTab?'var(--amber)':'var(--dim)'};font-size:9px;cursor:pointer" onclick="ghTab=${i};if(ghTab===3){S='ghIssue';ghIssueTitle='';ghIssueBody='';ghIssueField='title';ghResult='';} draw()">${t}</span>`;
  });
  h+=`</div>`;
  if(ghError) return h+`<div style="color:var(--red)">${ghError}</div><div style="color:var(--dim);font-size:9px;margin-top:8px">CONFIGURE GITHUB_TOKEN + GITHUB_REPO</div>`;
  if(!ghData) return h+`<div style="color:var(--dim)">PRESS A TO LOAD</div>`;
  if(ghTab===0){
    h+=`<div style="font-size:9px;color:var(--green);margin-bottom:4px">RECENT COMMITS</div>`;
    (ghData.commits||[]).forEach(c=>{
      if(c.error){ h+=`<div style="color:var(--red);font-size:9px">${c.error}</div>`; return; }
      h+=`<div style="margin-bottom:5px"><span style="color:var(--amber);font-size:9px">${c.sha}</span> <span style="font-size:9px">${c.message}</span><br><span style="color:var(--dim);font-size:8px">${c.author} · ${c.date}</span></div>`;
    });
  } else if(ghTab===1){
    h+=`<div style="font-size:9px;color:var(--green);margin-bottom:4px">OPEN PULL REQUESTS</div>`;
    const prs=ghData.prs||[];
    if(!prs.length) h+=`<div style="color:var(--dim);font-size:9px">NO OPEN PRS</div>`;
    prs.forEach(p=>{
      if(p.error){ h+=`<div style="color:var(--red);font-size:9px">${p.error}</div>`; return; }
      h+=`<div style="margin-bottom:5px"><span style="color:var(--amber);font-size:9px">#${p.number}</span> <span style="font-size:9px">${p.title}</span><br><span style="color:var(--dim);font-size:8px">${p.user}</span></div>`;
    });
  } else if(ghTab===2){
    h+=`<div style="font-size:9px;color:var(--green);margin-bottom:4px">OPEN ISSUES</div>`;
    const issues=ghData.issues||[];
    if(!issues.length) h+=`<div style="color:var(--dim);font-size:9px">NO OPEN ISSUES</div>`;
    issues.forEach(i=>{
      if(i.error){ h+=`<div style="color:var(--red);font-size:9px">${i.error}</div>`; return; }
      h+=`<div style="margin-bottom:5px"><span style="color:var(--amber);font-size:9px">#${i.number}</span> <span style="font-size:9px">${i.title}</span><br><span style="color:var(--dim);font-size:8px">${i.user}</span></div>`;
    });
  }
  h+=`<div style="color:var(--dim);font-size:8px;margin-top:6px">A=REFRESH  ◄►=TAB  B=BACK</div>`;
  return h;
}

function rGhIssue(){
  let h=`<div style="color:var(--amber);font-size:10px;border-bottom:1px solid var(--dim);padding-bottom:4px;margin-bottom:6px">NEW GITHUB ISSUE</div>`;
  if(ghResult) return h+`<div style="color:var(--green);font-size:9px">${ghResult}</div><div style="color:var(--dim);font-size:8px;margin-top:8px">B=BACK</div>`;
  if(ghSubmitting) return h+`<div style="color:var(--amber)">SUBMITTING...</div>`;
  h+=`<div style="font-size:9px;color:${ghIssueField==='title'?'var(--amber)':'var(--dim)'};margin-bottom:2px">TITLE ${ghIssueField==='title'?'▲':''}</div>`;
  h+=`<div style="font-size:9px;min-height:16px;border:1px solid ${ghIssueField==='title'?'var(--amber)':'var(--dim)'};padding:2px;margin-bottom:6px">${ghIssueTitle||'<span style="color:var(--dim)">tap to type</span>'}</div>`;
  h+=`<div style="font-size:9px;color:${ghIssueField==='body'?'var(--amber)':'var(--dim)'};margin-bottom:2px">BODY ${ghIssueField==='body'?'▲':''}</div>`;
  h+=`<div style="font-size:9px;min-height:24px;border:1px solid ${ghIssueField==='body'?'var(--amber)':'var(--dim)'};padding:2px">${ghIssueBody||'<span style="color:var(--dim)">optional</span>'}</div>`;
  h+=`<div style="color:var(--dim);font-size:8px;margin-top:8px">TAP FIELD TO EDIT · A=SUBMIT · B=BACK</div>`;
  h+=`<input id="gh-title-input" style="position:absolute;opacity:0;pointer-events:none" type="text" value="${ghIssueTitle.replace(/"/g,'&quot;')}" oninput="ghIssueTitle=this.value;draw()" onblur="draw()">`;
  h+=`<input id="gh-body-input" style="position:absolute;opacity:0;pointer-events:none" type="text" value="${ghIssueBody.replace(/"/g,'&quot;')}" oninput="ghIssueBody=this.value;draw()" onblur="draw()">`;
  h+=`<div onclick="ghIssueField='title';document.getElementById('gh-title-input').focus()" style="position:absolute;top:60px;left:8px;right:8px;height:22px;cursor:pointer"></div>`;
  h+=`<div onclick="ghIssueField='body';document.getElementById('gh-body-input').focus()" style="position:absolute;top:108px;left:8px;right:8px;height:28px;cursor:pointer"></div>`;
  return h;
}

async function ghSubmitIssue(){
  if(!ghIssueTitle.trim()){ beep(200,100); return; }
  ghSubmitting=true; draw();
  try{
    const r=await fetch('/github/create-issue',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:ghIssueTitle,body:ghIssueBody})});
    const d=await r.json();
    if(d.ok) ghResult=`CREATED #${d.number}\\n${d.url}`;
    else ghResult='ERROR: '+d.error;
  }catch(e){ ghResult='ERROR: '+e.message; }
  ghSubmitting=false; draw(); beep(880,120);
}

// ── neural mesh SSE ───────────────────────────────────────────────────────
function sseDot(on){
  const d=document.getElementById('sse-dot');
  if(d){ d.style.color=on?'#00ff88':'#333'; d.title=on?'NEURAL MESH LIVE':'DISCONNECTED'; }
}

function connectSSE(){
  if(_sse){ _sse.close(); _sse=null; }
  _sse=new EventSource('/events');
  _sse.onopen=()=>{ sseConnected=true; sseDot(true); };
  _sse.onerror=()=>{
    sseConnected=false; sseDot(false);
    setTimeout(connectSSE,5000);
  };
  _sse.addEventListener('live_log', e=>{
    try{
      const d=JSON.parse(e.data);
      lives.unshift(d);
      if(lives.length>100) lives=lives.slice(0,100);
      if(S==='live') draw();
    }catch(_){}
  });
  _sse.addEventListener('prometheus', e=>{
    try{
      const d=JSON.parse(e.data);
      lives.unshift({action:'PROMETHEUS: '+d.decision, status:'done', ts:d.ts, system:d.system});
      if(lives.length>100) lives=lives.slice(0,100);
      if(S==='live') draw();
    }catch(_){}
  });
  _sse.addEventListener('github', e=>{
    loadGithub();
  });
}

// ── boot sequence
const BOOT_LINES=[
  'INITIALIZING...',
  'LOADING GOD SYSTEMS...',
  'CHECKING GOLD LAW...',
  'MOUNTING THE GRID...',
  'ERIS ENTROPY CHECK...',
  'READY.',
];

function runBoot(){
  const el=document.getElementById('screen-inner');
  el.innerHTML=`<div class="boot-panel">
    <div class="boot-logo">JARVIS</div>
    <div class="boot-sub">GOD SYSTEM INTERFACE v2.5</div>
    <div class="boot-lines" id="blines"></div>
    <div class="boot-hint">PRESS START</div>
  </div>`;
  let i=0;
  function tick(){
    if(i>=BOOT_LINES.length){ setTimeout(()=>{S='menu';cur=0;draw();},700); return; }
    const ln=document.createElement('div');
    ln.className='boot-line';
    ln.textContent=BOOT_LINES[i++];
    document.getElementById('blines').appendChild(ln);
    setTimeout(tick,220);
  }
  setTimeout(tick,350);
}

// ── data
async function loadData(){
  try{ const r=await fetch('/gameboy/data'); if(r.ok){ gdata=await r.json(); if(S!=='boot') draw(); } }catch(e){}
}
async function loadLive(){
  try{ const r=await fetch('/live_log.json'); if(r.ok){ lives=await r.json(); if(S==='live') draw(); } }catch(e){}
}

loadData();
loadLive();
loadGithub();
connectSSE();
setInterval(loadGithub,60000);
runBoot();
if('serviceWorker' in navigator){
  navigator.serviceWorker.register('/gameboy/sw.js').then(()=>checkPushSupport()).catch(()=>{});
}
</script>
</body>
</html>"""

_INTAKE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>JARVIS INTAKE</title>
<meta name="theme-color" content="#020408">
<style>
:root {
  --amber:#f5a623; --green:#00ff88; --dim:#1e3a52; --text:#4a7a99;
  --bright:#a0c8e0; --bg:#020408; --surface:#080f18; --border:#0f2035;
}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{background:var(--bg);color:var(--bright);font-family:system-ui,-apple-system,sans-serif;min-height:100vh;}
.shell{max-width:480px;margin:0 auto;padding:16px;}
header{border-bottom:1px solid var(--border);padding-bottom:12px;margin-bottom:20px;display:flex;align-items:center;gap:10px;}
.logo{font-size:11px;letter-spacing:4px;color:var(--amber);font-family:monospace;font-weight:bold;}
.sub{font-size:10px;color:var(--text);letter-spacing:2px;}
label{display:block;font-size:10px;letter-spacing:2px;color:var(--text);margin-bottom:5px;margin-top:14px;}
input,select,textarea{
  width:100%;background:var(--surface);border:1px solid var(--border);
  color:var(--bright);font-size:14px;padding:10px 12px;border-radius:4px;
  font-family:inherit;outline:none;-webkit-appearance:none;
}
input:focus,select:focus,textarea:focus{border-color:var(--amber);}
select{background-image:none;}
textarea{resize:vertical;min-height:80px;line-height:1.5;}
.submit{
  display:block;width:100%;margin-top:24px;padding:14px;
  background:var(--amber);color:#020408;font-size:12px;letter-spacing:3px;
  font-weight:bold;border:none;border-radius:4px;cursor:pointer;font-family:monospace;
}
.submit:active{opacity:.8;}
.submit:disabled{opacity:.4;cursor:not-allowed;}
.toast{
  position:fixed;bottom:24px;left:50%;transform:translateX(-50%);
  background:var(--green);color:#020408;padding:12px 24px;border-radius:6px;
  font-size:11px;letter-spacing:2px;font-family:monospace;font-weight:bold;
  opacity:0;transition:opacity .3s;pointer-events:none;
}
.toast.show{opacity:1;}
.err{color:#ff3355;font-size:10px;margin-top:4px;letter-spacing:1px;}
.aegis{font-size:9px;color:var(--dim);letter-spacing:1px;text-align:center;margin-top:16px;}
</style>
</head>
<body>
<div class="shell">
  <header>
    <div>
      <div class="logo">JARVIS</div>
      <div class="sub">INTAKE // MOBILE</div>
    </div>
  </header>

  <form id="form">
    <label>TITLE</label>
    <input type="text" id="title" placeholder="short descriptive title" required>

    <label>REQUESTED ACTION</label>
    <select id="action">
      <option value="review">review</option>
      <option value="implement">implement</option>
      <option value="remember">remember</option>
      <option value="archive">archive</option>
    </select>

    <label>SUMMARY</label>
    <textarea id="summary" placeholder="what is this about?" required></textarea>

    <label>DETAILS</label>
    <textarea id="details" placeholder="full context, constraints, relevant links..." style="min-height:120px;"></textarea>

    <label>SUGGESTED NEXT STEP</label>
    <textarea id="next" placeholder="what should JARVIS or Codex do with this?"></textarea>

    <button type="submit" class="submit" id="btn">SUBMIT TO INTAKE</button>
    <div class="err" id="err"></div>
    <div class="aegis">AEGIS — routed to intake/claude/ — governed workflow applies</div>
  </form>
</div>
<div class="toast" id="toast"></div>

<script>
document.getElementById('form').addEventListener('submit', async function(e){
  e.preventDefault();
  const btn=document.getElementById('btn');
  const err=document.getElementById('err');
  err.textContent='';
  btn.disabled=true; btn.textContent='SUBMITTING...';
  const payload={
    title:    document.getElementById('title').value.trim(),
    action:   document.getElementById('action').value,
    summary:  document.getElementById('summary').value.trim(),
    details:  document.getElementById('details').value.trim(),
    next:     document.getElementById('next').value.trim(),
  };
  try{
    const r=await fetch('/intake',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const j=await r.json();
    if(r.ok){
      document.getElementById('form').reset();
      const t=document.getElementById('toast');
      t.textContent='FILED: '+j.file;
      t.classList.add('show');
      setTimeout(()=>t.classList.remove('show'),3500);
    } else {
      err.textContent=j.detail||'submit failed';
    }
  }catch(ex){ err.textContent='network error'; }
  btn.disabled=false; btn.textContent='SUBMIT TO INTAKE';
});
</script>
</body>
</html>"""
