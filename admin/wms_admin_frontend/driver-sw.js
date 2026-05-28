/**
 * driver-sw.js — Service Worker для PWA водителя.
 * Sprint 105: кэширование страницы + offline-синхронизация операций.
 */

const CACHE_NAME = "tms-driver-v1";
const OFFLINE_URLS = [
  "/?page=driver",
  "/src/main.tsx",
];

// Установка: кэшируем основные ресурсы
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      cache.addAll(OFFLINE_URLS).catch(() => {})
    )
  );
  self.skipWaiting();
});

// Активация: удаляем старые кэши
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: network-first для API, cache-first для статики
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // API: network-first, при offline сохраняем в IndexedDB
  if (url.pathname.startsWith("/api/driver/ops/") && event.request.method === "POST") {
    event.respondWith(
      fetch(event.request.clone()).catch(async () => {
        // Сохраняем операцию в IndexedDB для Background Sync
        await saveOfflineOp(event.request.clone());
        return new Response(JSON.stringify({ queued: true, offline: true }), {
          headers: { "Content-Type": "application/json" },
        });
      })
    );
    return;
  }

  // Статика: cache-first
  if (url.pathname.startsWith("/assets/") || url.pathname.endsWith(".js") || url.pathname.endsWith(".css")) {
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request))
    );
    return;
  }

  // Default: network-first
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});

// Background Sync: при восстановлении сети отправляем накопленные операции
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-driver-ops") {
    event.waitUntil(syncOfflineOps());
  }
});

async function saveOfflineOp(request) {
  const db = await openDB();
  const tx = db.transaction("pending_ops", "readwrite");
  tx.objectStore("pending_ops").add({
    url: request.url,
    method: request.method,
    timestamp: Date.now(),
  });
}

async function syncOfflineOps() {
  const db = await openDB();
  const tx = db.transaction("pending_ops", "readwrite");
  const store = tx.objectStore("pending_ops");
  const all = await new Promise((res) => {
    const req = store.getAll();
    req.onsuccess = () => res(req.result);
    req.onerror = () => res([]);
  });
  for (const op of all) {
    try {
      await fetch(op.url, { method: op.method });
      store.delete(op.id);
    } catch { /* retry next sync */ }
  }
}

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open("tms-driver", 1);
    req.onupgradeneeded = () => {
      req.result.createObjectStore("pending_ops", { keyPath: "id", autoIncrement: true });
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = reject;
  });
}
