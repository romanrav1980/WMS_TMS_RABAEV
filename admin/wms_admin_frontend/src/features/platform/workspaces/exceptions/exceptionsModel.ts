// Исключения склада (C-0152): карантин, дела качества и расхождения пересчёта из GET /api/tradecase/warehouses/{id}/exceptions.
// Количество и собственник — из учётных строк склада; дело хранит только коды. Списание проводится штатной складской проводкой (POSTED);
// ответ SAP/СКМ — отдельное состояние исходящего документа.

export type CaseState = "OPEN" | "DEFECT" | "RELEASED" | "WAITING_POSTING" | "POSTED";
export type CaseAction = "DEFECT" | "RELEASED" | "APPROVE" | "POST";
export type CompositionLine = { sku_id: string; owner_id: string; base_uom: string; base_qty: string; units: number };
export type QualityCase = { case_id: number; pallet_uid: string; cell: string; state: CaseState; version: number; reason: string;
  decision_note: string | null; approval_note: string | null; opened_by: string; opened_at: string; decided_by: string | null; decided_at: string | null;
  approved_by: string | null; approved_at: string | null; posting_status: string | null; composition: CompositionLine[];
  posted_by?: string | null; posted_at?: string | null; post_operation_id?: string | null; external_status?: "PENDING" | "ACKNOWLEDGED" | "MISSING" | null };
export type QuarantinePallet = { pallet_uid: string; cell: string; article: string; base_qty: string; base_uom: string; stock_version: number; case_id: number | null };
export type Discrepancy = { inventory_task_id: number; status: string; cell: string; article: string; planned_qty: string | null; fact_qty: string | null;
  revision_id: number | null; assigned_to: string | null; updated_at: string | null };
export type ExceptionsSnapshot = { warehouse_id: number; observed_at: string; quarantine: QuarantinePallet[]; cases: QualityCase[]; discrepancies: Discrepancy[] | null };
export type CaseDetail = QualityCase & { units: { unit_key: string; sku_id: string; base_uom: string; base_qty: string; owner_id: string; unchanged: boolean }[];
  events: { action: string; from_state: string | null; to_state: string; actor: string; at: string }[] };

export const STATE_TITLE: Record<CaseState, string> = { OPEN: "Ждёт решения контролёра", DEFECT: "Брак — ждёт утверждения списания",
  RELEASED: "Годен — можно выпустить", WAITING_POSTING: "Списание утверждено — ждёт проведения", POSTED: "Списано со склада" };
/** Действие по состоянию: решение — контролёр, утверждение списания — руководство (право проверяет сервер). */
export const ACTIONS: Record<CaseState, CaseAction[]> = { OPEN: ["DEFECT", "RELEASED"], DEFECT: ["APPROVE"], RELEASED: [], WAITING_POSTING: ["POST"], POSTED: [] };
export const ACTION_TITLE: Record<CaseAction, string> = { DEFECT: "Брак", RELEASED: "Годен", APPROVE: "Утвердить списание", POST: "Провести списание" };
/** Ответ внешней системы по исходящему документу — не подтверждение склада и не выдумывается. */
export const EXTERNAL_TITLE: Record<string, string> = { PENDING: "ответ SAP/СКМ ожидается", ACKNOWLEDGED: "SAP/СКМ подтвердил документ", MISSING: "исходящий документ не найден — сообщите администратору" };
const STATES = new Set(Object.keys(STATE_TITLE));

export class ExceptionsShapeError extends Error {}

/** Ответ сервера → снимок. Чужой склад или неизвестная форма — ошибка, а не пустой список. null у расхождений — раздел закрыт. */
export function parseSnapshot(raw: unknown, warehouse: number): ExceptionsSnapshot {
  const s = raw as ExceptionsSnapshot;
  const ok = s && typeof s === "object" && s.warehouse_id === warehouse && typeof s.observed_at === "string" && Array.isArray(s.quarantine)
    && Array.isArray(s.cases) && (s.discrepancies === null || Array.isArray(s.discrepancies))
    && s.cases.every(c => c && typeof c.case_id === "number" && STATES.has(c.state) && typeof c.version === "number" && Array.isArray(c.composition));
  if (!ok) throw new ExceptionsShapeError("Неожиданный ответ API исключений");
  return s;
}

