import { ApiRequestError, apiFetch, apiOperationScope } from "../../../../api";

// Бумажная сборка коробов CASE (C-0156, BP15). Бланк — копия строк существующего CASE-задания с версией каждой строки (CPICK).
// Факт после восстановления уходит существующей командой подтверждения строки с версией бланка; сервер отказывает по старому бланку.
// Тело с operation_id сохраняется в браузере ДО отправки; повтор — те же байты. Снимается только квитанцией своей операции
// или отказом с outcome_confirmed=true; 503/сеть/401/403 — команда остаётся и переживает перезагрузку.

export type CaseTask = { case_pick_task_id: number; status: string; assigned_to: string | null; sscc: string | null; order_no: string | null;
  customer_name: string | null; total_lines: number | null; picked_lines: number | null };
export type CaseLine = { line_id: number; articul: string; product_name: string | null; cell_code: string | null; pick_sequence: number | null; unit_code?: string | null;
  planned_qty: string; picked_qty: string; status: string; required_scan_mode: string | null; signature: string; reference: string;
  barcode_svg: string; device_required: "MARKING_SCAN_REQUIRED" | "WEIGHT_LABEL_SCAN_REQUIRED" | null; scale_reading: boolean };
export type CasePaper = { task: { task_id: number; ware_id: number; wave_code: string | null; order_no: string | null; customer_name: string | null;
  sscc: string; status: string; assigned_to: string | null }; lines: CaseLine[]; prepared_at: string };

export const LIMIT = 100;
const OPEN = new Set(["NEW", "ASSIGNED", "IN_PROGRESS", "PARTIAL", "WAIT_REPLENISHMENT"]);
export const WORKING = new Set(["IN_PROGRESS", "PARTIAL", "WAIT_REPLENISHMENT"]);  // native подтверждает строку только в этих состояниях
export const CASE_STATE: Record<string, string> = { NEW: "Новое", ASSIGNED: "Назначено", IN_PROGRESS: "В работе", PARTIAL: "Частично",
  WAIT_REPLENISHMENT: "Ждёт пополнения" };
const DONE_LINE = new Set(["PICKED", "DONE", "SHORT_PICKED", "CANCELLED"]);
export const DEVICE: Record<string, string> = { MARKING_SCAN_REQUIRED: "нужен код маркировки каждой единицы — сканером",
  WEIGHT_LABEL_SCAN_REQUIRED: "нужна весовая этикетка короба — только ТСД" };  // весовой товар без этикетки — показание весов, как и сейчас

export function openCaseTasks(raw: unknown): CaseTask[] {
  if (!Array.isArray(raw) || !raw.every(t => t && Number.isSafeInteger(t.case_pick_task_id) && typeof t.status === "string")) throw new Error("Неожиданный ответ очереди CASE");
  return (raw as CaseTask[]).filter(t => OPEN.has(t.status));
}

export function casePaper(raw: unknown): CasePaper {
  const v = raw as CasePaper;
  if (!v || !v.task || !Number.isSafeInteger(v.task.task_id) || !Array.isArray(v.lines)
    || !v.lines.every(l => Number.isSafeInteger(l.line_id) && /^[A-F0-9]{64}$/.test(l.signature) && l.reference === `CPICK:${v.task.task_id}:${l.line_id}:${l.signature}`))
    throw new Error("Неожиданный ответ бланка CASE");
  return v;
}

export const lineOpen = (l: CaseLine) => !DONE_LINE.has(l.status);
export const qty = (v: string | null) => v == null ? "—" : v.startsWith(".") ? "0" + v : v;
const CASE_UNITS: Record<string, string> = { EA: "шт.", BOX: "кор.", KG: "кг" };
export const caseUnit = (l: CaseLine) => CASE_UNITS[l.unit_code ?? ""] ?? (l.scale_reading ? "кг" : l.unit_code || "единица не указана");

/** Код со штрихкода бланка CASE: CPICK:<задание>:<строка>:<версия строки>. WTASK сюда не подходит: номера сущностей могут совпадать. */
export function parseCaseReference(text: string): { taskId: number; lineId: number; signature: string } | null {
  const m = /^CPICK:([1-9]\d{0,17}):([1-9]\d{0,17}):([A-F0-9]{64})$/.exec(text.trim());
  return m && Number.isSafeInteger(Number(m[1])) && Number.isSafeInteger(Number(m[2])) ? { taskId: Number(m[1]), lineId: Number(m[2]), signature: m[3] } : null;
}

