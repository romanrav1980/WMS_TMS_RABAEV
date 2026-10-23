import { ApiRequestError, apiFetch, apiOperationScope } from "../../../../api";
import type { YardAction } from "./yardModel";

// Команды двора. Тело с operation_id сохраняется в браузере ДО отправки; повтор — те же байты и тот же номер (сервер вернёт
// исходный ответ). Команда снимается только при подтверждённом исходе: ответ визита или отказ с outcome_confirmed=true.
// 503/сеть/401/403 без подтверждения — команда остаётся (переживает перезагрузку), нужен явный повтор. Одна команда на склад.

// EXPECT — новый визит рейса (visit_id 0 до ответа сервера).
export type YardIntent = { ware: string; visit_id: number; action: YardAction | "EXPECT"; path: string; wire: string; operation_id: string; created_at: string; scope: string };
export type YardSend = { kind: "ack" } | { kind: "refused"; code: string } | { kind: "unknown"; message: string };

const key = (ware: string) => `retailcase.yard.pending.v1:${apiOperationScope()}:${ware}`;
const pathOf = (ware: string, visit: number) => `/api/tradecase/warehouses/${encodeURIComponent(ware)}/yard/visits${visit ? `/${visit}/transitions` : ""}`;

export function readPending(ware: string): { intent: YardIntent | null; damaged: string } {
  let raw: string | null;
  try { raw = localStorage.getItem(key(ware)); } catch { return { intent: null, damaged: "Браузер не даёт прочитать сохранённую команду двора; новые действия заблокированы." }; }
  if (!raw) return { intent: null, damaged: "" };
  try {
    const v = JSON.parse(raw) as YardIntent, body = JSON.parse(v.wire) as { operation_id?: string; action?: string };
    if (v.ware !== ware || v.scope !== apiOperationScope() || body.operation_id !== v.operation_id || (body.action ?? "EXPECT") !== v.action || v.path !== pathOf(ware, v.visit_id)) throw new Error("shape");
    return { intent: v, damaged: "" };
  } catch { return { intent: null, damaged: "Сохранённая команда двора повреждена. Запись оставлена в браузере; новые действия заблокированы — обратитесь к администратору." }; }
}

/** Сохранить намерение до отправки; сбой записи — отправки нет. */
export function savePending(ware: string, visit: number, version: number, action: YardAction | "EXPECT",
  extra: { dock?: string; reason?: string; trip_id?: string; supply_ids?: string[]; vehicle?: string; planned_arrival_at?: string }): YardIntent {
  const saved = readPending(ware);
  if (saved.damaged) throw new Error(saved.damaged);
  if (saved.intent) throw new Error("Сначала завершите ранее сохранённую команду двора.");
  const operation = `yard-${crypto.randomUUID()}`;
  const intent: YardIntent = { ware, visit_id: visit, action, path: pathOf(ware, visit), operation_id: operation, created_at: new Date().toISOString(),
    scope: apiOperationScope(), wire: JSON.stringify(action === "EXPECT" ? { operation_id: operation, ...extra } : { operation_id: operation, expected_version: version, action, ...extra }) };
  const raw = JSON.stringify(intent);
  try { localStorage.setItem(key(ware), raw); } catch { throw new Error("Не удалось сохранить команду в браузере. Отправка не выполнена."); }
  if (localStorage.getItem(key(ware)) !== raw) throw new Error("Не удалось надёжно сохранить команду. Отправка не выполнена.");
  return intent;
}

function clearIfSame(intent: YardIntent) {
  try { if (localStorage.getItem(key(intent.ware)) === JSON.stringify(intent)) localStorage.removeItem(key(intent.ware)); } catch { /* останется до повтора */ }
}

/** Отправить ровно сохранённые байты. */
export async function sendPending(intent: YardIntent, retry = true): Promise<YardSend> {
  try {
    const v = await apiFetch<{ visit_id?: number; operation_id?: string }>(intent.path, { method: "POST", body: intent.wire });
    // Квитанция принимается только своей операции и своего визита: чужой/неполный/поздний ответ команду не снимает.
    if (v?.operation_id !== intent.operation_id || typeof v.visit_id !== "number" || (intent.visit_id && v.visit_id !== intent.visit_id)) return { kind: "unknown", message: "Ответ сервера не относится к этому визиту. Команда сохранена; повторите её." };
    clearIfSame(intent);
    return { kind: "ack" };
  } catch (error) {
    if (error instanceof ApiRequestError) {
      const d = (typeof error.detail === "object" && error.detail ? error.detail : {}) as { code?: string; outcome_confirmed?: boolean };
      // A current access/validation refusal cannot establish the outcome of an earlier unacknowledged request.
      if (retry && ([401, 403, 404, 422].includes(error.status) || ["YARD_SUPPLY_NOT_FOUND", "YARD_VISIT_NOT_FOUND", "YARD_TRIP_REQUIRED"].includes(d.code ?? ""))) {
        return { kind: "unknown", message: "Сервер не разрешил повтор сохранённой команды. Её первоначальный результат не подтверждён; восстановите доступ или обратитесь к администратору. Номер команды сохранён." };
      }
      if (d.outcome_confirmed === true && error.status !== 503) { clearIfSame(intent); return { kind: "refused", code: d.code ?? `HTTP ${error.status}` }; }
      if (error.status === 422) { clearIfSame(intent); return { kind: "refused", code: "YARD_REQUEST_INVALID" }; } // тело не принято — исполнения не было
      return { kind: "unknown", message: error.status === 401 || error.status === 403 ? "Доступ закрыт или сессия завершена. Команда сохранена; войдите снова и повторите её."
        : `Исход не подтверждён (HTTP ${error.status}). Команда сохранена; повторите её тем же номером.` };
    }
    return { kind: "unknown", message: "Сервер не ответил. Команда сохранена; повторите её тем же номером." };
  }
}
