// MOCK: учебный набор для проверки UI-контракта C0074 до готовности /api/resources/timeline. Не реальные данные, только в preview-mock.
import type { ResourceTimeline, TimelineEvent } from "../timelineTypes";

const ev = (e: Partial<TimelineEvent> & Pick<TimelineEvent, "event_id" | "event_kind" | "title">): TimelineEvent => ({
  status: null, wave_id: null, task_id: null, trip_id: null, plan_start_at: null, plan_finish_at: null, fact_start_at: null, fact_finish_at: null,
  quantity: null, source: "mock", link: null, ...e });

export function mockTimeline(timeZone: string | null): ResourceTimeline {
  const shift = (start_at: string, finish_at: string | null, source = "mock.attendance") => ({ start_at, finish_at, state: "ON_SHIFT" as const, source, reason: null });
  return {
    warehouse: { warehouse_id: 1, name: "MOCK РЦ", time_zone: timeZone, time_zone_source: timeZone ? "mock" : null },
    window: { start_at: "2026-10-15T18:00:00+03:00", finish_at: "2026-10-16T08:00:00+03:00" },
    read_at: "2026-10-15T21:30:00+03:00",
    resources: [
      { resource_key: "REACH_TRUCK:1", resource_type: "REACH_TRUCK", resource_id: 1, code: "MOCK-RT-01", name: "Ричтрак 1", warehouse_id: 1, warehouse_name: "MOCK РЦ", zone_code: "HB",
        availability: [shift("2026-10-15T18:00:00+03:00", "2026-10-16T08:00:00+03:00")], last_signal: { state: "ACTIVE", observed_at: "2026-10-15T21:29:00+03:00", source: "mock.sessions", session_id: null },
        qualifications: ["REACH_TRUCK"], link: { page: "resources", params: { resource_id: 1 } } },
      { resource_key: "REACH_TRUCK:2", resource_type: "REACH_TRUCK", resource_id: 2, code: "MOCK-RT-02", name: null, warehouse_id: 1, warehouse_name: "MOCK РЦ", zone_code: "HB",
        availability: [{ start_at: "2026-10-15T18:00:00+03:00", finish_at: "2026-10-15T23:00:00+03:00", state: "DOWN", source: "mock.equipment", reason: "ремонт (учебный пример)" }],
        last_signal: null, qualifications: null, link: null },
      { resource_key: "REACH_TRUCK:3", resource_type: "REACH_TRUCK", resource_id: 3, code: "MOCK-RT-03", name: null, warehouse_id: 1, warehouse_name: "MOCK РЦ", zone_code: null,
        availability: [], last_signal: null, qualifications: null, link: null },
      { resource_key: "PICKER:11", resource_type: "PICKER", resource_id: 11, code: "MOCK-PK-01", name: "Комплектовщик 1", warehouse_id: 1, warehouse_name: "MOCK РЦ", zone_code: "PICK",
        availability: [shift("2026-10-15T20:00:00+03:00", "2026-10-16T08:00:00+03:00")], last_signal: { state: "ACTIVE", observed_at: "2026-10-15T21:28:00+03:00", source: "mock.sessions", session_id: null },
        qualifications: ["CASE_PICK"], link: null },
      { resource_key: "PICKER:12", resource_type: "PICKER", resource_id: 12, code: "MOCK-PK-02", name: null, warehouse_id: 1, warehouse_name: "MOCK РЦ", zone_code: "PICK",
        availability: [shift("2026-10-15T20:00:00+03:00", null, "mock.attendance-down")], last_signal: null, qualifications: ["CASE_PICK"], link: null },
      { resource_key: "DOCK:3", resource_type: "DOCK", resource_id: 3, code: "MOCK-D03", name: "Ворота 3", warehouse_id: 1, warehouse_name: "MOCK РЦ", zone_code: "SHIP",
        availability: [shift("2026-10-15T18:00:00+03:00", "2026-10-16T08:00:00+03:00", "mock.docks")], last_signal: null, qualifications: null, link: null },
      { resource_key: "DOCK:4", resource_type: "DOCK", resource_id: 4, code: "MOCK-D04", name: "Ворота 4", warehouse_id: 1, warehouse_name: "MOCK РЦ", zone_code: "SHIP",
        availability: [shift("2026-10-15T18:00:00+03:00", "2026-10-16T08:00:00+03:00", "mock.docks")], last_signal: null, qualifications: null, link: null },
      { resource_key: "VEHICLE:7", resource_type: "VEHICLE", resource_id: 7, code: "MOCK-A123", name: "Тент 20т", warehouse_id: 1, warehouse_name: "MOCK РЦ", zone_code: null,
        availability: [], last_signal: null, qualifications: null, link: null },
    ],
    events: [
      ev({ event_id: "REPL:1", event_kind: "REPLENISHMENT", title: "Пополнение P-1 (MOCK)", status: "IN_PROGRESS", wave_id: 900, task_id: 1,
        plan_start_at: "2026-10-15T19:00:00+03:00", plan_finish_at: "2026-10-15T20:00:00+03:00", fact_start_at: "2026-10-15T19:10:00+03:00", quantity: { value: "2", uom: "PAL" } }),
      ev({ event_id: "REPL:2", event_kind: "REPLENISHMENT", title: "Пополнение P-2 (MOCK)", status: "PLANNED", wave_id: 900, task_id: 2,
        plan_start_at: "2026-10-15T19:30:00+03:00", plan_finish_at: "2026-10-15T20:30:00+03:00", quantity: { value: "1", uom: "PAL" } }),
      // Время в UTC (Z): на оси склада это 22:00–02:00, через границу суток.
      ev({ event_id: "CASE:1040", event_kind: "CASE_PICK", title: "Сборка 1040 (MOCK)", status: "DONE", wave_id: 900, task_id: 1040,
        plan_start_at: "2026-10-15T19:00:00Z", plan_finish_at: "2026-10-15T23:00:00Z", fact_start_at: "2026-10-15T19:05:00Z", fact_finish_at: "2026-10-15T22:40:00Z", quantity: { value: "120", uom: "BOX" } }),
      ev({ event_id: "LOAD:33634", event_kind: "TRIP_OPERATION", title: "Погрузка рейса 33634 (MOCK)", status: "PLANNED", trip_id: 33634,
        plan_start_at: "2026-10-15T23:30:00+03:00", plan_finish_at: "2026-10-16T01:00:00+03:00", quantity: { value: "18", uom: "PAL" }, link: { page: "transport", params: { task_id: 33634 } } }),
      ev({ event_id: "TRANSIT:33634", event_kind: "TRIP_OPERATION", title: "В пути 33634 (MOCK)", status: "PLANNED", trip_id: 33634,
        plan_start_at: "2026-10-16T01:00:00+03:00", plan_finish_at: "2026-10-16T06:00:00+03:00", link: { page: "transport", params: { task_id: 33634 } } }),
      ev({ event_id: "ARRIVE:33640", event_kind: "TRIP_OPERATION", title: "Приезд 33640 (MOCK)", status: "PLANNED", trip_id: 33640, plan_start_at: "2026-10-16T03:00:00+03:00" }),
      // Старое Oracle-время без пояса: на оси только при подтверждённом поясе склада.
      ev({ event_id: "LEGACY:5", event_kind: "TRIP_OPERATION", title: "Выгрузка 33601 (MOCK, без пояса)", status: "PLANNED", trip_id: 33601,
        plan_start_at: "2026-10-15T20:00:00", plan_finish_at: "2026-10-15T20:40:00" }),
      ev({ event_id: "CASE:1052", event_kind: "CASE_PICK", title: "Сборка 1052 (MOCK)", status: "ASSIGNED", wave_id: 901, task_id: 1052, quantity: { value: "40", uom: "BOX" } }),
      ev({ event_id: "REPL:9", event_kind: "REPLENISHMENT", title: "Пополнение P-9 (MOCK)", status: "NEW", wave_id: 901, task_id: 9 }),
    ],
    bindings: [
      { binding_id: "b1", event_id: "REPL:1", resource_key: "REACH_TRUCK:1", role: "EQUIPMENT", basis: "PLAN", start_at: null, finish_at: null },
      { binding_id: "b1f", event_id: "REPL:1", resource_key: "REACH_TRUCK:1", role: "EQUIPMENT", basis: "FACT", start_at: null, finish_at: null },
      { binding_id: "b2", event_id: "REPL:2", resource_key: "REACH_TRUCK:1", role: "EQUIPMENT", basis: "PLAN", start_at: null, finish_at: null },
      { binding_id: "b3", event_id: "CASE:1040", resource_key: "PICKER:11", role: "EXECUTOR", basis: "PLAN", start_at: null, finish_at: null },
      { binding_id: "b3f", event_id: "CASE:1040", resource_key: "PICKER:11", role: "EXECUTOR", basis: "FACT", start_at: null, finish_at: null },
      { binding_id: "b4", event_id: "LOAD:33634", resource_key: "DOCK:3", role: "DOCK", basis: "PLAN", start_at: null, finish_at: null },
      { binding_id: "b5", event_id: "LOAD:33634", resource_key: "VEHICLE:7", role: "VEHICLE", basis: "PLAN", start_at: null, finish_at: null },
      { binding_id: "b6", event_id: "LOAD:33634", resource_key: "PICKER:11", role: "EXECUTOR", basis: "PLAN", start_at: null, finish_at: null },
      { binding_id: "b7", event_id: "TRANSIT:33634", resource_key: "VEHICLE:7", role: "VEHICLE", basis: "PLAN", start_at: null, finish_at: null },
      { binding_id: "b8", event_id: "ARRIVE:33640", resource_key: "DOCK:4", role: "DOCK", basis: "PLAN", start_at: null, finish_at: null },
      { binding_id: "b10", event_id: "LEGACY:5", resource_key: "DOCK:4", role: "DOCK", basis: "PLAN", start_at: null, finish_at: null },
      { binding_id: "b9", event_id: "CASE:1052", resource_key: "PICKER:12", role: "EXECUTOR", basis: "PLAN", start_at: null, finish_at: null },
    ],
    sources: [
      { source: "mock.sessions", title: "Сессии (MOCK)", status: "OK", read_at: "2026-10-15T21:30:00+03:00", row_count: 2, limit: 500, truncated: false, message: null },
      { source: "mock.attendance", title: "Табель (MOCK)", status: "OK", read_at: "2026-10-15T21:30:00+03:00", row_count: 3, limit: 500, truncated: false, message: null },
      { source: "mock.attendance-down", title: "Табель склада 2 (MOCK)", status: "ERROR", read_at: null, row_count: null, limit: null, truncated: false, message: "учебная ошибка источника" },
      { source: "mock.transport", title: "Рейсы (MOCK)", status: "OK", read_at: "2026-10-15T21:30:00+03:00", row_count: 200, limit: 200, truncated: true, message: null },
      { source: "mock.replenishment", title: "Пополнения (MOCK)", status: "NOT_MAPPED", read_at: null, row_count: null, limit: null, truncated: false, message: "учебный пример неподключённого источника" },
    ],
  };
}
