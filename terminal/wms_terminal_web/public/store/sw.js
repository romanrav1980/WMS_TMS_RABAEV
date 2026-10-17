const STORE_CACHE = "retailcase-store-shell-v3";
const STORE_SHELL = "/store/";
self.addEventListener("install", event => {
  event.waitUntil((async () => {
    const cache = await caches.open(STORE_CACHE);
    const page = await fetch(STORE_SHELL, { cache: "reload", credentials: "omit" });
    if (!page.ok) throw new Error("Store shell unavailable");
    await cache.put(STORE_SHELL, page.clone());
    const html = await page.text();
    const assets = [...html.matchAll(/(?:src|href)=["'](\/assets\/[^"']+)["']/g)].map(match => match[1]);
    await cache.addAll([...new Set(["/store/icon.svg", "/store/manifest.webmanifest", ...assets])]);
    await self.skipWaiting();
  })());
});
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key.startsWith("retailcase-store-shell-") && key !== STORE_CACHE).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});
self.addEventListener("fetch", event => {
  const request = event.request, url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin || request.headers.has("authorization")) return;
  if (url.pathname.startsWith("/api/")) return;
  if (request.mode === "navigate" && url.pathname.startsWith("/store/")) {
    event.respondWith((async () => {
      const cache = await caches.open(STORE_CACHE);
      try {
        const response = await fetch(request);
        if (response.ok) await cache.put(STORE_SHELL, response.clone());
        return response;
      } catch { return cache.match(STORE_SHELL); }
    })());
    return;
  }
  if (!(url.pathname.startsWith("/assets/") || url.pathname.startsWith("/store/"))) return;
  event.respondWith((async () => {
    const cached = await caches.match(request);
    if (cached) return cached;
    const response = await fetch(request);
    if (response.ok && response.type === "basic") {
      const cache = await caches.open(STORE_CACHE);
      await cache.put(request, response.clone());
    }
    return response;
  })());
});
