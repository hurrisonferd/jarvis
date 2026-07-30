export class Router {
  constructor({root,bus}){this.root=root;this.bus=bus;this.routes=new Map();this.state='menu';this.context={cursor:0};}
  register(name,screen){this.routes.set(name,screen);}
  go(name,patch={}){if(!this.routes.has(name))throw new Error(`Unknown screen: ${name}`);this.state=name;this.context={...this.context,...patch,cursor:0};this.bus.emit('screen_change',{screen:name});this.render();}
  command(command){const screen=this.routes.get(this.state);screen?.command?.(command,this);this.render();}
  render(){const screen=this.routes.get(this.state);this.root.innerHTML=screen?.render?.(this)||'<div class="bad">SCREEN OFFLINE</div>';}
}
