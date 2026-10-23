// C-0148 UI плана маршрута на собранном frontend (:3000).
// ЖИВОЕ: вход admin, GET рейсов склада 220793322/R1.1168, исполнение, нативные route-context и delivery-windows (рейс 33665).
// FIXTURE: /route-points — работающий сервер ещё без нового эндпоинта; ответ = реальный вывод read model (route-points-live.json).
// SYNTHETIC: delivery-windows подменён результатом существующего нативного расчёта на синтетическом входе (synthetic-schedule.json).
// Также fixture: 403 расчёта окон, 403 связи точек, поздний ответ прежнего рейса.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const POINTS = JSON.parse(fs.readFileSync(path.join(OUT, "route-points-live.json"), "utf8"));
const SYN = JSON.parse(fs.readFileSync(path.join(OUT, "synthetic-schedule.json"), "utf8"));
const BASE = process.env.C0148_BASE || "http://127.0.0.1:3000/", WH = "220793322", TRIP = "R1.1168";
const res = { base: BASE, checks: [], liveWrites: [], errors: [], http: [], timings: {} };
const cors = { "access-control-allow-origin": "*" };
let fx = {};

function synthetic(name) {
  // Same stop address as the live route so the plan joins; times/issues are the native calculator's synthetic result.
  const s = SYN[name], first = s.stops[s.stops.length - 1];
  return { status: s.status, departure_at: "2026-11-02T10:15:00.000000+00:00", return_at: s.return_at, warnings: [],
    issues: s.issues.map(code => ({ code, address: code === "DELIVERY_HARD_WINDOW_MISSED" ? "FP21.QA.ADDRESS" : null })),
    stops: [{ ...first, address: "FP21.QA.ADDRESS", window_from: "2026-11-02T12:40:00.000000+00:00", window_to: "2026-11-02T13:25:00.000000+00:00", service_finish_at: null }] };
}

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (m !== "GET") { res.liveWrites.push(m + " " + u); return r.abort(); }
  if (u.includes("/route-points")) {
    if (fx.points403) return r.fulfill({ status: 403, json: { detail: { code: "TRADECASE_ACCESS_DENIED" } }, headers: cors });
    if (fx.late) await new Promise(x => setTimeout(x, 2500));
    return r.fulfill({ json: POINTS[`${WH}/${TRIP}`].result, headers: cors });
  }
  if (u.includes("/delivery-windows")) {
    if (fx.windows403) return r.fulfill({ status: 403, json: { detail: "forbidden" }, headers: cors });
    if (fx.synthetic) return r.fulfill({ json: synthetic(fx.synthetic), headers: cors });
  }
  return r.continue();
}

async function open(b, w, h) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  p.on("response", rr => { if (rr.url().includes(":8088/api/")) res.http.push(`${w} ${rr.status()} ${rr.url().replace(/^.*\/api\//, "/api/").slice(0, 110)}`); });
  await p.route(u => u.href.includes(":8088/api/"), route);
  const t0 = Date.now();
  await p.goto(BASE + "?page=tradecase&tc_wh=" + WH + "&tc_tab=TRIP");
  if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  const rows = p.locator(".tc-body .tc-table tbody tr"); await rows.first().waitFor({ timeout: 30000 });
  await p.locator(".tc-body .tc-table tbody tr", { hasText: TRIP }).first().getByRole("button", { name: "Открыть" }).click();
  await p.locator("[aria-label='План маршрута']").waitFor({ timeout: 30000 });
  return { p, ctx, t0 };
}
const plan = p => p.locator("[aria-label='План маршрута']");
const ok = (w, name, extra = {}) => { res.checks.push({ width: w, name, ...extra }); console.log("PASS", w, name); };

async function live(b, w, h) {
  fx = {};
  const { p, ctx, t0 } = await open(b, w, h);
  await plan(p).locator(".tc-msg", { hasText: "Выезд" }).waitFor({ timeout: 30000 });
  await plan(p).locator("article", { hasText: "MT22.220793322.RECIPIENT" }).waitFor({ timeout: 30000 });
  res.timings["useful_" + w] = Date.now() - t0;
  const t = await plan(p).innerText();
  assert(/Окна не подтверждены/.test(t) && /адрес склада выезда не настроен/.test(t) && /время приезда неизвестно/.test(t), t);
  assert(/Factory CASE QA \(MT22\.220793322\.RECIPIENT\)/.test(t) && /клиент совпадает/.test(t) && /адреса точки нет среди адресов клиента/.test(t), t);
  assert(/выезд и доставку он не подтверждает/.test(t) && !/\d\d:\d\d UTC.*Приезд/.test(t), "no invented times");
  ok(w, "LIVE native windows (33665): depot/time missing named, no invented times; FIXTURE(real read model) recipient linked by keys + checks", { ms: res.timings["useful_" + w] });
  assert(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "page overflow");
  await plan(p).screenshot({ path: path.join(SHOTS, `route-plan-live-${w}.png`) });
  await ctx.close();
}

async function syntheticPlan(b, w, h) {
  fx = { synthetic: "detour_45" };
  let s = await open(b, w, h);
  await plan(s.p).locator("article", { hasText: "строгое окно доставки нарушено" }).waitFor({ timeout: 30000 });
  const t = await plan(s.p).innerText();
  assert(/13:40 UTC/.test(t) && /30 мин/.test(t) && /Окна не подтверждены/.test(t), t);
  ok(w, "SYNTHETIC detour 45: arrival/late from native calculator shown as violation");
  await plan(s.p).screenshot({ path: path.join(SHOTS, `route-plan-synthetic45-${w}.png`) });
  await s.ctx.close();
  fx = { synthetic: "detour_15" };
  s = await open(b, w, h);
  await plan(s.p).locator(".tc-msg", { hasText: "Нарушений окон по расчёту нет" }).waitFor({ timeout: 30000 });
  assert(/12:55 UTC/.test(await plan(s.p).innerText()));
  ok(w, "SYNTHETIC detour 15: no violation, still marked as plan not departure");
  await s.ctx.close();
}

async function negatives(b, w, h) {
  fx = { windows403: true, points403: true };
  const s = await open(b, w, h);
  await plan(s.p).locator(".tc-err", { hasText: "Нет права расчёта окон" }).waitFor({ timeout: 30000 });
  await plan(s.p).locator(".tc-err", { hasText: "Связь точек с получателями не прочитана" }).waitFor({ timeout: 30000 });
  assert.equal(await plan(s.p).locator("article", { hasText: "MT22" }).count(), 0);
  ok(w, "FIXTURE 403 windows and points: explicit, no recipient shown");
  await s.ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try {
    for (const [w, h] of [[1440, 1000], [390, 844]]) { await live(b, w, h); await syntheticPlan(b, w, h); await negatives(b, w, h); }
    assert.deepEqual(res.errors, []); assert.deepEqual(res.liveWrites, []);
    res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  res.asset = (await (await fetch(BASE)).text()).match(/assets\/index-[^"]+\.js/)?.[0];
  res.counts = { checks: res.checks.length, http: res.http.length, liveWrites: res.liveWrites.length, jsErrors: res.errors.length };
  fs.writeFileSync(path.join(OUT, "c0148-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, JSON.stringify(res.counts), JSON.stringify(res.timings));
  await b.close(); process.exit(res.status === "PASS" ? 0 : 1);
})();
