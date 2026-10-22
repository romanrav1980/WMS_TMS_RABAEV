// C-0150 (ревизия C-0149) UI двора у старшего смены на frontend (dev :3021) при 1440 и 390.
// ЖИВОЕ (только GET): вход admin, склады, волны, сессии, общий Гант.
// FIXTURE: весь /yard/** (миграция двора не применена), события визитов дописаны в живой ответ /api/resources/timeline.
// Любой не-GET вне /yard/ прерывается и записывается как нарушение.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0150_BASE || "http://127.0.0.1:3021/", WH = 220793322;
const res = { base: BASE, checks: [], liveWrites: [], errors: [], posts: [], timings: {} };
const cors = { "access-control-allow-origin": "*" };
const NOW = Date.now(), at = min => new Date(NOW + min * 60000).toISOString().replace(/\.\d+Z$/, "Z");
const visit = (id, state, extra) => ({ visit_id: id, warehouse_id: WH, visit_kind: "OUTBOUND", trip_id: "R" + id, native_task_id: null, vehicle: "А00" + id + "ВС",
  dock: null, planned_dock: null, state, version: 3, planned_arrival_at: null, arrived_at: null, docked_at: null, work_started_at: null, work_finished_at: null,
  departed_at: null, cancelled_at: null, cancel_reason: null, updated_by: "boss", ...extra });
const VISITS = [visit(1, "WORKING", { dock: "Д-01", arrived_at: at(-70), docked_at: at(-60), work_started_at: at(-55) }),
  visit(2, "ARRIVED", { planned_dock: "Д-01", arrived_at: at(-25) }), visit(3, "EXPECTED", { planned_arrival_at: at(-30), planned_dock: "Д-02" }),
  visit(4, "EXPECTED", { vehicle: null })];
let fx = {};

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (u.includes("/yard/visits")) {
    if (m === "GET") {
      if (fx.late) { const late = fx.late; fx.late = null; await new Promise(x => setTimeout(x, late));
        return r.fulfill({ json: { warehouse_id: WH, observed_at: at(0), visits: [visit(99, "ARRIVED", { arrived_at: at(-5) })] }, headers: cors }); }
      if (fx.unavailable) return r.fulfill({ status: 503, json: { detail: { code: "YARD_NOT_AVAILABLE", outcome_confirmed: false, retry_same_operation_id: true } }, headers: cors });
      if (fx.read403) return r.fulfill({ status: 403, json: { detail: { code: "YARD_ACCESS_DENIED", outcome_confirmed: true, retry_same_operation_id: false } }, headers: cors });
      return r.fulfill({ json: { warehouse_id: WH, observed_at: at(0), visits: fx.visits ?? VISITS }, headers: cors });
    }
    const body = req.postData(); res.posts.push(body);
    const reply = fx.replies.shift();
    if (reply === 503) return r.fulfill({ status: 503, json: { detail: { code: "YARD_RESULT_UNKNOWN", outcome_confirmed: false, retry_same_operation_id: true } }, headers: cors });
    if (typeof reply === "string" && reply !== "foreign") return r.fulfill({ status: 409, json: { detail: { code: reply, outcome_confirmed: true, retry_same_operation_id: false } }, headers: cors });
    const id = Number(u.match(/visits\/(\d+)\/transitions/)?.[1] ?? 9);
    const op = reply === "foreign" ? "yard-someone-else" : JSON.parse(body).operation_id;  // квитанция называет свою операцию
    return r.fulfill({ json: { ...visit(id, "ARRIVED", { arrived_at: at(0) }), operation_id: op, replayed: false }, headers: cors });
  }
  if (m === "POST" && u.endsWith("/api/picking/shift-overview")) return r.continue(); // пакетное чтение деталей волн (read-only)
  if (m !== "GET") { res.liveWrites.push(m + " " + u); return r.abort(); }
  if (u.includes("/api/resources/timeline")) {
    const t0 = Date.now(), live = await r.fetch(), t = await live.json();
    (res.timings.timeline_live_ms ??= []).push(Date.now() - t0);
    t.resources.push({ resource_id: `DOCK:${WH}:Д-01`, kind: "DOCK", label: "Д-01", warehouse_id: WH, source_state: "UNKNOWN", availability: "UNKNOWN" },
      { resource_id: "VEHICLE:А001ВС", kind: "VEHICLE", label: "А001ВС", warehouse_id: WH, source_state: null, availability: "UNKNOWN" });
    // Вывод TimelineProjection.yard для визита: машина с приезда (-70), ворота Д-02 с -65 до переназначения (-60), Д-01 с -60 открыто.
    const ev = (event_id, kind, label, fs, ff, status) => ({ event_id, kind, label, source: "RRL_YARD_VISIT", source_id: 1, trip_id: "R1", status,
      plan_start_at: null, plan_finish_at: null, fact_start_at: fs, fact_finish_at: ff, time_status: "AWARE_FACT", fact_finish_status: ff ? "CLOSED" : "OPEN" });
    t.events.push(ev("YARD_VISIT:1", "YARD_VISIT", "Визит 1 · рейс R1", at(-70), null, "WORKING"),
      ev("YARD_DOCK:1:1", "YARD_DOCK", "Ворота Д-02 · визит 1", at(-65), at(-60), "DONE"), ev("YARD_DOCK:1:2", "YARD_DOCK", "Ворота Д-01 · визит 1", at(-60), null, "WORKING"));
    t.resources.push({ resource_id: `DOCK:${WH}:Д-02`, kind: "DOCK", label: "Д-02", warehouse_id: WH, source_state: "UNKNOWN", availability: "UNKNOWN" });
    t.assignments.push({ event_id: "YARD_VISIT:1", resource_id: "VEHICLE:А001ВС" }, { event_id: "YARD_DOCK:1:1", resource_id: `DOCK:${WH}:Д-02` },
      { event_id: "YARD_DOCK:1:2", resource_id: `DOCK:${WH}:Д-01` });
    // Живой сервер без миграции отдаёт yard=NOT_MAPPED (записывается как доказательство); в fixture источник готов.
    res.liveYardSource = t.sources.find(x => x.source_id === "yard")?.status ?? "ABSENT";
    t.sources = [...t.sources.filter(x => x.source_id !== "yard"), { source_id: "yard", status: "READY", permission: "tradecase_view", limit: 2000, observed_at: t.observed_at }];
    return r.fulfill({ response: live, json: t });
  }
  return r.continue();
}

