// Двор склада (C-0149): визиты машин из GET /api/tradecase/warehouses/{id}/yard/visits. Опоздание и ожидание — по часам
// сервера (observed_at снимка), не браузера. Визиты скрытых владельцев сервер не отдаёт вовсе.

export type YardState = "EXPECTED" | "ARRIVED" | "AT_DOCK" | "WORKING" | "WORK_DONE" | "DEPARTED" | "CANCELLED";
export type YardAction = "ARRIVE" | "ASSIGN_DOCK" | "REASSIGN_DOCK" | "START" | "FINISH" | "DEPART" | "CANCEL";
export type YardVisit = { visit_id: number; warehouse_id: number; trip_id: string | null; vehicle: string | null; dock: string | null;
  planned_dock: string | null; state: YardState; version: number; planned_arrival_at: string | null; arrived_at: string | null;
  docked_at: string | null; work_started_at: string | null; work_finished_at: string | null; updated_by: string | null };
export type YardSnapshot = { warehouse_id: number; observed_at: string; visits: YardVisit[] };

export const STATE_TITLE: Record<YardState, string> = { EXPECTED: "Ожидается", ARRIVED: "На площадке", AT_DOCK: "У ворот", WORKING: "Идёт работа",
  WORK_DONE: "Работа закончена", DEPARTED: "Выехала", CANCELLED: "Отменён" };
export const ACTIONS: Record<YardState, YardAction[]> = { EXPECTED: ["ARRIVE", "CANCEL"], ARRIVED: ["ASSIGN_DOCK", "CANCEL"],
  AT_DOCK: ["START", "REASSIGN_DOCK", "CANCEL"], WORKING: ["FINISH"], WORK_DONE: ["DEPART"], DEPARTED: [], CANCELLED: [] };
export const ACTION_TITLE: Record<YardAction, string> = { ARRIVE: "Приехала", ASSIGN_DOCK: "Поставить к воротам", REASSIGN_DOCK: "Сменить ворота",
  START: "Начать работу", FINISH: "Закончить работу", DEPART: "Выезд", CANCEL: "Отменить визит" };
export const GROUPS: YardState[] = ["ARRIVED", "AT_DOCK", "WORKING", "WORK_DONE", "EXPECTED"];
const STATES = new Set(Object.keys(STATE_TITLE));

export class YardShapeError extends Error {}

/** Ответ сервера → снимок двора. Чужой склад или неизвестная форма — ошибка, а не пустой двор. */
export function parseSnapshot(raw: unknown, warehouse: number): YardSnapshot {
  const s = raw as YardSnapshot;
  const ok = s && typeof s === "object" && s.warehouse_id === warehouse && typeof s.observed_at === "string" && Array.isArray(s.visits)
    && s.visits.every(v => v && typeof v.visit_id === "number" && v.warehouse_id === warehouse && STATES.has(v.state) && typeof v.version === "number");
  if (!ok) throw new YardShapeError("Неожиданный ответ API двора");
  return s;
}

const minutes = (from: string, to: string) => Math.floor((Date.parse(to) - Date.parse(from)) / 60000);

/** Опоздание приезда (ожидаемый визит) или ожидание ворот (на площадке) в минутах по часам сервера; null — не применимо. */
export function delay(v: YardVisit, observedAt: string): { kind: "LATE" | "WAITING"; min: number } | null {
  if (v.state === "EXPECTED" && v.planned_arrival_at && minutes(v.planned_arrival_at, observedAt) > 0)
    return { kind: "LATE", min: minutes(v.planned_arrival_at, observedAt) };
  if (v.state === "ARRIVED" && v.arrived_at) return { kind: "WAITING", min: Math.max(0, minutes(v.arrived_at, observedAt)) };
  return null;
}

/** Чего не хватает визиту, чтобы им можно было управлять без догадок. */
export function missing(v: YardVisit): string[] {
  const out: string[] = [];
  if (!v.vehicle) out.push("машина в рейсе не указана");
  if (v.state === "EXPECTED" && !v.planned_arrival_at) out.push("нет плана приезда — опоздание не определяется");
  if ((v.state === "EXPECTED" || v.state === "ARRIVED") && !v.planned_dock) out.push("ворота в рейсе не запланированы");
  return out;
}

/** Конфликт: запланированные ворота заняты другим визитом. Окончательную проверку делает сервер при постановке. */
export function conflicts(visits: YardVisit[]): Map<number, string> {
  const busy = new Map(visits.filter(v => v.dock && ["AT_DOCK", "WORKING", "WORK_DONE"].includes(v.state)).map(v => [v.dock!, v.visit_id]));
  const out = new Map<number, string>();
  for (const v of visits) {
    const holder = v.planned_dock ? busy.get(v.planned_dock) : undefined;
    if ((v.state === "EXPECTED" || v.state === "ARRIVED") && holder != null && holder !== v.visit_id)
      out.set(v.visit_id, `запланированные ворота ${v.planned_dock} заняты визитом ${holder}`);
  }
  return out;
}

/** Очередь на ворота: машины на площадке по времени приезда. */
export function queue(visits: YardVisit[]): Map<number, number> {
  const waiting = visits.filter(v => v.state === "ARRIVED" && v.arrived_at).sort((a, b) => Date.parse(a.arrived_at!) - Date.parse(b.arrived_at!) || a.visit_id - b.visit_id);
  return new Map(waiting.map((v, i) => [v.visit_id, i + 1]));
}

const REFUSAL: Record<string, string> = {
  VERSION_CONFLICT: "Визит уже изменён другим пользователем. Обновите двор и повторите действие.",
  YARD_STATE_CONFLICT: "Действие не подходит текущему состоянию визита. Обновите двор.",
  YARD_DOCK_OR_VEHICLE_OCCUPIED: "Ворота или машина уже заняты другим визитом.", YARD_DOCK_OCCUPIED: "Ворота заняты другим визитом.",
  YARD_DOCK_BLOCKED: "Ворота заблокированы.", YARD_DOCK_UNKNOWN: "Таких ворот на складе нет.",
  YARD_TRIP_VISIT_ACTIVE: "У рейса уже есть активный визит.", YARD_VEHICLE_OCCUPIED: "Машина уже на площадке в другом визите.",
  YARD_VISIT_NOT_FOUND: "Визит не найден или недоступен.", YARD_TRIP_REQUIRED: "Рейс не найден или недоступен.", YARD_ACCESS_DENIED: "Нет права управлять двором на этом складе.",
};
export const refusalText = (code: string) => REFUSAL[code] ?? `Сервер отклонил действие (${code}). Обновите двор и проверьте данные.`;
