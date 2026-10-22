import type { Availability, BindingRole, ObjectLink, ResourceTimeline, ResourceType, SourceStatus, TimelineBinding, TimelineEvent, TimelineResource } from "./timelineTypes";

// Адаптер ответа GET /api/resources/timeline (RESOURCE_TIMELINE_API_V1, Codex) к UI-модели Ганта.
// Неизвестная форма ответа — ошибка, а не пустой Гант. ATTENDANCE — план выхода (доступность), не занятость.

type ServerEvent = { event_id: string; kind: string; label: string; source: string; source_id: string | number;
  plan_start_at: string | null; plan_finish_at: string | null; fact_start_at: string | null; fact_finish_at: string | null; time_status: string;
  status?: string | null; trip_id?: number | null; wave_id?: number | null; task_source?: string | null; source_task_id?: number | null;
  total_lines?: number | null; picked_lines?: number | null; legacy_time?: Record<string, string | null> | null; blocking_reason?: string | null; fact_finish_status?: string;
  approval_status?: string | null };
type ServerQualification = { source_resource_id?: number; task_type: string; current_by_native_policy?: boolean; legacy_valid_from?: string | null; legacy_valid_until?: string | null; time_status?: string };
type ServerSignal = { session_id: number; aware_at: string | null; legacy_at: string | null; time_status: string; recent_by_native_server_clock: boolean };
type ServerResource = { resource_id: string; kind: string; label: string | null; warehouse_id: number; source_state: string | null; availability: string;
  zone_code?: string | null; qualifications?: ServerQualification[] | null; last_signal?: ServerSignal | null };
export type ServerTimeline = { warehouse_id: number; start_at: string; finish_at: string; observed_at: string; access_revision?: number;
  warehouse_time_zone: string | null; resources: ServerResource[]; events: ServerEvent[]; unscheduled: ServerEvent[];
  assignments: { event_id: string; resource_id: string }[]; sources: { source_id: string; status: string; permission: string; limit: number | null; observed_at: string | null }[];
  overlap_candidates: { resource_id: string; phase: string; event_ids: string[]; status: string }[]; overlap_limit?: number; time_policy?: string; commands_executed?: boolean };

export class TimelineShapeError extends Error {}

const KIND: Record<string, ResourceType> = { CASE_PICKER: "PICKER", REACHTRUCK: "REACH_TRUCK", REACH_TRUCK: "REACH_TRUCK", DOCK: "DOCK", VEHICLE: "VEHICLE" };
const ROLE: Record<ResourceType, BindingRole> = { PICKER: "EXECUTOR", REACH_TRUCK: "EQUIPMENT", DOCK: "DOCK", VEHICLE: "VEHICLE", OTHER: "EXECUTOR" };
// Статусы, после которых работа не продолжается; без окончания у источника — точка, а не занятость до «сейчас» (как в overlap сервера).
const TERMINAL = new Set(["DONE", "CANCELLED", "SHIPPED", "READY_TO_SHIP", "CONTROLLED", "WAIT_CONTROL", "CONTROL_IN_PROGRESS", "PICKED", "CLOSED"]);
const TIME: Record<string, string> = { AWARE_FACT: "факт с часовым поясом", AWARE_PLAN: "план с часовым поясом", AWARE_APPROVED: "утверждённый план с часовым поясом",
  AWARE_TIME_SCHEDULE: "расписание с часовым поясом", TIME_UNRESOLVED: "время источника без часового пояса — на шкалу не ставится" };
const APPROVAL: Record<string, string> = { APPROVED: "утверждено", SOURCE_CHANGED: "источник изменился после утверждения — время не подтверждено", NOT_APPROVED: "не утверждено" };
const SOURCE_TITLE: Record<string, string> = { sessions: "Сессии", registry: "Реестр ресурсов", attendance: "План выхода", warehouse_tasks: "Складские задания", case_tasks: "Сборка", transport: "Рейсы и ворота", yard: "Двор (визиты)" };

