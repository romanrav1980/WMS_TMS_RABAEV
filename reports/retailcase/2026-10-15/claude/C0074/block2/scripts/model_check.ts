// C0074: проверка чистой модели и адаптера общего Ганта (приёмочные случаи TASK_C0074, замечания C-0078). Запуск: esbuild bundle + node.
import assert from "node:assert/strict";
import fs from "node:fs";
import { axisMinutes, buildRows, fmtAxis, nowAxis, stateNow, summarize, unscheduled } from "../../../../../../../admin/wms_admin_frontend/src/features/platform/workspaces/resources/timelineModel";
import { timelinePath, wallToAware } from "../../../../../../../admin/wms_admin_frontend/src/features/platform/workspaces/resources/useResourceTimeline";
import { TimelineShapeError, adaptTimeline } from "../../../../../../../admin/wms_admin_frontend/src/features/platform/workspaces/resources/timelineAdapter";
import { mockTimeline } from "../../../../../../../admin/wms_admin_frontend/src/features/platform/workspaces/resources/preview-mock/mockTimeline";
const out: Record<string, unknown> = {};
const t = mockTimeline("Europe/Moscow");
const rows = buildRows(t), row = (k: string) => rows.find(r => r.resource.resource_key === k)!;
// 1. Все 4 типа на одной шкале.
assert.deepEqual([...new Set(rows.map(r => r.resource.resource_type))].sort(), ["DOCK", "PICKER", "REACH_TRUCK", "VEHICLE"]);
// 2. UTC offset: 19:00Z = 22:00 по Москве; граница суток: окончание 02:00 следующего дня.
const pk = row("PICKER:11"), casePlan = pk.bars.find(b => b.event.event_id === "CASE:1040" && b.basis === "PLAN")!;
assert.equal(fmtAxis(casePlan.start, true), "15.10 22:00"); assert.equal(fmtAxis(casePlan.end, true), "16.10 02:00");
assert.equal(axisMinutes("2026-10-15T19:00:00Z", "Europe/Moscow"), axisMinutes("2026-10-15T22:00:00+03:00", "Europe/Moscow"));
// 3. Многоресурсная работа: один event_id, три привязки, количество не удваивается.
const load = rows.flatMap(r => r.bars.filter(b => b.event.event_id === "LOAD:33634").map(b => r.resource.resource_type));
assert.deepEqual(load.sort(), ["DOCK", "PICKER", "VEHICLE"]);
const s = summarize(t, rows); // события считаются по event_id
assert.equal(s.qty.get("PAL"), 21); // 2 + 1 + 18, погрузка один раз
out.summary = { ...s, qty: Object.fromEntries(s.qty) };
// 4. Пересечения подтверждённых интервалов (расчёт браузера только при отсутствии серверных кандидатов, как в MOCK).
assert.equal(row("REACH_TRUCK:1").conflicts, 2); assert.equal(pk.conflicts, 2); assert.equal(row("DOCK:3").conflicts, 0);
// 5. Незавершённый факт — до момента чтения, без выдуманного окончания; точка без окончания.
const open = row("REACH_TRUCK:1").bars.find(b => b.basis === "FACT")!; assert.ok(open.open && !open.point); assert.equal(fmtAxis(open.end), "21:30");
assert.ok(row("DOCK:4").bars.find(b => b.event.event_id === "ARRIVE:33640")!.point);
// 6. Неизвестное ≠ свободное.
const now = nowAxis(t)!; out.states = Object.fromEntries(rows.map(r => [r.resource.code, stateNow(r, now).label]));
assert.equal(stateNow(row("REACH_TRUCK:3"), now).tone, "unknown"); // нет данных о смене
assert.equal(stateNow(row("PICKER:12"), now).tone, "unknown");     // источник табеля не ответил
assert.equal(stateNow(row("REACH_TRUCK:2"), now).tone, "down");
assert.equal(stateNow(row("REACH_TRUCK:1"), now).tone, "busy");
assert.equal(stateNow(row("DOCK:3"), now).tone, "free");           // смена подтверждена, назначений на 21:30 нет
assert.equal(stateNow(row("VEHICLE:7"), now).tone, "unknown");
// 7. Очередь без времени / без ресурса / без пояса.
assert.deepEqual(unscheduled(t).map(q => q.event.event_id + ":" + q.reason).sort(), ["CASE:1052:NO_TIME", "LEGACY:5:NO_ZONE", "REPL:9:NO_RESOURCE"]);
// Старое время без offset не ставится на ось даже при известном поясе (C-0075/C-0078).
assert.ok(!row("DOCK:4").bars.some(b => b.event.event_id === "LEGACY:5"));
assert.equal(axisMinutes("2026-10-15T20:00:00", "Europe/Moscow"), null);
// 8. Неизвестный пояс РЦ: ось UTC (offset-эквивалентность), «сейчас» — реальный момент чтения на той же оси.
const u = mockTimeline(null), ur = buildRows(u);
assert.equal(axisMinutes("2026-10-15T19:00:00Z", null), axisMinutes("2026-10-15T22:00:00+03:00", null));
assert.equal(nowAxis(u), Date.parse("2026-10-15T18:30:00Z") / 60000);
assert.equal(fmtAxis(ur.find(r => r.resource.resource_key === "PICKER:11")!.bars.find(b => b.event.event_id === "CASE:1040" && b.basis === "PLAN")!.start), "19:00");
assert.ok(unscheduled(u).some(q => q.event.event_id === "LEGACY:5" && q.reason === "NO_ZONE"));
// 9. Запрос: только aware; при известном поясе — offset склада (не браузера), без пояса — UTC.
assert.equal(wallToAware("2026-10-15T18:00", "Europe/Moscow"), "2026-10-15T18:00:00+03:00");
assert.equal(wallToAware("2026-03-29T03:30", "Europe/Berlin"), "2026-03-29T03:30:00+02:00");
assert.match(timelinePath({ warehouseId: "1", startLocal: "2026-10-15T18:00", hours: 14 }, "Europe/Moscow")!, /start_at=2026-10-15T18%3A00%3A00%2B03%3A00&finish_at=2026-10-16T08%3A00%3A00%2B03%3A00/);
assert.match(timelinePath({ warehouseId: "1", startLocal: "2026-10-15T18:00", hours: 500 }, null)!, /start_at=2026-10-15T18%3A00%3A00%2B00%3A00&finish_at=2026-10-22T18%3A00%3A00%2B00%3A00/);
// 10. Адаптер: живой ответ API склада 1 (15.10.2026).
const live = adaptTimeline(JSON.parse(fs.readFileSync(__dirname + "/live_timeline_wh1.json", "utf8")));
const liveQueue = unscheduled(live);
out.live = { resources: live.resources.length, events: live.events.length, queue: liveQueue.length, reasons: [...new Set(liveQueue.map(q => q.reason))], sources: live.sources.map(x => x.source + ":" + x.status) };
assert.equal(live.warehouse.time_zone, null);
assert.ok(live.events.filter(e => e.time_status === "TIME_UNRESOLVED").every(e => liveQueue.some(q => q.event.event_id === e.event_id)));
assert.equal(buildRows(live).length, live.resources.length);
// 11. Адаптер: синтетический серверный ответ по RESOURCE_TIMELINE_API_V1.
const srv = { warehouse_id: 7, start_at: "2026-10-15T18:00:00+00:00", finish_at: "2026-10-16T06:00:00+00:00", observed_at: "2026-10-15T20:00:00+00:00", warehouse_time_zone: null,
  resources: [{ resource_id: "RESOURCE:1", kind: "CASE_PICKER", label: "Петров", warehouse_id: 7, source_state: "AVAILABLE", availability: "UNKNOWN", zone_code: "PICK",
      qualifications: [{ task_type: "CASE_PICK", current_by_native_policy: true, legacy_valid_until: "2026-12-31T00:00:00", time_status: "UNRESOLVED_SERVER_LOCAL" }],
      last_signal: { session_id: 5, aware_at: null, legacy_at: "2026-10-15T22:59:00", time_status: "UNRESOLVED_SERVER_LOCAL", recent_by_native_server_clock: true } },
    { resource_id: "EQUIPMENT:2", kind: "REACHTRUCK", label: "RT-2", warehouse_id: 7, source_state: "ACTIVE", availability: "UNKNOWN" },
    { resource_id: "DOCK:7:D1", kind: "DOCK", label: "D1", warehouse_id: 7, source_state: "BLOCKED", availability: "UNKNOWN" },
    { resource_id: "VEHICLE:A1", kind: "VEHICLE", label: "A1", warehouse_id: 7, source_state: null, availability: "UNKNOWN" },
    { resource_id: "RESOURCE:9", kind: "LOADING_TEAM", label: "Бригада", warehouse_id: 7, source_state: null, availability: "UNKNOWN" }],
  events: [
    { event_id: "ATTENDANCE:1", kind: "ATTENDANCE", label: "План выхода", source: "RRL_WORKLOAD_ATTENDANCE", source_id: "1", plan_start_at: "2026-10-15T18:00:00+00:00", plan_finish_at: "2026-10-16T02:00:00+00:00", fact_start_at: null, fact_finish_at: null, time_status: "AWARE_PLAN" },
    { event_id: "WAREHOUSE_TASK:5", kind: "WAREHOUSE_TASK", label: "REPLENISHMENT · 5", source: "RRL_WAREHOUSE_TASK", source_id: 5, status: "IN_PROGRESS", plan_start_at: null, plan_finish_at: null, fact_start_at: "2026-10-15T19:00:00+00:00", fact_finish_at: null, time_status: "AWARE_FACT", wave_id: 3, legacy_time: { plan_start: "2026-10-15T21:00:00" } },
    { event_id: "CASE_PICK_TASK:8", kind: "CASE_PICK_TASK", label: "Сборка 8 · волна 3", source: "RRL_CASE_PICK_TASK", source_id: 8, status: "WAIT_CONTROL", wave_id: 3, total_lines: 4, picked_lines: 4, plan_start_at: null, plan_finish_at: null, fact_start_at: "2026-10-15T18:30:00+00:00", fact_finish_at: null, time_status: "AWARE_FACT", fact_finish_status: "UNRESOLVED", legacy_time: { fact_finish: "2026-10-15T22:10:00" } }],
  unscheduled: [{ event_id: "TRANSPORT_OPERATION:4", kind: "TRANSPORT_OPERATION", label: "LOADING · рейс 77", source: "RRL_TT_OPERATIONS", source_id: 4, trip_id: 77, plan_start_at: null, plan_finish_at: null, fact_start_at: null, fact_finish_at: null, time_status: "TIME_UNRESOLVED", legacy_time: { plan_start: "2026-10-15T23:00:00" } }],
  assignments: [{ event_id: "ATTENDANCE:1", resource_id: "RESOURCE:1" }, { event_id: "WAREHOUSE_TASK:5", resource_id: "RESOURCE:1" }, { event_id: "WAREHOUSE_TASK:5", resource_id: "EQUIPMENT:2" },
    { event_id: "CASE_PICK_TASK:8", resource_id: "RESOURCE:1" }, { event_id: "TRANSPORT_OPERATION:4", resource_id: "VEHICLE:A1" }, { event_id: "TRANSPORT_OPERATION:4", resource_id: "DOCK:7:D1" }],
  sources: [{ source_id: "registry", status: "READY", permission: "resource_management_view", limit: 500, observed_at: "2026-10-15T20:00:00+00:00" },
    { source_id: "transport", status: "FORBIDDEN", permission: "transport_dispatch_view", limit: 2000, observed_at: null }],
  overlap_candidates: [{ resource_id: "RESOURCE:1", phase: "fact", event_ids: ["CASE_PICK_TASK:8", "WAREHOUSE_TASK:5"], status: "OVERLAP_REVIEW" }], overlap_limit: 200 };
