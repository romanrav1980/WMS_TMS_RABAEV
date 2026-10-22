// C-0154 UI дополнительного заезда в маршруте рейса (dev :3021) при 1440 и 390.
// ЖИВОЕ (только GET): вход, рейсы склада 220793322/R1.1168, маршрут, связь точек, окна. FIXTURE: /extra-stops/** (миграция не применена);
// ответы оценки = настоящий вывод PURE-части пакета на настоящем native calculate (extra-stop-pure-live.json, SYNTHETIC маршрут программы)
// и настоящий вывод evaluate по рейсу 33665 (extra-stop-trip-live.json). Любой не-GET вне /extra-stops/ прерывается.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const PURE = JSON.parse(fs.readFileSync(path.join(OUT, "extra-stop-pure-live.json"), "utf8"));
const TRIP = JSON.parse(fs.readFileSync(path.join(OUT, "extra-stop-trip-live.json"), "utf8"))["33665"].result;
const BASE = process.env.C0154_BASE || "http://127.0.0.1:3021/", WH = "220793322", TRIPNO = "R1.1168", H = "c".repeat(64);
const res = { base: BASE, checks: [], liveWrites: [], errors: [], posts: [], timings: {} };
const cors = { "access-control-allow-origin": "*" };
let fx = {};
const bind = (r, address) => ({ ...r, address, source_hash: H, time_version: 3 });
const EVAL = { EXTRA: bind(PURE.extra_15_slack_30, "EXTRA"), "EXTRA-45": bind(PURE.extra_45_slack_30, "EXTRA-45"), "EXTRA-BAN": bind(PURE.new_stops_forbidden, "EXTRA-BAN"),
  "EXTRA-REAL": { ...TRIP, address: "EXTRA-REAL" } };

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (u.includes("/extra-stops")) {
    if (u.includes("/decisions")) return r.fulfill({ json: { trip_id: 33665, source_hash: H, time_version: 3, new_stops_forbidden: !!fx.banned, policy_version: fx.banned ? 1 : 0,
      decisions: [{ operation_id: "TC.STOP.UI:old", address: "OLD-STORE", position: 1, decision_state: "APPROVED", decided_by: "disp", decided_at: "2026-10-23T08:00:00Z", validity: "STALE_ROUTE_CHANGED" }] }, headers: cors });
    if (m === "GET") {
      if (fx.unavailable) return r.fulfill({ status: 503, json: { detail: { code: "EXTRA_STOP_NOT_AVAILABLE", outcome_confirmed: false, retry_same_operation_id: true } }, headers: cors });
      const a = new URL(u).searchParams.get("address"); return r.fulfill({ json: EVAL[a] ?? { ...EVAL["EXTRA-REAL"], address: a }, headers: cors });
    }
    const body = req.postData(); res.posts.push(body);
    const reply = fx.replies.shift();
    if (reply === 503) return r.fulfill({ status: 503, json: { detail: { code: "EXTRA_STOP_RESULT_UNKNOWN", outcome_confirmed: false, retry_same_operation_id: true } }, headers: cors });
    if (typeof reply === "string") return r.fulfill({ status: 409, json: { detail: { code: reply, outcome_confirmed: true, retry_same_operation_id: false } }, headers: cors });
    return r.fulfill({ json: { operation_id: JSON.parse(body).operation_id, action: JSON.parse(body).action, replayed: false }, headers: cors });
  }
  if (m !== "GET") { res.liveWrites.push(m + " " + u); return r.abort(); }
  return r.continue();
}

const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };
const panel = p => p.locator("[aria-label='Дополнительный заезд']");

async function open(b, w, h) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await p.route(u => u.href.includes(":8088/api/"), route);
  const t0 = Date.now();
  await p.goto(BASE + "?page=tradecase&tc_wh=" + WH + "&tc_tab=TRIP");
  await enter(p);
  (res.timings["panel_" + w] ??= []).push(Date.now() - t0);
  return { p, ctx };
}

async function enter(p) {
  const login = p.locator("input[type=password]"), rows = p.locator(".tc-body .tc-table tbody tr");
  await Promise.race([login.waitFor({ timeout: 30000 }), rows.first().waitFor({ timeout: 30000 })]);
  if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
  await rows.first().waitFor({ timeout: 30000 });
  await p.locator(".tc-body .tc-table tbody tr", { hasText: TRIPNO }).first().getByRole("button", { name: "Открыть" }).click();
  await panel(p).waitFor({ timeout: 30000 });
}

async function check(p, address) {
  await panel(p).getByLabel("Адрес получателя для заезда").fill(address);
  await panel(p).getByRole("button", { name: "Проверить заезд" }).click();
}