function assertShape(cond: unknown, what: string): asserts cond { if (!cond) throw new TimelineShapeError("Неожиданный ответ API ресурсов: " + what); }
const isArr = Array.isArray;

function linkOf(e: ServerEvent): ObjectLink {
  if ((e.kind === "LOAD_CONFIRMATION" || e.kind === "TRIP_DEPARTURE") && e.trip_id != null)
    return { page: "transport-loading.html", params: { trip_id: e.trip_id } };
  if (e.kind === "TRANSPORT_OPERATION" && e.trip_id != null) return { page: "transport", params: { task_id: e.trip_id } };
  if (e.kind === "CASE_PICK_TASK") return { page: "case-pick-management.html" };
  if (e.kind === "WAREHOUSE_TASK") return { page: "warehouse-tasks.html" };
  return null;
}

function eventOf(e: ServerEvent): TimelineEvent {
  assertShape(typeof e.event_id === "string" && typeof e.kind === "string", "событие без event_id/kind");
  const details: [string, string][] = [["Время", TIME[e.time_status] ?? "состояние не распознано"]];
  if (e.total_lines != null) details.push(["Строки сборки", `${e.picked_lines ?? "?"} из ${e.total_lines}`]); // строки разных SKU — не единицы товара
  if (e.task_source) details.push(["Источник задания", `${e.task_source}${e.source_task_id != null ? " · " + e.source_task_id : ""}`]);
  if (e.blocking_reason) details.push(["Блокировка", e.blocking_reason]);
  if (e.fact_finish_status === "UNRESOLVED") details.push(["Окончание факта", "не известно у источника"]);
  if (e.kind === "YARD_VISIT" || e.kind === "YARD_DOCK") details.push(["Окончание", !e.fact_start_at ? "визит не начат" : e.fact_finish_at ? "закрыто фактом визита"
    : e.kind === "YARD_DOCK" ? "открыто до смены ворот или выезда — ворота заняты" : "открыто до выезда — машина на площадке"]);
  if (e.approval_status) details.push(["Утверждение времени", APPROVAL[e.approval_status] ?? "состояние не распознано"]);
  return { event_id: e.event_id, event_kind: e.kind, title: e.label, status: e.status ?? null, wave_id: e.wave_id ?? null,
    task_id: e.kind === "LOAD_CONFIRMATION" || e.kind === "TRIP_DEPARTURE" || e.kind.startsWith("YARD_") ? null : e.source_id, trip_id: e.trip_id ?? null,
    plan_start_at: e.plan_start_at, plan_finish_at: e.plan_finish_at, fact_start_at: e.fact_start_at, fact_finish_at: e.fact_finish_at,
    quantity: null, source: e.source, link: linkOf(e), finish_unresolved: e.fact_finish_status === "UNRESOLVED",
    terminal: e.status != null && TERMINAL.has(e.status), legacy_time: e.legacy_time ?? null, time_status: e.time_status, details };
}

