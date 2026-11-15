// Gerado por _scripts/gerar_redes.py. Service worker mínimo: só existe para o Chrome oferecer
// "Instalar app". Vai sempre à rede e não guarda cache (lição de 2026-09-16: o Pages manda
// max-age=600 e um fetch() comum devolveria a cópia velha do navegador).
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', function (e) {
  if (e.request.mode !== 'navigate') return;
  var u = new URL(e.request.url);
  u.searchParams.set('_sw', Date.now());
  e.respondWith(fetch(u.href, { cache: 'no-store', credentials: 'same-origin' }).catch(function () { return fetch(e.request); }));
});
