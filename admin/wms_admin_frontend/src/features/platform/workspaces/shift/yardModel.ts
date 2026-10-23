// Двор склада (C-0149): визиты машин из GET /api/tradecase/warehouses/{id}/yard/visits. Опоздание и ожидание — по часам
// сервера (observed_at снимка), не браузера. Визиты скрытых владельцев сервер не отдаёт вовсе.

export type YardState = "EXPECTED" | "ARRIVED" | "AT_DOCK" | "WORKING" | "WORK_DONE" | "DEPARTED" | "CANCELLED";
export type YardAction = "ARRIVE" | "ASSIGN_DOCK" | "REASSIGN_DOCK" | "START" | "FINISH" | "DEPART" | "CANCEL";
export type YardVisit = { visit_id: number; warehouse_id: number; trip_id: string | null; vehicle: string | null; dock: string | null;
  visit_kind?: "OUTBOUND" | "INBOUND"; supply_ids?: string[];
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
  if (!v.vehicle) out.push(v.visit_kind === "INBOUND" ? "не указан номер машины" : "машина в рейсе не указана");
  if (v.state === "EXPECTED" && !v.planned_arrival_at) out.push("нет плана приезда — опоздание не определяется");
  if (v.visit_kind !== "INBOUND" && (v.state === "EXPECTED" || v.state === "ARRIVED") && !v.planned_dock) out.push("ворота в рейсе не запланированы");
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
  YARD_VISIT_NOT_FOUND: "Визит не найден или недоступен.", YARD_OPERATION_CONFLICT: "Этот номер операции уже использован другим действием или пользователем.",
  YARD_TRIP_BINDING_REQUIRED: "Рейс не привязан к транспортному заданию — приезд не подтверждается.",
  YARD_VEHICLE_REQUIRED: "Укажите машину перед регистрацией приезда.", YARD_TRIP_REQUIRED: "Рейс не найден или недоступен.", YARD_ACCESS_DENIED: "Нет права управлять двором на этом складе.",
  YARD_SUPPLIES_REQUIRED: "Укажите основания поставки.", YARD_SUPPLY_NOT_FOUND: "Основание поставки не получено или недоступно.",
  YARD_SUPPLY_VISIT_ACTIVE: "Основание поставки уже назначено активному визиту.",
  YARD_SUPPLY_CHANGED: "Основание поставки изменилось. Отмените ожидание и создайте визит по актуальным данным.",
};
export const refusalText = (code: string) => REFUSAL[code] ?? `Сервер отклонил действие (${code}). Обновите двор и проверьте данные.`;

// Плановые интервалы ворот (C-0158): GET …/yard/dock-plans?from&to. План — не факт и не гарантия свободных ворот; факты визита
// приходят рядом с планом и никогда из него не выводятся. Автоматического пересчёта плана при задержке нет.
export type DockPlan = { plan_id: number; warehouse_id: number; visit_id: number; dock: string; planned_from: string; planned_to: string;
  status: "ACTIVE"; version: number; visit_kind: "OUTBOUND" | "INBOUND"; trip_id: string | null; vehicle: string | null; visit_state: YardState;
  fact_dock: string | null; arrived_at: string | null; docked_at: string | null; work_started_at: string | null; departed_at: string | null };
export type DockPlans = { warehouse_id: number; observed_at: string; plans: DockPlan[] };
export const PLANNABLE = new Set<YardState>(["EXPECTED", "ARRIVED"]);  // как native: план ставится и переносится до постановки к воротам

export function parsePlans(raw: unknown, warehouse: number): DockPlans {
  const s = raw as DockPlans;
  const ok = s && typeof s === "object" && s.warehouse_id === warehouse && typeof s.observed_at === "string" && Array.isArray(s.plans)
    && s.plans.every(p => p && typeof p.plan_id === "number" && p.warehouse_id === warehouse && typeof p.version === "number" && STATES.has(p.visit_state)
      && typeof p.dock === "string" && !Number.isNaN(Date.parse(p.planned_from)) && Date.parse(p.planned_to) > Date.parse(p.planned_from));
  if (!ok) throw new YardShapeError("Неожиданный ответ плана ворот");
  return s;
}

/** Отклонения от плана только по фактам визита и часам сервера; пустой список — отклонений по имеющимся данным нет. */
export function planDeviation(p: DockPlan, observedAt: string, visits: YardVisit[]): string[] {
  const out: string[] = [], late = minutes(p.planned_from, observedAt);
  if (p.visit_state === "EXPECTED" && late > 0) out.push(`машина не приехала, план начала прошёл ${late} мин назад`);
  if (p.visit_state === "ARRIVED" && late > 0) out.push(`машина на площадке, к воротам не поставлена; план начала прошёл ${late} мин назад`);
  if (p.docked_at && p.fact_dock === p.dock && minutes(p.planned_from, p.docked_at) > 0) out.push(`встала к воротам на ${minutes(p.planned_from, p.docked_at)} мин позже плана`);
  if (p.fact_dock && p.fact_dock !== p.dock) out.push(`фактически стоит у ворот ${p.fact_dock}`);
  if (["AT_DOCK", "WORKING", "WORK_DONE"].includes(p.visit_state) && p.fact_dock === p.dock && minutes(p.planned_to, observedAt) > 0)
    out.push(`занимает ворота дольше плана на ${minutes(p.planned_to, observedAt)} мин`);
  const holder = visits.find(v => v.dock === p.dock && v.visit_id !== p.visit_id && ["AT_DOCK", "WORKING", "WORK_DONE"].includes(v.state));
  if (holder && late > -60) out.push(`ворота сейчас занимает визит ${holder.visit_id}`);
  return out;
}

const PLAN_REFUSAL: Record<string, string> = {
  YARD_DOCK_PLAN_CONFLICT: "На эти ворота уже запланирована другая машина на пересекающееся время.",
  YARD_VEHICLE_PLAN_CONFLICT: "Эта машина уже запланирована на пересекающееся время (возможно, на другом складе).",
  YARD_PLAN_EXISTS: "У визита уже есть план ворот — перенесите его.", YARD_PLAN_IN_PAST: "Начало плана уже прошло. Планируются только будущие интервалы.",
  YARD_PLAN_RANGE_INVALID: "Конец плана должен быть позже начала.", YARD_PLAN_VISIT_STATE: "Машина уже у ворот или визит закрыт — план не меняется, действуют факты двора.",
  YARD_PLAN_STATE_CONFLICT: "План уже отменён.", YARD_PLAN_NOT_FOUND: "План не найден или недоступен.", YARD_PLAN_TIME_INVALID: "Время плана не распознано.",
  YARD_PLAN_REASON_REQUIRED: "Укажите причину отмены плана.", YARD_PLAN_BUSY: "Машину сейчас планирует другой сотрудник. Повторите.",
  YARD_PLAN_NOT_AVAILABLE: "План ворот на сервере ещё не включён.",
};
export const planRefusalText = (code: string) => PLAN_REFUSAL[code] ?? refusalText(code);
