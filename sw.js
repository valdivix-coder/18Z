/* ===================================================================
   ZOMBIES EN EL 18 — service worker

   Existe por DOS motivos y ninguno es la velocidad:
   1. Android no ofrece instalar (WebAPK) sin un service worker que
      atienda `fetch`. Sin el, el icono y el nombre de esta app no
      llegan nunca al lanzador.
   2. Que el juego no muera con la senal a medias en la micro.

   VA A LA RED PRIMERO, SIEMPRE. La cache es solo el paracaidas de
   cuando no hay red. Es la leccion que ya costo cara en otro proyecto:
   sirviendo desde la cache, un telefono se queda con la version vieja
   —arte incluido— sin que nadie se entere, y en una app instalada eso
   no se arregla recargando.
   =================================================================== */
var CACHE = "z18-v1";

self.addEventListener("install", function(e){ self.skipWaiting(); });
self.addEventListener("activate", function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.map(function(k){ return k === CACHE ? null : caches.delete(k); }));
  }).then(function(){ return self.clients.claim(); }));
});

self.addEventListener("fetch", function(e){
  var req = e.request;
  if(req.method !== "GET") return;
  if(new URL(req.url).origin !== self.location.origin) return;   // fuentes de Google: que las gestione el navegador
  e.respondWith(
    fetch(req).then(function(res){
      if(res && res.ok){
        var copia = res.clone();
        caches.open(CACHE).then(function(c){ c.put(req, copia); });
      }
      return res;
    }).catch(function(){
      return caches.match(req).then(function(hit){
        return hit || caches.match("/inicio.html");
      });
    })
  );
});
