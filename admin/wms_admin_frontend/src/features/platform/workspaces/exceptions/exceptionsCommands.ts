import { ApiRequestError, apiFetch, apiOperationScope } from "../../../../api";

// Команды исключений (дело качества, перемещение в/из карантина, проведение списания). Тело с operation_id сохраняется в браузере ДО отправки;
// повтор — те же байты. Снимается только подтверждённым исходом: квитанцией своей операции или отказом с outcome_confirmed=true.
// 503/сеть/401/403 без подтверждения — команда остаётся (переживает перезагрузку). Одна команда на склад.

export type ExceptionsIntent = { ware: string; kind: "CASE" | "QUARANTINE" | "WRITE_OFF"; title: string; path: string; wire: string; operation_id: string; created_at: string; scope: string };
export type ExceptionsSend = { kind: "ack" } | { kind: "refused"; code: string } | { kind: "unknown"; message: string };

const key = (ware: string) => `retailcase.exceptions.pending.v1:${apiOperationScope()}:${ware}`;
const pathOf = (ware: string, kind: ExceptionsIntent["kind"]) =>
  `/api/tradecase/warehouses/${encodeURIComponent(ware)}/exceptions/${kind === "CASE" ? "cases" : kind === "WRITE_OFF" ? "write-offs" : "quarantine-moves"}`;

export function readPending(ware: string): { intent: ExceptionsIntent | null; damaged: string } {
  let raw: string | null;
  try { raw = localStorage.getItem(key(ware)); } catch { return { intent: null, damaged: "Браузер не даёт прочитать сохранённую команду; новые действия заблокированы." }; }
  if (!raw) return { intent: null, damaged: "" };
  try {
    const v = JSON.parse(raw) as ExceptionsIntent, body = JSON.parse(v.wire) as { operation_id?: string };
    if (v.ware !== ware || v.scope !== apiOperationScope() || body.operation_id !== v.operation_id || v.path !== pathOf(ware, v.kind)) throw new Error("shape");
    return { intent: v, damaged: "" };
  } catch { return { intent: null, damaged: "Сохранённая команда повреждена. Запись оставлена в браузере; новые действия заблокированы — обратитесь к администратору." }; }
}

/** Сохранить намерение до отправки; сбой записи — отправки нет. */
export function savePending(ware: string, kind: ExceptionsIntent["kind"], title: string, body: Record<string, unknown>): ExceptionsIntent {
  const saved = readPending(ware);
  if (saved.damaged) throw new Error(saved.damaged);
  if (saved.intent) throw new Error("Сначала завершите ранее сохранённую команду.");
  const operation = `exc-${crypto.randomUUID()}`;
  const intent: ExceptionsIntent = { ware, kind, title, path: pathOf(ware, kind), operation_id: operation, created_at: new Date().toISOString(),
    scope: apiOperationScope(), wire: JSON.stringify({ operation_id: operation, ...body }) };
  const raw = JSON.stringify(intent);
  try { localStorage.setItem(key(ware), raw); } catch { throw new Error("Не удалось сохранить команду в браузере. Отправка не выполнена."); }
  if (localStorage.getItem(key(ware)) !== raw) throw new Error("Не удалось надёжно сохранить команду. Отправка не выполнена.");
  return intent;
}

function clearIfSame(intent: ExceptionsIntent) {
  try { if (localStorage.getItem(key(intent.ware)) === JSON.stringify(intent)) localStorage.removeItem(key(intent.ware)); } catch { /* останется до повтора */ }
}

/** Отправить ровно сохранённые байты. */
export async function sendPending(intent: ExceptionsIntent): Promise<ExceptionsSend> {
  try {
    const v = await apiFetch<{ operation_id?: string }>(intent.path, { method: "POST", body: intent.wire });
    // Квитанция принимается только своей операции: чужой/неполный/поздний ответ команду не снимает.
    if (v?.operation_id !== intent.operation_id) return { kind: "unknown", message: "Ответ сервера не относится к этой команде. Команда сохранена; повторите её." };
    clearIfSame(intent);
    return { kind: "ack" };
  } catch (error) {
    if (error instanceof ApiRequestError) {
      const d = (typeof error.detail === "object" && error.detail ? error.detail : {}) as { code?: string; outcome_confirmed?: boolean };
      if (d.outcome_confirmed === true && error.status !== 503) { clearIfSame(intent); return { kind: "refused", code: d.code ?? `HTTP ${error.status}` }; }
      if (error.status === 422) { clearIfSame(intent); return { kind: "refused", code: "QUALITY_REQUEST_INVALID" }; }
      return { kind: "unknown", message: error.status === 401 || error.status === 403 ? "Доступ закрыт или сессия завершена. Команда сохранена; войдите снова и повторите её."
        : `Исход не подтверждён (HTTP ${error.status}). Команда сохранена; повторите её тем же номером.` };
    }
    return { kind: "unknown", message: "Сервер не ответил. Команда сохранена; повторите её тем же номером." };
  }
}
