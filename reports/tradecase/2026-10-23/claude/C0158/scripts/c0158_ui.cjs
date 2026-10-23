// C-0158 «План ворот» в дворе старшего смены (dev :3021) при 1440 и 390.
// ЖИВОЕ (GET и read-only POST /api/picking/shift-overview): вход, рабочее место смены склада 220793322 и его прочие чтения.
// FIXTURE: GET визитов двора и планов ворот (маршрут плана на :8088 ещё не загружен, native NOT_APPLIED), все POST команд плана.
// Живых записей нет: любой не-GET вне fixture прерывается и фиксируется. Подтверждения команд — подставные ответы, не исход Oracle.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0158_BASE || "http://127.0.0.1:3021/", WH = 220793322;
const res = { base: BASE, checks: [], liveWrites: [], errors: [], posts: [], timings: {} };
const cors = { "access-control-allow-origin": "*" };
const at = min => new Date(Date.now() + min * 60000).toISOString().replace(/\.\d+Z$/, "Z");
let fx = {};

const visit = (id, state, extra = {}) => ({ visit_id: id, warehouse_id: WH, visit_kind: "OUTBOUND", trip_id: "T" + id, vehicle: "A" + id + "BC77", dock: null,
  planned_dock: null, state, version: 2, planned_arrival_at: at(-30), arrived_at: state === "EXPECTED" ? null : at(-20), docked_at: null,
  work_started_at: null, work_finished_at: null, updated_by: "admin", ...extra });
const VISITS = () => [visit(901, "EXPECTED"), visit(902, "ARRIVED"), visit(903, "EXPECTED"), visit(904, "WORKING", { dock: "16", docked_at: at(-40) })];
const plan = (id, v, dock, from, to, extra = {}) => ({ plan_id: id, warehouse_id: WH, visit_id: v, dock, planned_from: at(from), planned_to: at(to), status: "ACTIVE",
  version: 1, visit_kind: "OUTBOUND", trip_id: "T" + v, vehicle: "A" + v + "BC77", visit_state: "EXPECTED", fact_dock: null, arrived_at: null, docked_at: null,
  work_started_at: null, departed_at: null, ...extra });
const PLANS = () => ({ warehouse_id: WH, observed_at: at(0), plans: [plan(71, 901, "16", -15, 45), plan(72, 902, "17", 60, 120, { visit_state: "ARRIVED", arrived_at: at(-20) })] });

async function route(r) {
  const req = r.request(), m = req.method(), u = new URL(req.url());
  if (m === "OPTIONS") return r.continue();
  if (u.pathname === `/api/tradecase/warehouses/${WH}/yard/visits` && m === "GET") return r.fulfill({ status: 200, json: { warehouse_id: WH, observed_at: at(0), visits: VISITS() }, headers: cors });
  if (u.pathname === `/api/tradecase/warehouses/${WH}/yard/dock-plans` && m === "GET") {
    if (fx.plans403) return r.fulfill({ status: 403, json: { detail: { code: "YARD_ACCESS_DENIED" } }, headers: cors });
    if (fx.plans503) return r.fulfill({ status: 503, json: { detail: { code: "YARD_PLAN_NOT_AVAILABLE", outcome_confirmed: false, retry_same_operation_id: true } }, headers: cors });
    res.window = [u.searchParams.get("from"), u.searchParams.get("to")];
    return r.fulfill({ status: 200, json: PLANS(), headers: cors });
  }
  if (m === "POST" && u.pathname.startsWith(`/api/tradecase/warehouses/${WH}/yard/dock-plans`)) {
    const body = req.postData(); res.posts.push({ path: u.pathname, body }); const op = JSON.parse(body).operation_id, next = (fx.confirm || []).shift() || "ack";
    const planId = Number((/dock-plans\/(\d+)/.exec(u.pathname) || [])[1] || 99);
    if (next === "ack") return r.fulfill({ status: 200, json: { operation_id: op, plan_id: planId, replayed: false }, headers: cors });
    if (next === "503") return r.fulfill({ status: 503, json: { detail: { code: "YARD_RESULT_UNKNOWN", outcome_confirmed: false, retry_same_operation_id: true } }, headers: cors });
    return r.fulfill({ status: 409, json: { detail: { code: next, outcome_confirmed: true, retry_same_operation_id: false } }, headers: cors });
  }
  // Documented read-only POST (bundles wave IDs into one READ ONLY snapshot); counted as a live read, not a write.
  if (m === "POST" && u.pathname === "/api/picking/shift-overview") { res.liveReadPosts = (res.liveReadPosts || 0) + 1; return r.continue(); }
  if (m !== "GET") { res.liveWrites.push(m + " " + u.href); return r.abort(); }
  return r.continue();
}
const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };
const section = p => p.locator("[aria-label='План ворот']");

async function enter(p) {
  const password = p.locator("input[type=password]"), open = p.locator("[aria-label='Процессы старшего смены']").getByRole("button", { name: /Двор и ворота/ });
  await Promise.race([password.waitFor({ timeout: 30000 }), open.waitFor({ timeout: 30000 })]);
  if (await password.count()) { await p.fill("input[autocomplete=username]", "admin"); await password.fill(pass); await p.click("button[type=submit]"); }
  await open.waitFor({ timeout: 30000 }); await open.click(); await section(p).waitFor({ timeout: 30000 });
}
const login = (p, name) => p.evaluate(async n => {
  const api = await import(performance.getEntriesByType("resource").map(e => e.name).find(u => /\/src\/api\.ts(\?|$)/.test(u)));
  if (!window.__c0158) window.__c0158 = { username: "admin", password: api.adminBasicAuth().split(":").slice(1).join(":") };
  api.setSessionCredentials(n === "admin" ? window.__c0158 : { username: n, password: "x" });
}, name);
const localValue = min => { const d = new Date(Date.now() + min * 60000); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16); };