export type CaseIntent = { task: number; line: number; path: string; wire: string; operation_id: string; scope: string; created_at: string };
export type CaseSend = { kind: "ack" } | { kind: "refused"; code: string } | { kind: "unknown"; message: string } | { kind: "foreign"; message: string };
export type UnitScan = { system_code: string; profile_code: string; code: string };
export type CaseFact = { fact_qty: string; scan_cell: string; scan_container: string; scan_product: string; expected_case_signature: string; unit_scans?: UnitScan[] };
/** Профили маркировки строки из существующего marking-policy; неизвестная форма — ошибка. */
export function markingProfiles(raw: unknown): { system_code: string; profile_code: string }[] {
  const v = raw as { marking_required?: boolean; profiles?: { system_code: string; profile_code: string }[] };
  if (!v || !Array.isArray(v.profiles) || !v.profiles.every(p => typeof p.system_code === "string" && typeof p.profile_code === "string")) throw new Error("Неожиданный ответ правил маркировки");
  return v.profiles;
}

const key = (task: number, line: number) => `retailcase.casepaper.pending.v1:${apiOperationScope()}:${task}:${line}`;
const pathOf = (task: number, line: number) => `/api/case-pick/tasks/${task}/lines/${line}/confirm`;

export function readCasePending(task: number, line: number): { intent: CaseIntent | null; damaged: string } {
  let raw: string | null;
  try { raw = localStorage.getItem(key(task, line)); } catch { return { intent: null, damaged: "Браузер не даёт прочитать сохранённый факт; внесение заблокировано." }; }
  if (!raw) return { intent: null, damaged: "" };
  try {
    const v = JSON.parse(raw) as CaseIntent, body = JSON.parse(v.wire) as { operation_id?: string };
    if (v.task !== task || v.line !== line || v.scope !== apiOperationScope() || v.path !== pathOf(task, line) || body.operation_id !== v.operation_id) throw new Error("shape");
    return { intent: v, damaged: "" };
  } catch { return { intent: null, damaged: "Сохранённый факт повреждён. Запись оставлена в браузере; внесение заблокировано — обратитесь к администратору." }; }
}

/** Сохранить факт до отправки; сбой записи — отправки нет. Количество — накопленное по строке, как в штатной команде. */
export function saveCasePending(task: number, line: number, fact: CaseFact): CaseIntent {
  const saved = readCasePending(task, line);
  if (saved.damaged) throw new Error(saved.damaged);
  if (saved.intent) throw new Error("Сначала завершите ранее сохранённый факт этой строки.");
  if (!/^\d{1,18}(\.\d{1,9})?$/.test(fact.fact_qty)) throw new Error("Количество — число, до 9 знаков после точки.");
  const units = fact.unit_scans ?? [];
  if (units.length > 10000 || new Set(units.map(u => `${u.system_code}|${u.profile_code}|${u.code}`)).size !== units.length) throw new Error("Коды маркировки повторяются или их больше 10000.");
  // С кодами маркировки товар определяется кодами (native не требует скан товара); без кодов скан товара обязателен.
  if (!fact.scan_cell.trim() || !fact.scan_container.trim() || (!units.length && !fact.scan_product.trim())) throw new Error("Отсканируйте ячейку, короб (SSCC) и товар.");
  const operation = `case-paper-${crypto.randomUUID()}`;
  const intent: CaseIntent = { task, line, path: pathOf(task, line), operation_id: operation, scope: apiOperationScope(), created_at: new Date().toISOString(),
    wire: JSON.stringify({ operation_id: operation, fact_qty: fact.fact_qty, scan_cell: fact.scan_cell.trim(), scan_container: fact.scan_container.trim(),
      scan_product: fact.scan_product.trim() || null, expected_case_signature: fact.expected_case_signature, ...(units.length ? { unit_scans: units } : {}) }) };
  const raw = JSON.stringify(intent);
  try { localStorage.setItem(key(task, line), raw); } catch { throw new Error("Не удалось сохранить факт в браузере. Отправка не выполнена."); }
  if (localStorage.getItem(key(task, line)) !== raw) throw new Error("Не удалось надёжно сохранить факт. Отправка не выполнена.");
  return intent;
}

function clearIfSame(intent: CaseIntent) {
  try { if (localStorage.getItem(key(intent.task, intent.line)) === JSON.stringify(intent)) localStorage.removeItem(key(intent.task, intent.line)); } catch { /* останется до повтора */ }
}

/** Запись этого входа и именно этот факт: scope, путь и байты совпадают с сохранённым. */
const inScope = (intent: CaseIntent) => { try { return intent.scope === apiOperationScope(); } catch { return false; } };
const own = (intent: CaseIntent) => inScope(intent) && readCasePending(intent.task, intent.line).intent !== null
  && (() => { try { return localStorage.getItem(key(intent.task, intent.line)) === JSON.stringify(intent); } catch { return false; } })();
