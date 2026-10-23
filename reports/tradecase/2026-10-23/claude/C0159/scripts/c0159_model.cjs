// C-0159: модельные проверки новых рисков смены (без сети): контроль, задания без исполнителя, сроки утверждённого плана.
// Формы данных — как в живых ответах 23.10 (склад 220793322: LAUNCHED волны, CASE WAIT_CONTROL/NEW, сессии ACTIVE/CLOSED, time-context).
const assert = require("node:assert/strict"), fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const root = "C:/projects/TMS", ts = require(path.join(root, "admin/wms_admin_frontend/node_modules/typescript"));
const base = path.join(root, "admin/wms_admin_frontend/src/features/platform/workspaces"), cache = {};
const STUB = { react: { useMemo: f => f() }, "./useShiftData": { SHIFT_LIMITS: { future: 50, launched: 100, caseTasks: 200, sessions: 100 } } };
function load(rel) {
  if (cache[rel]) return cache[rel];
  const exports = {}; cache[rel] = exports;
  const js = ts.transpileModule(fs.readFileSync(path.join(base, rel), "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  const dir = path.dirname(rel);
  vm.runInNewContext(js, { exports, Set, Map, Date, Intl, Number, Object, Math, require: id => STUB[id] ?? (id.startsWith(".") && fs.existsSync(path.join(base, dir, id + ".ts")) ? load(path.join(dir, id + ".ts").replace(/\\/g, "/")) : {}) });
  return exports;
}
const risk = load("shift/risks.ts"), hook = load("shift/useShiftRisks.ts");
const out = []; const check = (name, run) => { run(); out.push(name); console.log("PASS", name); };
const wave = (id, status) => ({ pick_wave_id: id, wave_code: "W" + id, ware_id: 220793322, ware_name: "", status, wave_kind: "", planned_start_at: null, planned_finish_at: null, order_count: 1, task_count: 1, launched_at: null });
const task = (id, w, status, assigned_to = null) => ({ case_pick_task_id: id, pick_wave_id: w, status, assigned_to, blocking_reason: null, total_lines: 1, picked_lines: 0 });
const detail = (w, extra = {}) => ({ wave_id: w, observed_at: "2026-10-23T10:00:00Z", readiness: { data: { blockers: [] }, error: "" },
  pick: { data: { released_at: "2026-10-23T08:00:00Z", tasks: [] }, error: "" }, time: { data: { plan_status: "NO_APPROVED_PLAN" }, error: "" }, replenishment: { data: [], error: "" }, ...extra });
const session = (status, resource_type = "CASE_PICKER") => ({ session_id: 1, resource_type, status });
const keys = rs => Array.from(rs, r => r.key).sort();
const none = rs => assert.equal(rs.length, 0, JSON.stringify(rs));

check("control: visible WAIT_CONTROL/CONTROL_IN_PROGRESS of a launched wave are one warning; CONTROLLED/SHIPPED are not", () => {
  const rs = risk.progressRisks([wave(613, "LAUNCHED")], new Map([[613, detail(613)]]),
    [task(1, 613, "WAIT_CONTROL"), task(2, 613, "CONTROL_IN_PROGRESS"), task(3, 613, "CONTROLLED"), task(4, 613, "SHIPPED")], false, [], false);
  assert.deepEqual(keys(rs), ["613:CTL"]); assert.match(rs[0].basis, /Ждут контроля: 2 коробов/); assert.equal(rs[0].action.page, "case-pick-management.html");
});
check("unassigned: only NEW without assignee, only after picking is released; session fact in impact, never a free resource", () => {
  const tasks = [task(1, 613, "NEW"), task(2, 613, "NEW", "picker1"), task(3, 613, "ASSIGNED", "picker2")];
  let rs = risk.progressRisks([wave(613, "LAUNCHED")], new Map([[613, detail(613)]]), tasks, false, [session("CLOSED"), session("ACTIVE", "REACHTRUCK")], false);
  assert.deepEqual(keys(rs), ["613:UNA"]); assert.match(rs[0].basis, /без исполнителя: 1$/); assert.equal(rs[0].impact, "открытых сессий комплектовщиков на складе нет");
  rs = risk.progressRisks([wave(613, "LAUNCHED")], new Map([[613, detail(613)]]), tasks, false, [session("ACTIVE")], false);
  assert.equal(rs[0].impact, "открытых сессий комплектовщиков: 1");
  rs = risk.progressRisks([wave(613, "LAUNCHED")], new Map([[613, detail(613)]]), tasks, false, null, false);
  assert.equal(rs[0].impact, "сессии комплектовщиков не проверены полностью");
  rs = risk.progressRisks([wave(613, "LAUNCHED")], new Map([[613, detail(613)]]), tasks, false, [], true);
  assert.equal(rs[0].impact, "сессии комплектовщиков не проверены полностью");
  const unreleased = detail(613, { pick: { data: { released_at: null, tasks: [] }, error: "" } });
  none(risk.progressRisks([wave(613, "LAUNCHED")], new Map([[613, unreleased]]), tasks, false, [], false));
});
check("truncated CASE sample says 'не меньше'; closed and preview waves get no progress risks; unread tasks → none (gap elsewhere)", () => {
  const rs = risk.progressRisks([wave(613, "LAUNCHED")], new Map([[613, detail(613)]]), [task(1, 613, "WAIT_CONTROL")], true, [], false);
  assert.match(rs[0].basis, /не меньше 1/);
  for (const s of ["DONE", "CANCELLED", "PREVIEW"]) none(risk.progressRisks([wave(9, s)], new Map([[9, detail(9)]]), [task(1, 9, "WAIT_CONTROL"), task(2, 9, "NEW")], false, [], false));
  none(risk.progressRisks([wave(613, "LAUNCHED")], new Map(), null, false, [], false));
});
check("deadline only from APPROVED plan vs server clock: finish passed on LAUNCHED, start passed on PREVIEW; no plan → no lateness", () => {
  const approved = { plan_status: "APPROVED", time_zone: "Europe/Moscow", start_at: "2026-10-23T08:30:00.000000+00:00", finish_at: "2026-10-23T09:15:00.000000+00:00" };
  let rs = risk.waveRisks(wave(613, "LAUNCHED"), detail(613, { time: { data: approved, error: "" } }));
  const tf = rs.find(r => r.key === "613:TF"); assert.equal(tf.severity, "BLOCKER"); assert.match(tf.basis, /прошло 45 мин назад/);
  rs = risk.waveRisks(wave(614, "PREVIEW"), detail(614, { time: { data: approved, error: "" } }));
  assert.match(rs.find(r => r.key === "614:TS").basis, /начало волны прошло 90 мин назад, волна не запущена/);
  rs = risk.waveRisks(wave(615, "LAUNCHED"), detail(615, { time: { data: { ...approved, finish_at: "2026-10-23T11:00:00+00:00" }, error: "" } }));
  assert.ok(!rs.some(r => r.key.endsWith(":TF")));
  rs = risk.waveRisks(wave(616, "LAUNCHED"), detail(616));  // NO_APPROVED_PLAN: only the existing 'not approved' warning
  assert.deepEqual(keys(rs.filter(r => r.source === "time-context")), ["616:T"]);
  rs = risk.waveRisks(wave(617, "LAUNCHED"), detail(617, { observed_at: undefined, time: { data: approved, error: "" } }));
  assert.ok(!rs.some(r => r.key.endsWith(":TF")), "no server clock → no lateness");
  none(risk.waveRisks(wave(618, "DONE"), detail(618, { time: { data: approved, error: "" } })));
});
check("hook: new risks join the list; sessions read failure and truncation are listed as verification gaps", () => {
  const ok = v => ({ data: v, error: "", loading: false });
  const data = { future: ok([]), launched: ok([wave(613, "LAUNCHED")]), caseTasks: ok([task(1, 613, "WAIT_CONTROL"), task(2, 613, "NEW")]), shorts: ok([]),
    sessions: { data: null, error: "403: нет права", loading: false } };
  const r = hook.useShiftRisks([wave(613, "LAUNCHED")], new Map([[613, detail(613)]]), data, { error: "" }, false);
  assert.deepEqual(keys(r.risks), ["613:CTL", "613:T", "613:UNA"]);  // 613:T — existing NO_APPROVED_PLAN warning assert.ok(r.gaps.some(g => g.startsWith("сессии ресурсов: 403")));
  const many = Array.from({ length: 100 }, () => session("CLOSED"));
  const r2 = hook.useShiftRisks([wave(613, "LAUNCHED")], new Map([[613, detail(613)]]), { ...data, sessions: ok(many) }, { error: "" }, false);
  assert.ok(r2.gaps.some(g => g.includes("наличие открытых сессий не утверждается")));
  assert.equal(r2.risks.find(x => x.key === "613:UNA").impact, "сессии комплектовщиков не проверены полностью");
});
fs.writeFileSync(path.join(__dirname, "..", "c0159-model.json"), JSON.stringify({ status: "PASS", checks: out }, null, 1));
console.log(out.length, "C0159 model checks PASS");