const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };
const panel = p => p.locator("[aria-label='Двор']");

async function open(b, w, h, ctx) {
  ctx = ctx ?? await b.newContext({ viewport: { width: w, height: h } });
  const p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await p.route(u => u.href.includes(":8088/api/"), route);
  await p.goto(`${BASE}?page=workspace&workspace=shift&warehouse_id=${WH}`);
  await enter(p);
  return { p, ctx };
}

async function enter(p) {
  const login = p.locator("input[type=password]"), yard = p.locator("button[data-help-id='shift.process.yard']");
  await Promise.race([login.waitFor({ timeout: 30000 }), yard.waitFor({ timeout: 30000 })]);
  if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
  await yard.click({ timeout: 30000 });
  await panel(p).waitFor({ timeout: 30000 });
}

async function width(b, w, h) {
  fx = { replies: [] };
  const { p, ctx } = await open(b, w, h);
  const y = panel(p);
  const t0 = Date.now(); await y.getByText("Визит 1").waitFor(); (res.timings.yard_panel_render_ms ??= []).push(Date.now() - t0);
  const text = await y.innerText();
  for (const s of ["На площадке · 1", "У ворот", "Идёт работа · 1", "Ожидается · 2", "очередь на ворота: 1", "ждёт 25 мин", "опаздывает на 30 мин",
    "Конфликт: запланированные ворота Д-01 заняты визитом 1", "машина в рейсе не указана", "нет плана приезда"]) if (s !== "У ворот") assert(text.includes(s), s);
  ok(w, "groups, queue, server-clock delay, conflict, missing data");
  const bad = await y.locator("button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every yard button has title and help id");
  const scroll = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  assert(scroll <= 1, "horizontal scroll " + scroll); ok(w, "no horizontal page scroll");
  await y.screenshot({ path: path.join(SHOTS, `yard-${w}.png`) });

  // Неизвестный исход: команда сохранена, переживает перезагрузку, повтор — те же байты и тот же operation_id.
  fx.replies = [503];
  await y.locator("li", { hasText: "Визит 3" }).getByRole("button", { name: "Приехала" }).click();
  await y.getByText("не подтверждена").waitFor(); ok(w, "503 keeps the command as unconfirmed");
  assert(await y.getByRole("button", { name: "Приехала" }).first().isDisabled()); ok(w, "new actions blocked while unconfirmed");
  await p.reload(); await enter(p); await panel(p).getByText("не подтверждена").waitFor();
  ok(w, "unconfirmed command survives reload");
  fx.replies = [200];
  await panel(p).getByRole("button", { name: "Повторить" }).click();
  await panel(p).getByText("Выполнено: Приехала").waitFor();
  assert.strictEqual(res.posts.at(-1), res.posts.at(-2)); assert(JSON.parse(res.posts.at(-1)).operation_id.startsWith("yard-"));
  ok(w, "retry resends identical bytes with the same operation_id");

  // Чужая квитанция (другой operation_id) не снимает команду.
  fx.replies = ["foreign"];
  await panel(p).locator("li", { hasText: "Визит 4" }).getByRole("button", { name: "Приехала" }).click();
  await panel(p).getByText("не подтверждена").waitFor(); ok(w, "foreign receipt keeps the command unconfirmed");
  fx.replies = [200]; await panel(p).getByRole("button", { name: "Повторить" }).click(); await panel(p).getByText("Выполнено: Приехала").waitFor();
  assert.strictEqual(res.posts.at(-1), res.posts.at(-2)); ok(w, "retry after a foreign receipt resends the same bytes");

  // Подтверждённый отказ снимает команду и объясняет причину.
  fx.replies = ["VERSION_CONFLICT"];
  const row2 = panel(p).locator("li", { hasText: "Визит 2" });
  await row2.getByRole("button", { name: "Поставить к воротам" }).click();
  assert.strictEqual(await row2.getByLabel("Ворота").inputValue(), "Д-01");
  await row2.getByLabel("Ворота").fill("Д-02"); await row2.locator("button[data-help-id='shift.yard.confirm']").click();
  await panel(p).getByText("Визит уже изменён другим пользователем").waitFor();
  assert.deepStrictEqual(JSON.parse(res.posts.at(-1)), { operation_id: JSON.parse(res.posts.at(-1)).operation_id, expected_version: 3, action: "ASSIGN_DOCK", dock: "Д-02" });
  assert.strictEqual(await panel(p).getByText("не подтверждена").count(), 0); ok(w, "409 refusal clears the command with a reason");

  // Отмена требует причину; кнопка неактивна, пока причина короче 3 символов.
  const row3 = panel(p).locator("li", { hasText: "Визит 3" });
  await row3.getByRole("button", { name: "Отменить визит" }).click();
  assert(await row3.locator("button[data-help-id='shift.yard.confirm']").isDisabled()); ok(w, "cancel needs a reason");

  // «В Ганте» выделяет визит в общем Ганте: открытая полоса ворот и машины.
  await panel(p).locator("li", { hasText: "Визит 1" }).getByRole("button", { name: "В Ганте" }).click();
  const bar = p.locator(".rg-bar.selected").first(); await bar.waitFor({ timeout: 30000 });
  assert((await bar.getAttribute("title")).includes("Визит 1")); ok(w, "yard visit is selected in the resource Gantt");
  const card = await p.locator("[aria-label='Общий Гант ресурсов']").first().innerText();
  assert(card.includes("Идёт работа") && card.includes("открыто до выезда")); ok(w, "Gantt card shows visit state and open end");
  const docks = await p.locator(".rg-bar").evaluateAll(bs => bs.map(b => b.title).filter(t => t.startsWith("Ворота Д-0")));
  assert(docks.some(t => t.startsWith("Ворота Д-02") && !t.includes("идёт")) && docks.some(t => t.startsWith("Ворота Д-01") && t.includes("идёт")), JSON.stringify(docks));
  ok(w, "reassigned visit: closed interval on the old dock, open on the new one");
  await p.locator("[aria-label='Общий Гант ресурсов']").first().screenshot({ path: path.join(SHOTS, `gantt-${w}.png`) });

  // Поздний ответ прежнего чтения не перетирает более новый снимок.
  fx.late = 2500; await panel(p).locator("button[data-help-id='shift.yard.refresh']").click();
  await p.waitForTimeout(200); await panel(p).locator("button[data-help-id='shift.yard.refresh']").click({ timeout: 500 }); // второе чтение сразу, не после первого
  const clickedAt = Date.now(); await p.waitForTimeout(3200);
  assert(Date.now() - clickedAt >= 3200 && fx.late === null, "late response was served");
  assert.strictEqual(await panel(p).getByText("Визит 99").count(), 0); assert(await panel(p).getByText("Визит 1").count() > 0);
  ok(w, "late response of an older read is ignored");

  // Двор до миграции: явная недоступность, не «нет визитов».
  fx.unavailable = true; await panel(p).locator("button[data-help-id='shift.yard.refresh']").click();
  await panel(p).getByText("Учёт двора на сервере ещё не включён").waitFor();
  assert.strictEqual(await panel(p).getByText("Активных визитов нет").count(), 0); ok(w, "yard not available is explicit, not an empty yard");
  fx.unavailable = false;

  // 403 чтения убирает прежний список.
  fx.read403 = true; await panel(p).locator("button[data-help-id='shift.yard.refresh']").click();
  await panel(p).getByText("Нет права просмотра").waitFor();
  assert.strictEqual(await panel(p).getByText("Визит 1").count(), 0); ok(w, "403 clears visible visits");
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 900); await width(b, 390, 844); }
  catch (e) { res.errors.push(String(e.stack || e)); console.error(e); }
  finally { await b.close(); }
  assert.deepStrictEqual(res.liveWrites, []);
  fs.writeFileSync(path.join(OUT, "c0150-ui.json"), JSON.stringify({ ...res, posts: res.posts.length }, null, 1));
  console.log(res.errors.length ? "FAIL" : "OK", res.checks.length, "checks");
  process.exit(res.errors.length ? 1 : 0);
})();
