self.addEventListener('push', function(e) {
    const d = e.data ? e.data.json() : {title:'JARVIS', body:'Event'};
    e.waitUntil(self.registration.showNotification(d.title || 'JARVIS', {
        body:    d.body || '',
        icon:    '/jarvis/icon.svg',
        badge:   '/jarvis/icon.svg',
        tag:     d.tag || 'jarvis',
        vibrate: [100, 50, 100],
        data:    {url: '/jarvis/'}
    }));
});

self.addEventListener('notificationclick', function(e) {
    e.notification.close();
    e.waitUntil(clients.openWindow(
        (e.notification.data && e.notification.data.url) || '/jarvis/'
    ));
});
