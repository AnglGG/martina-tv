// Guarda una copia del menú en la tele. Al abrirlo se muestra la copia al instante y, mientras tanto,
// se descarga la versión nueva para la siguiente vez. Si falla internet, el menú sigue abriendo.
var CACHE = 'martina-tv-1';

self.addEventListener('install', function () { self.skipWaiting(); });

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;   // las apps y sus webs no pasan por aquí
  var key = req.mode === 'navigate' ? url.origin + url.pathname : req.url;
  e.respondWith(caches.open(CACHE).then(function (cache) {
    return cache.match(key).then(function (hit) {
      var fresh = fetch(req).then(function (res) {
        if (res.ok && !res.redirected) cache.put(key, res.clone());
        return res;
      });
      if (!hit) return fresh;
      e.waitUntil(fresh.catch(function () {}));
      return hit;
    });
  }));
});
