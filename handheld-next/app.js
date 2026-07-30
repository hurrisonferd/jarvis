import {EventBus,aegisGate} from './core/event-bus.js';
import {Router} from './core/router.js';
import {menuScreen,legacyScreen} from './screens/menu.js';
import {createOmniScreen} from './screens/omni-room.js';

const root=document.getElementById('screen-inner');
const led=document.getElementById('field-led');
const bus=new EventBus({gate:aegisGate,sink:e=>console.debug('[BUS]',e)});
const store={room:null,async load(){try{const r=await fetch('./data/observer-snapshot.json',{cache:'no-store'});if(!r.ok)throw new Error(String(r.status));this.room=await r.json();bus.emit('omni_snapshot_loaded',{receipt_hash:this.room.receipt_hash,interventions:(this.room.interventions||[]).length});led.classList.toggle('attention',(this.room.interventions||[]).length>0);router.render();}catch(error){bus.emit('omni_snapshot_failed',{error:String(error)});}}};
const router=new Router({root,bus});
router.register('menu',menuScreen);
router.register('legacy',legacyScreen);
router.register('omni',createOmniScreen({store,bus}));
document.querySelectorAll('[data-command]').forEach(button=>button.addEventListener('click',()=>router.command(button.dataset.command)));
window.addEventListener('keydown',event=>{const map={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right',Enter:'confirm',Escape:'back'};if(map[event.key])router.command(map[event.key]);});
bus.on('omni_snapshot_loaded',({data})=>console.info('OMNI observer snapshot ready',data));
store.load();
router.go('menu');
