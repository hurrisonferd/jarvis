const ITEMS=[
  ['SHIP MAP','shipmap','NAVIGATION'],
  ['OMNI COMMAND DECK','omni','ONLINE'],
  ['BRIDGE COMMS','bridge','READ-ONLY'],
  ['SHIP INTELLIGENCE','intelligence','JARVIS'],
  ['MNEMOS VAULT','mnemos','MEMORY'],
  ['SENSOR ARRAY','telemetry','LIVE FIELD'],
  ['ENGINE ROOM','godfield','GOD FIELD'],
  ['HANGAR','fleet','FLEET'],
  ['HOLODECK','legacy','PARITY PENDING']
];
export const menuScreen={
  render(router){return `<div class="header"><span>WORLD-002</span><span>BRIDGE</span></div>${ITEMS.map((item,index)=>`<div class="row ${index===router.context.cursor?'selected':''}">${index===router.context.cursor?'▶':' '} ${item[0]} <span class="sub">${item[2]}</span></div>`).join('')}<div class="footer">A:ENTER · ↑↓:MOVE · SELECT:REFRESH · START:BRIDGE</div>`;},
  command(cmd,router){if(cmd==='up')router.context.cursor=(router.context.cursor+ITEMS.length-1)%ITEMS.length;if(cmd==='down')router.context.cursor=(router.context.cursor+1)%ITEMS.length;if(cmd==='confirm')router.go(ITEMS[router.context.cursor][1]);if(cmd==='select')router.store?.load?.().then(()=>router.render()).catch(()=>router.render());if(cmd==='start')router.go('menu');}
};
export const legacyScreen={render(){return `<div class="header"><span>HOLODECK</span><span>WORLD-001 LINK</span></div><div class="panel">Production v2.5 remains untouched while screen, PWA, data, event, emulator, and governance parity are extracted into modules.</div><div class="panel identity">THE ORIGINAL SHIP'S SOUL IS PRESERVED.</div><div class="footer">B:BACK · START:BRIDGE</div>`;},command(cmd,router){if(cmd==='back'||cmd==='start')router.go('menu');}};