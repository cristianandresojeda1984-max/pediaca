// PediAcá — Service Worker (Network First)
const CACHE_NAME = 'pediaca-v1';
const STATIC_ASSETS = ['/static/img/logo_pediaca.png', '/static/manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(STATIC_ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  // No cachear rutas dinámicas
  if (['/api/','/admin','/mi-local','/mi-cuenta','/login','/registro','/dashboard'].some(p => url.pathname.startsWith(p))) return;

  e.respondWith(
    fetch(e.request).then(response => {
      if (response.ok && url.pathname.startsWith('/static/')) {
        caches.open(CACHE_NAME).then(c => c.put(e.request, response.clone()));
      }
      return response;
    }).catch(() => caches.match(e.request))
  );
});

self.addEventListener('push', function(event) {
  const data = event.data ? event.data.json() : {};
  event.waitUntil(
    self.registration.showNotification(data.titulo || '🛵 PediAcá', {
      body: data.cuerpo || 'Nuevo pedido disponible',
      icon: '/static/img/logo_pediaca.png',
      badge: '/static/img/logo_pediaca.png',
      vibrate: [200, 100, 200],
      tag: 'pediaca-pedido',
      renotify: true,
      data: { url: data.url || '/mi-panel-cadete' },
      actions: [{ action: 'ver', title: '👀 Ver pedido' }, { action: 'cerrar', title: '✕' }]
    })
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  if (event.action === 'cerrar') return;
  const url = event.notification.data?.url || '/mi-panel-cadete';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(ws => {
      for (const w of ws) { if (w.url.includes(self.location.origin)) { w.focus(); w.navigate(url); return; } }
      return clients.openWindow(url);
    })
  );
});