const a = adaptTimeline(srv), ar = buildRows(a), arow = (k: string) => ar.find(r => r.resource.resource_key === k)!, anow = nowAxis(a);
assert.deepEqual(a.resources.map(r => r.resource_type), ["PICKER", "REACH_TRUCK", "DOCK", "VEHICLE", "OTHER"]);
assert.ok(!a.events.some(e => e.event_kind === "ATTENDANCE"));                      // план выхода — доступность, не работа
assert.equal(arow("RESOURCE:1").availability[0].a.state, "PLANNED");
assert.equal(a.events.filter(e => e.event_id === "WAREHOUSE_TASK:5").length, 1);     // одно событие на две полосы
assert.deepEqual(ar.filter(r => r.bars.some(b => b.event.event_id === "WAREHOUSE_TASK:5")).map(r => r.resource.resource_key), ["RESOURCE:1", "EQUIPMENT:2"]);
assert.ok(!arow("RESOURCE:1").bars.some(b => b.event.event_id === "WAREHOUSE_TASK:5" && b.basis === "PLAN")); // старый план без пояса — без плановой полосы
assert.ok(arow("RESOURCE:1").bars.find(b => b.event.event_id === "CASE_PICK_TASK:8")!.point); // завершённая сборка без окончания — точка
assert.equal(arow("RESOURCE:1").conflicts, 2);                                         // пересечение — от сервера
assert.equal(stateNow(arow("RESOURCE:1"), anow).tone, "busy");                         // открытый факт пополнения
assert.equal(stateNow(arow("EQUIPMENT:2"), anow).tone, "busy");
assert.equal(stateNow(arow("DOCK:7:D1"), anow).tone, "down");                          // BLOCKED в реестре
assert.equal(stateNow(arow("VEHICLE:A1"), anow).tone, "unknown");
assert.equal(stateNow(arow("RESOURCE:9"), anow).tone, "unknown");
assert.deepEqual(unscheduled(a).map(q => q.event.event_id + ":" + q.reason), ["TRANSPORT_OPERATION:4:NO_ZONE"]);
assert.equal(a.sources.find(x => x.source === "transport")!.status, "NO_ACCESS");
assert.throws(() => adaptTimeline({ warehouse_id: 7, resources: [] }), TimelineShapeError); // неизвестная форма — ошибка, не пустой Гант
assert.throws(() => adaptTimeline({ ...srv, events: null }), TimelineShapeError);
// C-0089: зона, допуски, сигнал; null — не прочитано, [] — нет допусков; время сигнала без пояса не на оси.
const r1 = a.resources[0]; assert.equal(r1.zone_code, "PICK"); assert.deepEqual(r1.qualifications, ["CASE_PICK до 2026-12-31 00:00 (без пояса)"]);
assert.match(r1.last_signal!.state, /свежий/); assert.equal(a.resources[1].qualifications, null);
// План выхода без задач — «без назначений (план)», не «свободен».
const idle = adaptTimeline({ ...srv, events: [srv.events[0]], unscheduled: [], assignments: [srv.assignments[0]], overlap_candidates: [] });
assert.equal(stateNow(buildRows(idle)[0], nowAxis(idle)).tone, "plan");
console.log(JSON.stringify(out, null, 1)); console.log("MODEL CHECK PASS");