/** Активное дело держит паллету в карантине: выпуск разрешён только без дела или после решения «годен». */
export const releaseBlocked = (c: QualityCase | undefined) => c != null && c.state !== "RELEASED" && c.state !== "POSTED";

/** Состав одной строкой: артикул · собственник · количество в базовой единице (разные артикулы не складываются). */
export const compositionText = (lines: CompositionLine[]) =>
  lines.map(l => `${l.sku_id} · ${l.owner_id} · ${l.base_qty} ${l.base_uom} (${l.units} ед.)`).join("; ") || "состав не прочитан";

const REFUSAL: Record<string, string> = {
  VERSION_CONFLICT: "Дело уже изменено другим пользователем. Обновите список и повторите.",
  QUALITY_STATE_CONFLICT: "Действие не подходит текущему состоянию дела. Обновите список.",
  QUALITY_COMPOSITION_CHANGED: "Состав или место паллеты изменились после открытия дела. Решение не принято — разберитесь с паллетой.",
  QUALITY_QUARANTINE_REQUIRED: "Сначала поставьте паллету в карантин.", QUALITY_CODE_COMPOSITION_REQUIRED: "У паллеты нет полного кодового состава с собственником.",
  QUALITY_CASE_ACTIVE: "У паллеты уже есть активное дело качества.", QUALITY_CASE_BLOCKS_RELEASE: "Паллету держит дело качества: выпуск возможен после решения «годен».",
  QUALITY_PALLET_NOT_FOUND: "Паллета не найдена или недоступна.", QUALITY_CASE_NOT_FOUND: "Дело не найдено или недоступно.",
  QUALITY_PALLET_SPLIT: "Паллета лежит в нескольких ячейках — дело не открывается.", QUALITY_ACCESS_DENIED: "Это действие вам на этом складе недоступно.",
  TRADE_OWNER_ACCESS_DENIED: "Нет права на изменение товара этого собственника.", QUALITY_OPERATION_CONFLICT: "Этот номер операции уже использован другим действием или пользователем.",
  QUARANTINE_MOVE_FORBIDDEN: "Перемещение в карантин вам недоступно.", QUARANTINE_CELL_REQUIRED: "Одна из ячеек должна быть карантинной.",
  QUARANTINE_MOVE_REQUIRES_WHOLE_PALLET: "В карантин перемещается только паллета целиком.", CELL_NOT_EMPTY: "Целевая ячейка занята другой паллетой.",
  QUALITY_HOLD_ACTIVE: "Паллету держит дело качества: перемещение, отбор и отгрузка запрещены до решения.",
  QUALITY_STOCK_LOCK_BUSY: "Паллета сейчас занята другой складской операцией. Повторите действие.",
  QUALITY_WRITE_OFF_APPROVED_CASE_REQUIRED: "Провести можно только утверждённое списание.", QUALITY_WRITE_OFF_SCOPE_REQUIRED: "Проведение списания вам на этом складе недоступно.",
  QUALITY_WRITE_OFF_CURRENT_WHOLE_UNRESERVED_REQUIRED: "Паллета сдвинута, изменена или зарезервирована — списание не проведено.",
  QUALITY_WRITE_OFF_EXACT_FROZEN_UNITS_REQUIRED: "Коды паллеты не совпадают с зафиксированными в деле — списание не проведено.",
  QUALITY_WRITE_OFF_STANDALONE_REQUIRED: "Паллета входит в грузовое место — сначала разберите его.", QUALITY_WRITE_OFF_QUARANTINE_REQUIRED: "Паллета не в карантинной ячейке.",
};
export const refusalText = (code: string) => REFUSAL[code] ?? `Сервер отклонил действие (${code}). Обновите список и проверьте данные.`;
