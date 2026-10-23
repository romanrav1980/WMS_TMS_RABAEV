// C-0142: модульные проверки моделей старшего смены и общего Ганта (без сети). Формы данных — как в живых ответах 22.10
// (склад 220793322 волна 613/CASE1169 CONTROLLED; склад 9807 рейс 33564: операции назначены машине, время без пояса).
const assert = require("node:assert/strict"), fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const root = "C:/projects/TMS", ts = require(path.join(root, "admin/wms_admin_frontend/node_modules/typescript"));
const base = path.join(root, "admin/wms_admin_frontend/src/features/platform/workspaces"), cache = {};
// useShiftData тянет сетевой api — подставляется только его константа лимитов (как в коде: caseTasks 200).
const STUB = { react: { useMemo: f => f() }, "./useShiftData": { SHIFT_LIMITS: { future: 50, launched: 100, caseTasks: 200 } } };
function load(rel) {
  if (cache[rel]) return cache[rel];
  const exports = {}; cache[rel] = exports;
  const js = ts.transpileModule(fs.readFileSync(path.join(base, rel), "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  const dir = path.dirname(rel);
  vm.runInNewContext(js, { exports, Set, Map, Date, Intl, Number, Object, require: id => STUB[id] ?? (id.startsWith(".") && fs.existsSync(path.join(base, dir, id + ".ts")) ? load(path.join(dir, id + ".ts").replace(/\\/g, "/")) : {}) });
  return exports;
}
const state = load("shift/executionState.ts"), flow = load("shift/WaveFlowScene.tsx"), risk = load("shift/risks.ts"), hook = load("shift/useShiftRisks.ts");
const model = load("resources/timelineModel.ts"), adapter = load("resources/timelineAdapter.ts");
const out = []; const check = (name, run) => { run(); out.push(name); console.log("PASS", name); };
const complete = () => ({ wave_id: 613, readiness: { data: { blockers: [] }, error: "" }, pick: { data: { released_at: "2026-10-21T21:29:37-04:00", tasks: [] }, error: "" }, time: { data: { plan_status: "NO_APPROVED_PLAN" }, error: "" }, replenishment: { data: [], error: "" } });

check("actual CASE stage: open → PICKING, closed → AWAITING_SHIPMENT, all shipped → SHIPPED, unknown → null", () => {
  assert.equal(state.caseStage(["CONTROLLED"]), "AWAITING_SHIPMENT");
  assert.equal(state.caseStage(["SHIPPED", "SHIPPED"]), "SHIPPED");
  assert.equal(state.caseStage(["SHIPPED", "READY_TO_SHIP"]), "AWAITING_SHIPMENT");
  assert.equal(state.caseStage(["PICKED", "SHIPPED"]), "PICKING");
  assert.equal(state.caseStage(["CANCELLED"]), null);
  assert.equal(state.caseStage(["SOMETHING_NEW", "SHIPPED"]), null);
  assert.equal(state.caseStage([]), null);
});
check("wave 613 after real picking is not static CLEAR: CONTROLLED → PACKED; all SHIPPED → SHIPPED", () => {
  assert.equal(flow.stageOf({ status: "LAUNCHED" }, complete(), ["CONTROLLED"]), "PACKED");
  assert.equal(flow.stageOf({ status: "LAUNCHED" }, complete(), ["SHIPPED"]), "SHIPPED");
  assert.equal(flow.stageOf({ status: "LAUNCHED" }, complete()), "CLEAR");
});
check("blockers outrank case facts; open CASE without blocker still PICK; DONE stays ARCHIVE; PREVIEW stays PREP", () => {
  const d = complete(); d.readiness.data.blockers = [{ blocker_type: "SHORTAGE" }];
  assert.equal(flow.stageOf({ status: "LAUNCHED" }, d, ["CONTROLLED"]), "STAGE");
  assert.equal(flow.stageOf({ status: "LAUNCHED" }, complete(), ["IN_PROGRESS", "CONTROLLED"]), "PICK");
  assert.equal(flow.stageOf({ status: "DONE" }, complete(), ["SHIPPED"]), "ARCHIVE");
  assert.equal(flow.stageOf({ status: "PREVIEW" }, undefined, ["NEW"]), "PREP");
});
check("unread preparation uses case fact if known, otherwise UNREAD (never CLEAR)", () => {
  assert.equal(flow.stageOf({ status: "LAUNCHED" }, undefined, ["SHIPPED"]), "SHIPPED");
  assert.equal(flow.stageOf({ status: "LAUNCHED" }, undefined, []), "UNREAD");
  assert.equal(flow.stageOf({ status: "LAUNCHED" }, undefined), "UNREAD");
});
check("risk actions never loop back to the shift workplace itself", () => {
  const d = complete(); d.readiness.data.blockers = [{ blocker_type: "NEW_KIND", status: null, count: 1, message: "x" }]; d.pick.data.released_at = null; d.time.error = "нет права";
  const list = risk.waveRisks({ pick_wave_id: 613, status: "LAUNCHED" }, d);
  assert.ok(list.length >= 3);
  assert.ok(list.every(r => r.action == null || r.action.page !== "shift-supervisor-wave.html"), JSON.stringify(list.map(r => r.action)));
});

check("cancelled replenishment with its cancel reason is not a 'waiting' risk (live wave 613 row 1673)", () => {
  const d = complete(); d.replenishment.data = [{ pick_wave_replenish_task_id: 1673, status: "CANCELLED", wait_reason: "Existing usable own target coverage satisfies this CASE task", articul: "TC03" },
    { pick_wave_replenish_task_id: 1674, status: "NEW", wait_reason: "Нет свободного ричтрака", articul: "TC04" }];
  const keys = risk.waveRisks({ pick_wave_id: 613, status: "LAUNCHED" }, d).filter(r => r.key.includes(":P:")).map(r => r.key);
  assert.equal(keys.length, 1); assert.equal(keys[0], "613:P:1674");
  assert.equal(state.isOpenReplenishment("CANCELLED"), false); assert.equal(state.isOpenReplenishment("DONE"), false); assert.equal(state.isOpenReplenishment("IN_PROGRESS"), true);
});
const rs = (o = {}) => ({ data: [], error: "", loading: false, at: new Date(), ...o });
const shiftData = o => ({ future: rs(), launched: rs(), caseTasks: rs(), sessions: rs(), shorts: rs(), ...o });
const cov = { requested: 1, read: 1, batches: 1, failed: 0, observed: [], error: "" };
check("failed sources and unread waves are gaps, not 'no risk'", () => {
  const waves = [{ pick_wave_id: 613, status: "LAUNCHED" }];
  const ok = hook.useShiftRisks(waves, new Map([[613, complete()]]), shiftData(), cov, false);
  assert.equal(ok.gaps.length, 0, ok.gaps.join(" | "));
  const bad = hook.useShiftRisks(waves, new Map(), shiftData({ caseTasks: rs({ data: null, error: "Нет права просмотра." }), shorts: rs({ data: null, loading: true }) }), { ...cov, read: 0, failed: 1, error: "HTTP 503" }, false);
  assert.equal(bad.risks.length, 0);
  assert.ok(bad.gaps.some(g => g.startsWith("сборка: Нет права")) && bad.gaps.some(g => g.startsWith("недостачи: ещё читаются")) && bad.gaps.some(g => g.includes("подробно не проверено волн: 1 — HTTP 503")), bad.gaps.join(" | "));
});
check("closed waves without details are not gaps; truncated CASE list disables per-wave stage", () => {
  const r = hook.useShiftRisks([{ pick_wave_id: 604, status: "DONE" }], new Map(), shiftData(), cov, false);
  assert.equal(r.gaps.length, 0, r.gaps.join(" | "));
  const many = Array.from({ length: 200 }, (_, i) => ({ case_pick_task_id: i, pick_wave_id: 613, status: "SHIPPED" }));
  const t = hook.useShiftRisks([], new Map(), shiftData({ caseTasks: rs({ data: many }) }), cov, false);
  assert.equal(t.cases.size, 0); assert.ok(t.gaps.some(g => g.includes("первые 200")));
  const s = hook.useShiftRisks([], new Map(), shiftData({ caseTasks: rs({ data: [{ pick_wave_id: 613, status: "CONTROLLED" }, { pick_wave_id: 612, status: "SHIPPED" }] }) }), cov, false);
  assert.deepEqual([...s.cases.get(613)], ["CONTROLLED"]);
});

// Форма живого ответа склада 9807 (22.10): операции рейса назначены машине, времени с поясом нет.
const live9807 = { warehouse_id: 9807, start_at: "2026-10-14T21:00:00+00:00", finish_at: "2026-10-21T21:00:00+00:00", observed_at: "2026-10-22T05:20:00+00:00", warehouse_time_zone: null,
  resources: [{ resource_id: "DOCK:9807:B01", kind: "DOCK", label: "B01", warehouse_id: 9807, source_state: "UNKNOWN", availability: "UNKNOWN" },
    { resource_id: "VEHICLE:QC241", kind: "VEHICLE", label: "QC241", warehouse_id: 9807, source_state: null, availability: "UNKNOWN" }],
  events: [], unscheduled: ["DOCK_ASSIGN", "WAIT_LOAD"].map((op, i) => ({ event_id: "TRANSPORT_OPERATION:1016" + i, kind: "TRANSPORT_OPERATION", label: op + " · рейс 33564", source: "RRL_TT_OPERATIONS", source_id: 10160 + i, trip_id: 33564,
    plan_start_at: null, plan_finish_at: null, fact_start_at: null, fact_finish_at: null, time_status: "TIME_UNRESOLVED", approval_status: "SOURCE_CHANGED", legacy_time: { plan_start: "2026-10-14T00:00:00", plan_finish: "2026-10-14T00:15:00" } })),
  assignments: [{ event_id: "TRANSPORT_OPERATION:10160", resource_id: "VEHICLE:QC241" }, { event_id: "TRANSPORT_OPERATION:10161", resource_id: "VEHICLE:QC241" }], sources: [], overlap_candidates: [] };
check("assigned work without aware time stays attached to its resource (not 'no assignments'/'no resource')", () => {
  const t = adapter.adaptTimeline(live9807), rows = model.buildRows(t), veh = rows.find(r => r.resource.resource_type === "VEHICLE"), dock = rows.find(r => r.resource.resource_type === "DOCK");
  assert.equal(veh.bars.length, 0); assert.equal(veh.untimed.length, 2); assert.equal(dock.untimed.length, 0);
  assert.deepEqual(Array.from(model.unscheduled(t), q => q.reason), ["NO_ZONE", "NO_ZONE"]);
  const st = model.stateNow(veh, model.nowAxis(t)); assert.equal(st.tone, "unknown");
});
check("search and exact wave filter see untimed assignments", () => {
  const t = adapter.adaptTimeline(live9807), rows = model.buildRows(t), F = { types: new Set(["DOCK", "VEHICLE"]), query: "33564", groupBy: "type", onlyConflicts: false, waveId: null, waveLabel: null };
  assert.deepEqual([...model.groupRows(rows, F, x => x).flatMap(g => g.rows.map(r => r.resource.resource_type))], ["VEHICLE"]);
  t.events.forEach(e => { e.wave_id = 77; });
  assert.equal(model.groupRows(model.buildRows(t), { ...F, query: "", waveId: 77 }, x => x).flatMap(g => g.rows).length, 1);
});
check("event card details are plain language: time status and approval", () => {
  const e = adapter.adaptTimeline(live9807).events[0], d = Object.fromEntries(e.details);
  assert.match(d["Время"], /без часового пояса/); assert.match(d["Утверждение времени"], /источник изменился/);
  assert.ok(!Object.values(d).some(v => /TIME_UNRESOLVED|SOURCE_CHANGED/.test(v)));
});
check("one event on dock + vehicle + picker: three bars, counted once, conflict from server candidates only on the shared dock", () => {
  const ev = (id, s, f) => ({ event_id: id, kind: "TRANSPORT_OPERATION", label: id, source: "RRL_TT_OPERATIONS", source_id: 1, trip_id: 5, plan_start_at: s, plan_finish_at: f, fact_start_at: null, fact_finish_at: null, time_status: "AWARE_PLAN" });
  const t = adapter.adaptTimeline({ ...live9807, resources: [...live9807.resources, { resource_id: "RESOURCE:1", kind: "CASE_PICKER", label: "P1", warehouse_id: 9807, source_state: "AVAILABLE", availability: "UNKNOWN" }],
    unscheduled: [], events: [ev("LOAD", "2026-10-20T10:00:00+00:00", "2026-10-20T11:00:00+00:00"), ev("NEXT", "2026-10-20T10:30:00+00:00", "2026-10-20T11:30:00+00:00")],
    assignments: [["LOAD", "DOCK:9807:B01"], ["LOAD", "VEHICLE:QC241"], ["LOAD", "RESOURCE:1"], ["NEXT", "DOCK:9807:B01"]].map(([event_id, resource_id]) => ({ event_id, resource_id })),
    overlap_candidates: [{ resource_id: "DOCK:9807:B01", phase: "plan", event_ids: ["LOAD", "NEXT"], status: "REVIEW" }] }); // пересечения считает сервер
  const rows = model.buildRows(t), load = rows.flatMap(r => r.bars.filter(b => b.event.event_id === "LOAD"));
  assert.equal(load.length, 3); assert.deepEqual([...load.map(b => b.binding.role)].sort(), ["DOCK", "EXECUTOR", "VEHICLE"]);
  assert.equal(model.summarize(t, rows).events, 2);
  assert.equal(rows.find(r => r.resource.resource_type === "DOCK").conflicts, 2); assert.equal(rows.find(r => r.resource.resource_type === "VEHICLE").conflicts, 0);
});
fs.writeFileSync(path.join(__dirname, "..", "c0142-model.json"), JSON.stringify({ checks: out, count: out.length, network: false }, null, 1));
console.log(out.length + " C0142 model checks PASS");