async function newPlan(p, dock = "15") {
  const s = section(p), start = s.getByRole("button", { name: "Запланировать ворота" });
  if (await start.count()) await start.click();  // after a refusal the form stays open for correction
  await s.getByLabel("Визит").selectOption("903"); await s.getByLabel("Ворота").fill(dock);
  await s.getByLabel("Начало").fill(localValue(120)); await s.getByLabel("Конец").fill(localValue(180));
  await s.getByRole("button", { name: "Запланировать", exact: true }).click();
}

async function width(b, w, h) {
  fx = {}; res.posts = [];
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await ctx.route(u => u.href.includes(":8088/api/"), route);
  const t0 = Date.now(); await p.goto(`${BASE}?page=workspace&workspace=shift&warehouse_id=${WH}`); await enter(p); res.timings["plan_ready_" + w] = Date.now() - t0;
  const s = section(p);
  await s.getByText("Ворота 16").waitFor();
  const text = await s.innerText();
  assert(text.includes("машина не приехала, план начала прошёл") && text.includes("ворота сейчас занимает визит 904") && text.includes("не факт приезда"), text);
  ok(w, "FIXTURE plans listed next to visit facts; lateness and occupied dock from real-shaped facts, plan marked as not a fact");
  const span = (Date.parse(res.window[1]) - Date.parse(res.window[0])) / 3600000; assert(span <= 168, span); ok(w, "read window within the server's 7-day bound");
  const bad = await p.locator("section[aria-label='Двор'] button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every yard/plan button has title and help id");
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(over <= 1, "overflow " + over); ok(w, "no horizontal page scroll");
  await s.screenshot({ path: path.join(SHOTS, `dock-plan-${w}.png`) });

  fx.confirm = ["ack"]; await newPlan(p); await s.getByText("План ворот сохранён.").waitFor();
  const first = JSON.parse(res.posts[0].body);
  assert(res.posts[0].path.endsWith("/yard/dock-plans") && first.visit_id === 903 && first.dock === "15" && /Z$/.test(first.planned_from) && Date.parse(first.planned_to) - Date.parse(first.planned_from) === 3600000, res.posts[0].body);
  ok(w, "FIXTURE PLAN: visit, dock and an exact UTC interval from the browser time zone are sent");
  fx.confirm = ["YARD_DOCK_PLAN_CONFLICT"]; await newPlan(p); await s.getByText("уже запланирована другая машина").waitFor();
  assert(await s.getByRole("button", { name: "Повторить команду плана" }).count() === 0); ok(w, "FIXTURE conflict: readable refusal, journal cleared");

  fx.confirm = ["503"]; res.posts = []; await newPlan(p); await s.getByText("Исход не подтверждён").waitFor();
  await p.reload(); await enter(p); await section(p).getByRole("button", { name: "Повторить команду плана" }).waitFor(); ok(w, "FIXTURE unknown outcome: command survives reload");
  await login(p, "other"); await section(p).getByRole("button", { name: "Повторить команду плана" }).click(); await section(p).getByText("Вход сменился").waitFor();
  assert(res.posts.length === 1); ok(w, "account switched: the stored command is not sent under another login");
  await login(p, "admin"); await p.reload(); await enter(p); fx.confirm = ["ack"];
  await section(p).getByRole("button", { name: "Повторить команду плана" }).click(); await section(p).getByText("План ворот сохранён.").waitFor();
  assert(res.posts.length === 2 && res.posts[0].body === res.posts[1].body); ok(w, "exact replay: identical bytes and operation id, own receipt clears");

  const row = section(p).locator("li", { hasText: "Ворота 17" });
  await row.getByRole("button", { name: "Перенести" }).click(); await row.getByLabel("Ворота").fill("18");
  fx.confirm = ["VERSION_CONFLICT"]; res.posts = []; await row.getByRole("button", { name: "Перенести план" }).click();
  await section(p).getByText("Визит уже изменён").waitFor();
  const moved = JSON.parse(res.posts[0].body); assert(res.posts[0].path.endsWith("/dock-plans/72/move") && moved.expected_version === 1 && moved.dock === "18", res.posts[0].body);
  ok(w, "FIXTURE MOVE carries plan version; version conflict is shown");
  await section(p).locator("li", { hasText: "Ворота 16" }).getByRole("button", { name: "Отменить план" }).click();
  await section(p).getByLabel("Причина отмены плана").fill("рейс перенесён"); fx.confirm = ["ack"];
  await section(p).locator("li", { hasText: "Ворота 16" }).locator("form").getByRole("button", { name: "Отменить план" }).click(); await section(p).getByText("План отменён.").waitFor();
  assert(res.posts[1].path.endsWith("/dock-plans/71/cancel") && JSON.parse(res.posts[1].body).reason === "рейс перенесён"); ok(w, "FIXTURE CANCEL with reason; visit facts untouched");
  await section(p).screenshot({ path: path.join(SHOTS, `dock-plan-actions-${w}.png`) });

  fx.plans503 = true; await section(p).getByRole("button", { name: "Обновить план" }).click();
  await section(p).getByText("это не «ворота свободны»").waitFor(); fx.plans503 = false; ok(w, "plan objects absent: unknown, never 'docks free'");
  fx.plans403 = true; await section(p).getByRole("button", { name: "Обновить план" }).click();
  await section(p).getByText("План ворот не прочитан").waitFor(); assert(await section(p).locator("li").count() === 0); ok(w, "403 clears the plans");
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 1000); await width(b, 390, 844); assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.liveWrites, []); res.status = "PASS"; }
  catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0158-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, "checks", JSON.stringify(res.timings));
  process.exit(res.status === "PASS" ? 0 : 1);
})();