async function width(b, w, h) {
  fx = { replies: [] };
  let { p, ctx } = await open(b, w, h);
  const bad = await panel(p).locator("button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every extra-stop button has title and help id");
  assert((await panel(p).innerText()).includes("маршрут изменился после решения")); ok(w, "decision made on an older route is shown as stale");
  const plan = p.locator("[aria-label='План маршрута']"); await plan.getByText("Что сделать:").waitFor({ timeout: 30000 });
  assert((await plan.innerText()).includes("«Настроить исходные данные маршрута» → адрес склада выезда")); ok(w, "LIVE trip 33665: missing inputs point to the existing controls");

  await check(p, "EXTRA"); await panel(p).getByText("Заезд укладывается").waitFor();
  const t = await panel(p).innerText();
  assert(t.includes("30 мин → после заезда 15 мин") && t.includes("добавляет 15 мин") && t.includes("EXTRA (новая)") && !/[A-Z_]{12,}/.test(t.replace(/EXTRA/g, "")), t);
  ok(w, "15-minute stop with 30 minutes slack is proposed with changed arrivals/return (real calculator output)");
  const over = await p.evaluate(() => { const W = innerWidth; return document.documentElement.scrollWidth <= W + 1 ? null
    : [...document.querySelectorAll("body *")].filter(e => e.getBoundingClientRect().right > W + 1).slice(-6).map(e => e.tagName + "." + e.className + " " + Math.round(e.getBoundingClientRect().right)); });
  assert(over === null, "page overflow: " + JSON.stringify(over)); ok(w, "no horizontal page scroll");
  await panel(p).screenshot({ path: path.join(SHOTS, `extra-propose-${w}.png`) });

  fx.replies = [503];
  await panel(p).getByLabel("Основание решения").fill("магазин просит довезти");
  await panel(p).getByRole("button", { name: "Согласовать заезд" }).click(); await panel(p).getByText("Результат неизвестен").waitFor();
  const sent = JSON.parse(res.posts.at(-1));
  assert.deepStrictEqual({ ...sent, operation_id: 0 }, { operation_id: 0, action: "APPROVE", reason: "магазин просит довезти", address: "EXTRA", zone: "UTC",
    expected_version: 3, source_hash: H, position: 0 }); ok(w, "approval binds address, position, route version and source hash");
  await p.reload(); await enter(p);
  await panel(p).getByText("не подтверждено").waitFor(); ok(w, "unconfirmed decision survives reload");
  fx.replies = [200]; await panel(p).getByRole("button", { name: "Повторить ту же команду" }).click(); await panel(p).getByText("Заезд согласован").waitFor();
  assert.strictEqual(res.posts.at(-1), res.posts.at(-2)); assert((await panel(p).innerText()).includes("SAP сейчас недоступен")); ok(w, "retry resends identical bytes; SAP order not invented");

  await check(p, "EXTRA-45"); await panel(p).getByText("Заезд не укладывается").waitFor();
  assert(await panel(p).getByRole("button", { name: "Согласовать заезд" }).count() === 0); ok(w, "45-minute stop is rejected and cannot be approved");
  fx.replies = ["EXTRA_STOP_SOURCE_CHANGED"]; await panel(p).getByLabel("Основание решения").fill("не успеваем");
  await panel(p).getByRole("button", { name: "Отклонить заезд" }).click(); await panel(p).getByText("Маршрут или его данные изменились").waitFor(); ok(w, "changed route refuses an old decision");

  await check(p, "EXTRA-REAL"); await panel(p).getByText("Нельзя обещать выполнимость").waitFor();
  assert((await panel(p).innerText()).includes("адрес склада выезда не настроен")); ok(w, "real trip 33665: missing inputs named, no promise");
  await check(p, "EXTRA-BAN"); await panel(p).getByText("Заезд не предлагается").waitFor(); ok(w, "ban on new points: not proposed");
  fx.replies = [200]; await panel(p).getByRole("button", { name: "Запретить новые точки" }).click(); await panel(p).getByText("Настройка запрета").waitFor();
  assert.deepStrictEqual({ ...JSON.parse(res.posts.at(-1)), operation_id: 0 }, { operation_id: 0, action: "SET_POLICY", reason: "не успеваем", new_stops_forbidden: true, expected_policy_version: 0 });
  ok(w, "ban is a versioned command");
  fx.unavailable = true; await check(p, "EXTRA-OFF"); await panel(p).getByText("Решения о дополнительных заездах на сервере ещё не включены").waitFor(); ok(w, "not applied is explicit");
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 1000); await width(b, 390, 844); assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.liveWrites, []); res.status = "PASS"; }
  catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0154-ui.json"), JSON.stringify({ ...res, posts: res.posts.length }, null, 1));
  console.log(res.status, res.checks.length, "checks", JSON.stringify(res.timings));
  process.exit(res.status === "PASS" ? 0 : 1);
})();
