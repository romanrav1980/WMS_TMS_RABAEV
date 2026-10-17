import { ApiRequestError, apiFetch, apiOperationScope } from "../../../../api";
import { parseAck } from "./planModel";
import type { PlanAck } from "./planModel";

// Команды плана консолидации (PUT /{plan_id}, POST /{plan_id}/cancel). Тело сохраняется до отправки; повтор — то же тело и тот же
// operation_id (точный replay возвращает исходный ACK). Команда снимается только при подтверждённом исходе:
// ACK этой операции или ошибка с outcome_confirmed=true. 503/сеть/неизвестное — команда остаётся, нужен явный повтор.

export type PlanIntent = { kind: "SAVE" | "CANCEL"; plan_id: string; method: "PUT" | "POST"; path: string; wire: string; operation_id: string; created_at: string; scope: string };
export type SendResult = { kind: "ack"; ack: PlanAck } | { kind: "refused"; code: string } | { kind: "unknown"; message: string };

const KEY = "retailcase.consolidation.pending.v1";
const key = () => `${KEY}:${apiOperationScope()}`;

export function readPending(): { intent: PlanIntent | null; damaged: string } {
  let raw: string | null;
  try { raw = localStorage.getItem(key()); } catch { return { intent: null, damaged: "Браузер не даёт прочитать сохранённую команду плана; новые изменения заблокированы." }; }
  if (!raw) return { intent: null, damaged: "" };
  try {
    const v = JSON.parse(raw) as PlanIntent, body = JSON.parse(v.wire) as { operation_id?: string };
    if (!v || (v.kind !== "SAVE" && v.kind !== "CANCEL") || v.scope !== apiOperationScope() || body.operation_id !== v.operation_id
      || v.path !== `/api/consolidation-plans/${encodeURIComponent(v.plan_id)}${v.kind === "CANCEL" ? "/cancel" : ""}`) throw new Error("shape");
    return { intent: v, damaged: "" };
  } catch { return { intent: null, damaged: "Сохранённая команда плана повреждена. Исходная запись оставлена в браузере; новые изменения заблокированы — обратитесь к администратору." }; }
}

/** Сохранить намерение до отправки. Сбой записи блокирует отправку. */
export function savePending(kind: PlanIntent["kind"], planId: string, body: Record<string, unknown>): PlanIntent {
  const saved = readPending();
  if (saved.damaged) throw new Error(saved.damaged); // повреждённую исходную запись не перезаписываем новой командой
  if (saved.intent) throw new Error("Сначала завершите ранее сохранённую команду плана.");
  const intent: PlanIntent = { kind, plan_id: planId, method: kind === "SAVE" ? "PUT" : "POST",
    path: `/api/consolidation-plans/${encodeURIComponent(planId)}${kind === "CANCEL" ? "/cancel" : ""}`, wire: JSON.stringify(body),
    operation_id: String(body.operation_id), created_at: new Date().toISOString(), scope: apiOperationScope() };
  const raw = JSON.stringify(intent);
  try { localStorage.setItem(key(), raw); } catch { throw new Error("Не удалось сохранить команду в браузере. Отправка не выполнена."); }
  if (localStorage.getItem(key()) !== raw) throw new Error("Не удалось надёжно сохранить команду. Отправка не выполнена.");
  return intent;
}

function clearIfSame(intent: PlanIntent) {
  try { if (localStorage.getItem(key()) === JSON.stringify(intent)) localStorage.removeItem(key()); } catch { /* запись останется до следующей попытки */ }
}

/** Отправить ровно сохранённые байты. */
export async function sendPending(intent: PlanIntent): Promise<SendResult> {
  try {
    const v = await apiFetch<unknown>(intent.path, { method: intent.method, body: intent.wire, headers: { "Content-Type": "application/json" } });
    const ack = parseAck(v, intent.plan_id, intent.operation_id);
    clearIfSame(intent);
    return { kind: "ack", ack };
  } catch (error) {
    if (error instanceof ApiRequestError) {
      const d = (typeof error.detail === "object" && error.detail ? error.detail : {}) as { code?: string; outcome_confirmed?: boolean };
      if (d.outcome_confirmed === true && error.status !== 503) { clearIfSame(intent); return { kind: "refused", code: d.code ?? `HTTP ${error.status}` }; }
      return { kind: "unknown", message: error.status === 401 || error.status === 403 ? "Доступ закрыт или сессия завершена. Команда сохранена; войдите снова и повторите её." : `Исход не подтверждён (HTTP ${error.status}). Команда сохранена; повторите её тем же номером.` };
    }
    return { kind: "unknown", message: error instanceof Error && error.name !== "Error" ? error.message : "Сервер не ответил. Команда сохранена; повторите её тем же номером." };
  }
}

/** Текст отказа сервера (409 и др.) — коротко; код остаётся для диагностики. */
export const REFUSAL_TEXT: Record<string, string> = {
  CONSOLIDATION_VERSION_CONFLICT: "План уже изменён другим пользователем. Обновите план и внесите правку заново.",
};
export const refusalText = (code: string) => REFUSAL_TEXT[code] ?? `Сервер отклонил изменение (${code}). Обновите план и проверьте данные.`;
