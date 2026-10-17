// Reusable durable-intent journal for the 3 saved command kinds (open_session/open_step/finish).
// Exact payload is saved BEFORE the request, keyed by server+actor+task so a reload never auto-posts
// a different context's intent. A damaged/unrecognised entry blocks new mutations until explicit review.

export type JournalMeta = { server: string; actor: string; task_id: number };
export type JournalEntry<TBody> = { meta: JournalMeta; body: TBody; savedAt: string };

export class JournalDamagedError extends Error {}

function scopeKey(kind: string, meta: JournalMeta): string {
  return `assembly-scale:${kind}:${meta.server}:${meta.actor}:${meta.task_id}`;
}

function sameMeta(a: JournalMeta, b: JournalMeta): boolean {
  return a.server === b.server && a.actor === b.actor && a.task_id === b.task_id;
}

/** Throws JournalDamagedError on an unrecognised/foreign entry; never silently drops it. */
export function readIntent<TBody>(kind: string, meta: JournalMeta): JournalEntry<TBody> | null {
  const raw = localStorage.getItem(scopeKey(kind, meta));
  if (!raw) return null;
  let data: unknown;
  try { data = JSON.parse(raw); } catch { throw new JournalDamagedError("Сохранённая команда повреждена (не JSON)."); }
  const entry = data as Partial<JournalEntry<TBody>>;
  if (!entry || typeof entry !== "object" || !entry.meta || entry.body === undefined || typeof entry.savedAt !== "string" || !sameMeta(entry.meta, meta)) {
    throw new JournalDamagedError("Сохранённая команда не распознана или относится к другому контексту.");
  }
  return entry as JournalEntry<TBody>;
}

export function saveIntent<TBody>(kind: string, meta: JournalMeta, body: TBody): JournalEntry<TBody> {
  const entry: JournalEntry<TBody> = { meta, body, savedAt: new Date().toISOString() };
  const key = scopeKey(kind, meta), wire = JSON.stringify(entry);
  localStorage.setItem(key, wire);
  if (localStorage.getItem(key) !== wire) throw new Error("Не удалось надёжно сохранить команду. Отправка не выполнена.");
  return entry;
}

export function sameBody<TBody>(entry: JournalEntry<TBody> | null, body: TBody): boolean {
  return !!entry && JSON.stringify(entry.body) === JSON.stringify(body);
}

export function clearIntent(kind: string, meta: JournalMeta): void {
  localStorage.removeItem(scopeKey(kind, meta));
}