/** Серверный ответ → UI-модель. Бросает TimelineShapeError при неполной форме. */
export function adaptTimeline(raw: unknown): ResourceTimeline {
  const t = raw as ServerTimeline;
  assertShape(t && typeof t === "object", "не объект");
  assertShape(typeof t.warehouse_id === "number" && typeof t.start_at === "string" && typeof t.finish_at === "string" && typeof t.observed_at === "string", "нет склада/окна/observed_at");
  assertShape(isArr(t.resources) && isArr(t.events) && isArr(t.unscheduled) && isArr(t.assignments) && isArr(t.sources) && isArr(t.overlap_candidates), "нет обязательных списков");
  const all = [...t.events, ...t.unscheduled];
  const attendance = all.filter(e => e.kind === "ATTENDANCE"), work = all.filter(e => e.kind !== "ATTENDANCE");
  const seen = new Set<string>(); const events: TimelineEvent[] = [];
  for (const e of work) if (!seen.has(e.event_id)) { seen.add(e.event_id); events.push(eventOf(e)); } // одно событие — один раз
  const availability = new Map<string, Availability[]>();
  const attendanceIds = new Map(attendance.map(e => [e.event_id, e]));
  const types = new Map<string, ResourceType>();
  const resources: TimelineResource[] = t.resources.map(r => {
    assertShape(typeof r.resource_id === "string" && typeof r.kind === "string", "ресурс без resource_id/kind");
    const type = KIND[r.kind] ?? "OTHER"; types.set(r.resource_id, type);
    return { resource_key: r.resource_id, resource_type: type, resource_id: r.resource_id, code: r.label || r.resource_id, name: null,
      warehouse_id: r.warehouse_id, zone_code: r.zone_code ?? null, kind_raw: r.kind, source_state: r.source_state, availability: [], link: null,
      // null — источник не прочитан/неприменим; [] — текущих допусков нет. Допуск не равен доступности (C-0089).
      qualifications: r.qualifications == null ? null : r.qualifications.map(q => q.task_type + (q.legacy_valid_until ? ` до ${q.legacy_valid_until.replace("T", " ").slice(0, 16)} (без пояса)` : "")),
      // Сигнал сессии: свежесть — только по часам сервера (≤5 мин), это не занятость и не план; время без пояса на ось не ставится.
      last_signal: r.last_signal ? { state: r.last_signal.recent_by_native_server_clock ? "сигнал свежий (≤5 мин по часам сервера)" : "сигнал старше 5 мин",
        observed_at: r.last_signal.aware_at ?? r.last_signal.legacy_at ?? "", source: `сессия ${r.last_signal.session_id}`, session_id: r.last_signal.session_id } : null };
  });
  const bindings: TimelineBinding[] = [];
  const byId = new Map(events.map(e => [e.event_id, e]));
  for (const a of t.assignments) {
    const att = attendanceIds.get(a.event_id);
    if (att) {
      if (att.plan_start_at) (availability.get(a.resource_id) ?? availability.set(a.resource_id, []).get(a.resource_id)!)
        .push({ start_at: att.plan_start_at, finish_at: att.plan_finish_at, state: "PLANNED", source: "attendance", reason: att.label });
      continue;
    }
    const e = byId.get(a.event_id); if (!e) continue;
    const role = ROLE[types.get(a.resource_id) ?? "OTHER"];
    // Привязка по основаниям, у которых есть aware время; без времени — одна плановая привязка (работа уйдёт в очередь).
    const bases: ("PLAN" | "FACT")[] = [...(e.plan_start_at ? ["PLAN" as const] : []), ...(e.fact_start_at ? ["FACT" as const] : [])];
    for (const basis of bases.length ? bases : ["PLAN" as const])
      bindings.push({ binding_id: `${a.event_id}|${a.resource_id}|${basis}`, event_id: a.event_id, resource_key: a.resource_id, role, basis, start_at: null, finish_at: null });
  }
  for (const r of resources) r.availability = availability.get(r.resource_key) ?? [];
  return {
    warehouse: { warehouse_id: t.warehouse_id, name: null, time_zone: t.warehouse_time_zone, time_zone_source: null },
    window: { start_at: t.start_at, finish_at: t.finish_at }, read_at: t.observed_at,
    resources, events, bindings,
    sources: t.sources.map(s => ({ source: s.source_id, title: SOURCE_TITLE[s.source_id] ?? s.source_id, status: (s.status === "READY" ? "OK" : s.status === "FORBIDDEN" ? "NO_ACCESS" : s.status === "NOT_MAPPED" ? "NOT_MAPPED" : "ERROR") as SourceStatus,
      read_at: s.observed_at, row_count: null, limit: s.limit, truncated: false, message: s.status === "FORBIDDEN" ? `нет права ${s.permission} на этот склад` : null })),
    overlaps: t.overlap_candidates.map(o => ({ resource_key: o.resource_id, basis: o.phase === "fact" ? "FACT" as const : "PLAN" as const, event_ids: o.event_ids })),
    overlap_limit: t.overlap_limit,
  };
}
