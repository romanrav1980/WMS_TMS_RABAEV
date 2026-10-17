const ASSEMBLY_CACHE = "retailcase-assembly-shell-v1";
const ASSEMBLY_SHELL = "/assembly/";
self.addEventListener("install", event => {
  event.waitUntil((async () => {
    const cache = await caches.open(ASSEMBLY_CACHE);
    const page = await fetch(ASSEMBLY_SHELL, { cache: "reload", credentials: "omit" });
    if (!page.ok) throw new Error("Assembly shell unavailable");
    await cache.put(ASSEMBLY_SHELL, page.clone());
    const html = await page.text();
    const assets = [...html.matchAll(/(?:src|href)=["'](\/assets\/[^"']+)["']/g)].map(match => match[1]);
    await cache.addAll([...new Set(["/assembly/icon.svg", "/assembly/manifest.webmanifest", ...assets])]);
    await self.skipWaiting();
  })());
});
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key.startsWith("retailcase-assembly-shell-") && key !== ASSEMBLY_CACHE).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});
self.addEventListener("fetch", event => {
  const request = event.request, url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin || request.headers.has("authorization")) return;
  if (url.pathname.startsWith("/api/")) return;
  if (request.mode === "navigate" && url.pathname.startsWith("/assembly/")) {
    event.respondWith((async () => {
      const cache = await caches.open(ASSEMBLY_CACHE);
      try {
        const response = await fetch(request);
        if (response.ok) await cache.put(ASSEMBLY_SHELL, response.clone());
        return response;
      } catch { return cache.match(ASSEMBLY_SHELL); }
    })());
    return;
  }
  if (!(url.pathname.startsWith("/assets/") || url.pathname.startsWith("/assembly/"))) return;
  event.respondWith((async () => {
    const cached = await caches.match(request);
    if (cached) return cached;
    const response = await fetch(request);
    if (response.ok && response.type === "basic") {
      const cache = await caches.open(ASSEMBLY_CACHE);
      await cache.put(request, response.clone());
    }
    return response;
  })());
});
