const ITEMS=[
  ['OMNI ROOM','omni'],
  ['BRIDGE COMMS','stub'],
  ['SHIP INTELLIGENCE','stub'],
  ['MNEMOS ARCHIVE','stub'],
  ['ENGINE ROOM','stub'],
  ['FLEET','stub']
];
export const menuScreen={
  render(router){return `<div class="header"><span>WORLD-001</span><span>BRIDGE</span></div>${ITEMS.map((x,i)=>`<div class="row ${i===router.context.cursor?'selected':''}">${i===router.context.cursor?'▶':' '} ${x[0]} <span class="sub">${x[1]==='stub'?'LEGACY LINK':'ONLINE'}</span></div>`).join('')}<div class="footer">A:ENTER · ↑↓:MOVE · START:BRIDGE</div>`;},
  command(cmd,router){if(cmd==='up')router.context.cursor=(router.context.cursor+ITEMS.length-1)%ITEMS.length;if(cmd==='down')router.context.cursor=(router.context.cursor+1)%ITEMS.length;if(cmd==='confirm'){const [,route]=ITEMS[router.context.cursor];router.go(route==='stub'?'legacy':route);}}
};
export const legacyScreen={render(){return `<div class="header"><span>LEGACY SYSTEM</span><span>PRESERVED</span></div><div class="panel">This module remains aboard the production v2.5 vessel while parity extraction proceeds.</div><div class="footer">B:BACK · START:BRIDGE</div>`;},command(cmd,router){if(cmd==='back'||cmd==='start')router.go('menu');}};
