import { RAW_ADMIN_BASE } from "../../../../api";

// Восстановление недостач сборки (C0117): GET /api/inventory/recovery-shorts?ware_id=&limit=50 — JSON-массив, не больше 50 строк.
// Нет has_more/cursor/total: при 50 строках полнота неизвестна. Даты — legacy-строки без пояса (time_status нет).
// remaining_seconds/age_seconds — относительные значения серверного снимка, не живой SLA.

export const RECOVERY_LIMIT = 50;
export type RecoveryRow = {
  short_id: number; case_pick_task_id: number; case_pick_line_id: number; pick_wave_id: number; warehouse_id: number;
  inventory_task_id: number | null; replenish_task_id: number | null; warehouse_task_id: number | null;
  status: string; recovery_state: string | null; cell: string | null; article: string | null; picker: string | null;
  inventory_status: string | null; auditor: string | null; count_operation_id: string | null;
  replenish_status: string | null; wait_reason: string | null; recovery_last_error: string | null;
  short_quantity: string | null; restored_quantity: string | null; order_remaining_quantity: string | null;
  age_seconds: number | null; remaining_seconds: number | null; recovery_deadline_at: string | null; restored_at: string | null;
};

export class RecoveryShapeError extends Error {}
const rec = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);
const id = (v: unknown) => typeof v === "number" && Number.isSafeInteger(v) && v > 0;
const nid = (v: unknown) => v === null || v === undefined || id(v);
const ntext = (v: unknown) => v === null || v === undefined || typeof v === "string";
const nnum = (v: unknown) => v === null || v === undefined || (typeof v === "number" && Number.isFinite(v));
const qty = (v: unknown) => v === null || v === undefined || (typeof v === "string" && /^-?\d*\.?\d+$/.test(v));
const TEXT = ["status", "recovery_state", "cell", "article", "picker", "inventory_status", "auditor", "count_operation_id", "replenish_status", "wait_reason", "recovery_last_error", "recovery_deadline_at", "restored_at"];

/** Строгая проверка формы. Неизвестная форма — ошибка источника, а не «недостач нет». */
export function parseRecovery(v: unknown, warehouse: number | null): RecoveryRow[] {
  if (!Array.isArray(v)) throw new RecoveryShapeError("Неожиданный ответ источника восстановления: не список.");
  if (v.length > RECOVERY_LIMIT) throw new RecoveryShapeError("Источник вернул больше строк, чем разрешает контракт.");
  for (const r of v) {
    if (!rec(r) || !["short_id", "case_pick_task_id", "case_pick_line_id", "pick_wave_id", "warehouse_id"].every(k => id(r[k]))
      || !["inventory_task_id", "replenish_task_id", "warehouse_task_id"].every(k => nid(r[k])) || typeof r.status !== "string"
      || !TEXT.every(k => ntext(r[k])) || !["short_quantity", "restored_quantity", "order_remaining_quantity"].every(k => qty(r[k]))
      || !nnum(r.age_seconds) || !nnum(r.remaining_seconds)) throw new RecoveryShapeError("Неожиданный ответ источника восстановления: строка неполная.");
    if (warehouse !== null && r.warehouse_id !== warehouse) throw new RecoveryShapeError("Источник вернул строку другого склада.");
  }
  return (v as Record<string, unknown>[]).map(r => Object.fromEntries(Object.entries(r).map(([k, x]) => [k, x === undefined ? null : x]))) as unknown as RecoveryRow[];
}

/** Этап — по фактическим полям сервера (тем же условиям, что отбирает источник). Неизвестное не считается «готово». */
export type Stage = "FAILED" | "DECISION" | "INVENTORY" | "REPLENISHMENT" | "READY" | "UNKNOWN";
export const STAGES: { id: Stage; label: string; tone: "bad" | "other" | "plan" | "ship" | "closed" }[] = [
  { id: "FAILED", label: "Ошибка", tone: "bad" }, { id: "DECISION", label: "Ждёт решения", tone: "other" },
  { id: "INVENTORY", label: "Пересчёт", tone: "plan" }, { id: "REPLENISHMENT", label: "Пополнение", tone: "plan" },
  { id: "READY", label: "Готово к продолжению", tone: "ship" }, { id: "UNKNOWN", label: "Неизвестное состояние", tone: "closed" },
];
export function stageOf(r: RecoveryRow): Stage {
  if (r.recovery_state === "FAILED") return "FAILED";
  if (r.status === "CREATED" || r.status === "PENDING_APPROVAL") return "DECISION";
  if (r.recovery_state === "WAIT_INVENTORY") return "INVENTORY";
  if (r.recovery_state === "WAIT_REPLENISHMENT") return "REPLENISHMENT";
  if (r.recovery_state === "READY") return "READY";
  return "UNKNOWN";
}
export const stageMeta = (s: Stage) => STAGES.find(x => x.id === s)!;

/** Относительное время серверного снимка: «осталось N мин» / «просрочено N мин». Не живой таймер. */
export function remainingText(sec: number | null): string | null {
  if (sec === null) return null;
  const m = Math.round(Math.abs(sec) / 60);
  return sec >= 0 ? `осталось ~${m} мин` : `просрочено на ~${m} мин`;
}
/** Legacy-дата без пояса: показать цифры источника, не пересчитывать браузером и не выдавать за UTC. */
export const legacyDate = (v: string | null) => v ? v.replace("T", " ").replace(/\.\d+$/, "").slice(0, 16) : "—";

const API_ORIGIN = RAW_ADMIN_BASE.replace(/\/wms-admin$/, "");
export const recoveryHelpUrl = (anchor = "") => `${API_ORIGIN}/help/short-recovery.html${anchor ? "#" + anchor : ""}`;

/** Только существующие экраны и поддержанные ими параметры (проверено по исходникам raw UI). */
export const ownerLinks = (r: RecoveryRow) => ({
  investigation: `${RAW_ADMIN_BASE}/short-investigation.html?short_id=${r.short_id}`,
  inventory: r.inventory_task_id ? `${RAW_ADMIN_BASE}/inventory-count.html?inventory_task_id=${r.inventory_task_id}${r.cell ? "&cell=" + encodeURIComponent(r.cell) : ""}${r.article ? "&article=" + encodeURIComponent(r.article) : ""}` : null,
  replenishment: `${RAW_ADMIN_BASE}/wave-replenishment.html?wave_id=${r.pick_wave_id}&ware_id=${r.warehouse_id}`,
  warehouseTask: r.warehouse_task_id ? `${RAW_ADMIN_BASE}/warehouse-tasks.html?task_id=${r.warehouse_task_id}` : null,
});
