// aitema|Rats Service Worker - Offline-Faehigkeit
const CACHE_NAME = 'aitema-rats-v1';
const STATIC_CACHE = 'aitema-rats-static-v1';
const API_CACHE = 'aitema-rats-api-v1';

const STATIC_ASSETS = [
  '/',
  '/personen',
  '/gremien',
  '/sitzungen',
  '/vorlagen',
  '/suche',
  '/manifest.json',
  '/offline.html',
];

// Installation: Statische Assets cachen
self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(function (cache) {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Aktivierung: Alte Caches loeschen
self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (cacheNames) {
      return Promise.all(
        cacheNames
          .filter(function (name) {
            return (
              name !== STATIC_CACHE &&
              name !== API_CACHE &&
              name !== CACHE_NAME
            );
          })
          .map(function (name) {
            return caches.delete(name);
          })
      );
    })
  );
  self.clients.claim();
});

// Fetch: Strategie je nach Request-Typ
self.addEventListener('fetch', function (event) {
  var request = event.request;
  var url = new URL(request.url);

  // Nur GET-Requests cachen
  if (request.method !== 'GET') return;

  // API Calls: Network-first
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then(function (response) {
          if (response.ok) {
            var responseClone = response.clone();
            caches.open(API_CACHE).then(function (cache) {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(function () {
          return caches.match(request).then(function (cached) {
            return cached || new Response(
              JSON.stringify({ error: 'Offline', data: [] }),
              { headers: { 'Content-Type': 'application/json' } }
            );
          });
        })
    );
    return;
  }

  // Statische Assets: Cache-first
  event.respondWith(
    caches.match(request).then(function (cached) {
      if (cached) return cached;

      return fetch(request)
        .then(function (response) {
          if (response.ok && url.origin === self.location.origin) {
            var responseClone = response.clone();
            caches.open(STATIC_CACHE).then(function (cache) {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(function () {
          // Offline Fallback fuer HTML-Seiten
          if (request.headers.get('Accept') &&
              request.headers.get('Accept').includes('text/html')) {
            return caches.match('/offline.html');
          }
          return new Response('Offline', { status: 503 });
        });
    })
  );
});

// ── E3: Web Push Notification Handler ─────────────────────────────────────

self.addEventListener(push, function (event) {
  var data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: aitema

// -- E3: Web Push Notification Handler --

self.addEventListener('push', function (event) {
  var data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: 'aitema|RIS', body: event.data.text() };
    }
  }

  var title = data.title || 'aitema|RIS';
  var options = {
    body: data.body || 'Neue Benachrichtigung im Ratsinformationssystem',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-192x192.png',
    tag: data.tag || 'aitema-ris',
    data: { url: data.url || '/' },
    requireInteraction: false,
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function (event) {
  event.notification.close();
  var targetUrl = (event.notification.data && event.notification.data.url) || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (clientList) {
      for (var i = 0; i < clientList.length; i++) {
        var client = clientList[i];
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.navigate(targetUrl);
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
