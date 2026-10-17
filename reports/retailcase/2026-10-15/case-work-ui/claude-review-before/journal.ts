import { canonical, positive, record, sha256, validCommand, validateAck } from "./contracts";
import type { Intent, Journal } from "./contracts";

export const JOURNAL_KEY = "wms.case-work.journal.v1";
export const EMPTY_JOURNAL: Journal = { schema: 1, pending: null, last: null };
function stored(): string | null {
  try { return localStorage.getItem(JOURNAL_KEY); }
  catch { throw new Error("Браузер не даёт прочитать журнал. Новые действия заблокированы; разрешите локальное хранение и обновите страницу."); }
}

async function validateIntent(value: unknown): Promise<Intent> {
  if (!record(value) || !validCommand(value.body) || !positive(value.task_id) || typeof value.actor !== "string" || !value.actor
    || typeof value.server !== "string" || typeof value.created_at !== "string" || !Number.isFinite(Date.parse(value.created_at))
    || value.url !== `/api/case-pick/tasks/${value.task_id}/resource-commands` || value.wire !== canonical(value.body)
    || value.request_sha256 !== await sha256(value.wire as string)) throw new Error("Журнал операции повреждён. Новые действия заблокированы; обратитесь к старшему смены.");
  const allowed = ["actor", "body", "created_at", "request_sha256", "server", "task_id", "url", "wire"];
  if (Object.keys(value).sort().join() !== allowed.join()) throw new Error("Неизвестный формат сохранённой операции. Действия заблокированы.");
  return value as unknown as Intent;
}
export async function readJournal(): Promise<{ journal: Journal; raw: string | null }> {
  const raw = stored();
  if (raw === null) return { journal: EMPTY_JOURNAL, raw };
  let data: unknown;
  try { data = JSON.parse(raw); }
  catch { throw new Error("Журнал операции повреждён. Исходные данные сохранены; новые действия заблокированы. Обратитесь к старшему смены."); }
  if (!record(data) || data.schema !== 1 || Object.keys(data).sort().join() !== "last,pending,schema") throw new Error("Неизвестный формат журнала. Исходные данные сохранены, новые операции заблокированы.");
  const pending = data.pending === null ? null : await validateIntent(data.pending);
  let last: Journal["last"] = null;
  if (data.last !== null) {
    if (!record(data.last) || Object.keys(data.last).sort().join() !== "ack,intent") throw new Error("Повреждён архив результата операции.");
    const intent = await validateIntent(data.last.intent);
    last = { intent, ack: validateAck(data.last.ack, intent) };
  }
  return { journal: { schema: 1, pending, last }, raw };
}
export function writeJournal(journal: Journal, expectedRaw: string | null): string {
  if (stored() !== expectedRaw) throw new Error("Журнал изменён в другой вкладке. Прочитайте сохранённый результат.");
  const wire = JSON.stringify(journal);
  try { localStorage.setItem(JOURNAL_KEY, wire); }
  catch { throw new Error("Не удалось сохранить операцию в браузере. Отправка заблокирована; проверьте разрешение и свободное место локального хранилища."); }
  if (stored() !== wire) throw new Error("Не удалось надёжно сохранить операцию. Отправка заблокирована.");
  return wire;
}
export async function withJournalLock<T>(run: () => Promise<T>): Promise<T> {
  if (!navigator.locks) return Promise.reject(new Error("Браузер не поддерживает безопасную блокировку журнала. Используйте актуальный Chrome или Edge."));
  return await navigator.locks.request(JOURNAL_KEY, { mode: "exclusive" }, run);
}
