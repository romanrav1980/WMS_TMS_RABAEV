// Очередь для бумажных заданий (C-0155, BP15): ограниченный список разрешённых незавершённых складских заданий одного склада
// из существующей scoped очереди. Бланк и сверку версии делает панель TaskPaperPanel (root); печать задание не выполняет.

export type QueueTask = { task_id: number; task_type: string | null; status: string; assigned_to: string | null; from_cell: string | null;
  to_cell: string | null; to_slot_code: string | null; uid_pallet: string | null; sscc: string | null; raw_articul: string | null;
  target_articul: string | null; qty_exact: string | null; unit_code: string | null; planned_start_at: string | null };

export const LIMIT = 100;  // одна страница очереди; вся выгрузка склада не делается
const OPEN = new Set(["PLANNED", "ASSIGNED", "IN_PROGRESS"]);  // native допускает обычное завершение только из этих состояний
export const STATE: Record<string, string> = { PLANNED: "Запланировано", ASSIGNED: "Назначено", IN_PROGRESS: "В работе" };
export const ACTION: Record<string, string> = { PUTAWAY: "Размещение", REPLENISHMENT: "Пополнение", PICK: "Отбор", PICKING: "Отбор", MOVE: "Перемещение" };
const UNIT: Record<string, string> = { EA: "шт.", BOX: "кор.", HU: "место", CASE: "короб", KG: "кг", PALLET: "паллета" };  // как на бланке

/** Ответ очереди → только незавершённые задания этого склада; неизвестная форма — ошибка, а не пустой список. */
export function openTasks(raw: unknown): QueueTask[] {
  if (!Array.isArray(raw) || !raw.every(t => t && Number.isSafeInteger(t.task_id) && typeof t.status === "string")) throw new Error("Неожиданный ответ очереди заданий");
  return (raw as QueueTask[]).filter(t => OPEN.has(t.status));
}

/** Код со штрихкода бланка: WTASK:<номер>:<версия>. Номер и версия — из бланка, не из ввода сотрудника. */
export function parseReference(text: string): { taskId: number; signature: string } | null {
  const m = /^WTASK:([1-9]\d{0,17}):([A-F0-9]{64})$/.exec(text.trim());
  return m && Number.isSafeInteger(Number(m[1])) ? { taskId: Number(m[1]), signature: m[2] } : null;
}

export const taskLine = (t: QueueTask) => [ACTION[t.task_type ?? ""] ?? "Складская работа", t.raw_articul ?? t.target_articul ?? "грузовое место",
  t.qty_exact ? `${t.qty_exact.startsWith(".") ? "0" + t.qty_exact : t.qty_exact} ${UNIT[t.unit_code ?? ""] ?? t.unit_code ?? ""}`.trim() : null].filter(Boolean).join(" · ");
export const route = (t: QueueTask) => `${t.from_cell ?? "—"} → ${t.to_cell ?? "—"}${t.to_slot_code ? ` · слот ${t.to_slot_code}` : ""}`;