const OTHER_LOGIN: CaseSend = { kind: "foreign", message: "Вход сменился: сохранённый факт прежнего входа не отправлен и не показан." };

/** Отправить ровно сохранённые байты существующей командой подтверждения строки. Запись снимается только квитанцией своей операции или
 *  подтверждённым отказом своей операции (409 с outcome_confirmed=true и тем же operation_id, не конфликт содержимого), либо 422 формы. */
export async function sendCasePending(intent: CaseIntent): Promise<CaseSend> {
  if (!own(intent)) return OTHER_LOGIN;  // старое намерение не уходит под другим входом
  try {
    const v = await apiFetch<{ operation_id?: string }>(intent.path, { method: "POST", body: intent.wire });
    if (!own(intent)) return OTHER_LOGIN;  // Logout also removes credentials; a late reply must not throw or clear another record.
    if (v?.operation_id !== intent.operation_id) return { kind: "unknown", message: "Ответ сервера не относится к этому факту. Факт сохранён; повторите его." };
    clearIfSame(intent);
    return { kind: "ack" };
  } catch (error) {
    if (!own(intent)) return OTHER_LOGIN;
    if (error instanceof ApiRequestError) {
      const d = (typeof error.detail === "object" && error.detail ? error.detail : {}) as { code?: string; rule_reason?: string; outcome_confirmed?: boolean; operation_id?: string; read_before_retry?: boolean };
      const reason = d.rule_reason || d.code || `HTTP ${error.status}`;
      if (error.status === 409 && d.outcome_confirmed === true && d.operation_id === intent.operation_id && !d.read_before_retry && !reason.includes("CONFLICT_CONTENT") && !reason.includes("CONTENT_CONFLICT")) {
        clearIfSame(intent); return { kind: "refused", code: reason };
      }
      // 422: тело не прошло проверку формы до проведения (эффекта не было); это же тело никогда не пройдёт.
      if (error.status === 422 && (d.code === "CASE_COMMAND_INVALID" || Array.isArray(error.detail))) { clearIfSame(intent); return { kind: "refused", code: d.code ?? "CASE_COMMAND_INVALID" }; }
      if (reason.includes("CONTENT_CONFLICT")) return { kind: "unknown", message: "Номер этой операции уже использован с другими данными. Факт сохранён без изменений; сверьте строку в карточке CASE и обратитесь к руководителю." };
      return { kind: "unknown", message: error.status === 401 || error.status === 403 ? "Доступ закрыт или сессия завершена. Факт сохранён; войдите снова и повторите его."
        : `Исход не подтверждён (HTTP ${error.status}). Факт сохранён; повторите его тем же номером.` };
    }
    return { kind: "unknown", message: "Сервер не ответил. Факт сохранён; повторите его тем же номером." };
  }
}

/** Понятный текст отказа сервера. */
export function refusal(code: string): string {
  if (code.includes("CASE_PAPER_LINE_CHANGED")) return "Бланк устарел: строку изменили после печати. Проверьте, что сделано, и подготовьте новый бланк.";
  if (code.includes("CASE_CELL_CARRIER_SCAN_REQUIRED")) return "Ячейка или короб не совпали с заданием.";
  if (code.includes("CASE_FACT_NOT_INCREASING") || code.includes("FACT_NOT_INCREASING")) return "Количество должно быть больше уже подтверждённого (вводится накопленное по строке).";
  if (code.includes("CASE_TASK_ACTOR_CONFLICT")) return "Задание назначено другому сотруднику; подтверждать за него может только сотрудник с правом управления сборкой CASE.";
  if (code.includes("CASE_TASK_LINE_STATE_CONFLICT")) return "Задание или строка не в работе: начните задание штатно или проверьте строку.";
  if (code.includes("CASE_MARKED_UNIT_SCANS_REQUIRED")) return "Для маркированного товара нужны коды маркировки каждой собранной единицы.";
  if (code.includes("CASE_SELECTED_UNIT_NOT_OWNED") || code.includes("CASE_SCANNED_UNIT_QUANTITY_CONFLICT")) return "Коды маркировки не совпали с единицами в ячейке или с количеством.";
  if (code.includes("CASE_COMMAND_INVALID")) return "Данные факта не прошли проверку (например, повторный или неизвестный код). Исправьте и внесите заново.";
  return "Сервер отказал в подтверждении строки.";
}
