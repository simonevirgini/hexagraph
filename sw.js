/* Service worker di Hexagraph — strategia RETE-PRIMA, cache come riserva:
   con la rete l'app è SEMPRE l'ultima pubblicata (nessun rischio di versioni vecchie
   appiccicate: ogni risposta buona rinfresca la cache); senza rete si apre l'ultima
   versione vista. Cambiando questo file (basta la versione qui sotto) il browser
   installa il nuovo worker al prossimo avvio. */
const CACHE = 'hexagraph-v2';

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['/', 'tiles.js?v=3']).catch(() => {})));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;
  /* le navigazioni rivalidano SEMPRE col server (no-cache → ETag/304): senza, la cache HTTP
     del browser (max-age della CDN) può tenere l'app vecchia per ore anche col worker rete-prima */
  const req = e.request.mode === 'navigate' ? new Request(e.request, { cache: 'no-cache' }) : e.request;
  e.respondWith(
    fetch(req).then(r => {
      if (r && r.ok) { const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); }
      return r;
    }).catch(() =>
      caches.match(e.request).then(m => m || (e.request.mode === 'navigate' ? caches.match('/') : undefined))
    )
  );
});
