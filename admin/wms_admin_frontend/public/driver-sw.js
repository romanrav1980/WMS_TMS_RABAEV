/** Driver shell cache. Only the server may confirm an operation. */
const CACHE_NAME = "tms-driver-v2";
self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.add("/?page=driver")).catch(() => {}));
  self.skipWaiting();
});
self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(key => key.startsWith("tms-driver-") && key !== CACHE_NAME).map(key => caches.delete(key))
  )).then(() => self.clients.claim()));
});
// Legacy IndexedDB pending_ops is retained for investigation; never replay without
// authenticated, explicit confirmation. New intents are scoped by user and driver.
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== self.location.origin ||
      url.pathname.startsWith("/api/") || event.request.headers.has("Authorization")) return;
  const shell = event.request.mode === "navigate" && url.searchParams.get("page") === "driver";
  const asset = url.pathname.startsWith("/assets/");
  if (!shell && !asset) return;
  event.respondWith(fetch(event.request).then(response => {
    if (response.ok) {
      const copy = response.clone();
      event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy)));
    }
    return response;
  }).catch(async () => (await caches.match(event.request)) ||
    new Response("Нет сети. Подключитесь для загрузки рабочего места.", {status:503,headers:{"Content-Type":"text/plain; charset=utf-8"}})));
});
