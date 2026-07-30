const CACHE='jarvis-vessel-two-v0.2.0';
const SHELL=['./','./index.html','./app.js','./styles/app.css','./manifest.json','./icon.svg','./core/event-bus.js','./core/router.js','./core/observer-store.js','./screens/menu.js','./screens/omni-room.js','./screens/vessel-systems.js','./data/observer-snapshot.json'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  event.respondWith(fetch(event.request).then(response=>{const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(event.request,copy));return response;}).catch(()=>caches.match(event.request).then(hit=>hit||caches.match('./index.html'))));
});