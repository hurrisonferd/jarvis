const CACHE = 'jarvis-static-v2';

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
  // COI headers on navigation responses — enables SharedArrayBuffer for mGBA WASM
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request).then(resp => {
        const headers = new Headers(resp.headers);
        headers.set('Cross-Origin-Opener-Policy', 'same-origin');
        headers.set('Cross-Origin-Embedder-Policy', 'credentialless');
        return new Response(resp.body, {status: resp.status, statusText: resp.statusText, headers});
      }).catch(() => caches.match(e.request))
    );
    return;
  }
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
