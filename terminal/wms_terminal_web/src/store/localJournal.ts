import type { JournalEntry } from "../types";

const DB_NAME = "wms-terminal";
const DB_VERSION = 1;
const STORE_NAME = "journal";

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: "id" });
        store.createIndex("status", "status", { unique: false });
        store.createIndex("resourceKey", "resourceKey", { unique: false });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function saveJournalEntry(entry: JournalEntry): Promise<void> {
  const db = await openDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    tx.objectStore(STORE_NAME).put(entry);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
  db.close();
}

export async function listJournalEntries(limit = 25): Promise<JournalEntry[]> {
  const db = await openDb();
  const result = await new Promise<JournalEntry[]>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const request = tx.objectStore(STORE_NAME).getAll();
    request.onsuccess = () => resolve(request.result as JournalEntry[]);
    request.onerror = () => reject(request.error);
  });
  db.close();
  return result
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
    .slice(0, limit);
}

export function createJournalEntry(flow: string, resourceKey: string, payload: unknown): JournalEntry {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    flow,
    resourceKey,
    status: "draft",
    payload,
    createdAt: now,
    updatedAt: now
  };
}
