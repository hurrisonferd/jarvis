const CACHE = 'jarvis-static-v1';

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./'])));
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
  let d = { title: 'JARVIS', body: '' };
  try { d = e.data.json(); } catch (_) { d.body = e.data ? e.data.text() : ''; }
  e.waitUntil(
    self.registration.showNotification(d.title || 'JARVIS', {
      body: d.body || '',
      data: { url: d.url || self.location.origin + self.registration.scope },
    })
  );
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(clients.openWindow(e.notification.data?.url || self.registration.scope));
});
