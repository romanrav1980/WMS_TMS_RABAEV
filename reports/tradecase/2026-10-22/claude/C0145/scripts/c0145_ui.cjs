// C-0145 UI маршрута и обеспеченности на собранном frontend (:3000).
// ЖИВОЕ: вход admin, GET рейсов склада 215590763, исполнение и нативный GET /api/transport/preflight/trips/{id}/route-context.
// FIXTURE: /coverage — работающий сервер ещё без нового эндпоинта, поэтому ответ взят из реального вывода read model (coverage-live.json,
// одна READ ONLY транзакция 22.10); 403 маршрута/обеспеченности, непривязанный рейс (404 исполнения), поздний ответ прежнего рейса.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const LIVE = JSON.parse(fs.readFileSync(path.join(OUT, "coverage-live.json"), "utf8"));
const BASE = process.env.C0145_BASE || "http://127.0.0.1:3000/", WH = "215590763";
const res = { base: BASE, checks: [], liveWrites: [], errors: [], http: [], timings: {} };
const cors = { "access-control-allow-origin": "*" };
let fx = {};

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (m !== "GET") { res.liveWrites.push(m + " " + u); return r.abort(); }
  const trip = (u.match(/\/trips\/([^/]+)\//) || [])[1];
  if (u.includes("/coverage")) {
    if (fx.cover403) return r.fulfill({ status: 403, json: { detail: { code: "TRADECASE_ACCESS_DENIED" } }, headers: cors });
    if (fx.lateTrip === decodeURIComponent(trip)) await new Promise(x => setTimeout(x, 2500));
    const live = LIVE[`${WH}/${decodeURIComponent(trip)}`];
    return live ? r.fulfill({ json: live.result, headers: cors }) : r.fulfill({ status: 404, json: { detail: { code: "TRADE_ROUTE_SOURCE_MISSING:TRIP" } }, headers: cors });
  }
  if (fx.route403 && u.includes("/route-context")) return r.fulfill({ status: 403, json: { detail: "forbidden" }, headers: cors });
  if (fx.unbound && u.includes("/execution")) return r.fulfill({ status: 404, json: { detail: { code: "TRADE_TRIP_BINDING_NOT_FOUND" } }, headers: cors });
  return r.continue();
}

async function open(b, w, h, trip) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  p.on("response", rr => { if (rr.url().includes(":8088/api/")) res.http.push(`${w} ${rr.status()} ${rr.url().replace(/^.*\/api\//, "/api/").slice(0, 100)}`); });
  await p.route(u => u.href.includes(":8088/api/"), route);
  const t0 = Date.now();
  await p.goto(BASE + "?page=tradecase&tc_wh=" + WH + "&tc_tab=TRIP");
  if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  await openTrip(p, trip);
  return { p, ctx, t0 };
}
async function openTrip(p, trip) {
  const rows = p.locator(".tc-body .tc-table tbody tr"); await rows.first().waitFor({ timeout: 30000 });
  await p.locator(".tc-body .tc-table tbody tr", { hasText: trip }).first().getByRole("button", { name: "Открыть" }).click();
  await p.locator("section[aria-label='Маршрут и обеспеченность рейса']").waitFor({ timeout: 30000 });
}
const sec = p => p.locator("section[aria-label='Маршрут и обеспеченность рейса']");
const ok = (w, name, extra = {}) => { res.checks.push({ width: w, name, ...extra }); console.log("PASS", w, name); };

async function main(b, w, h) {
  fx = {};
  const { p, ctx, t0 } = await open(b, w, h, "R1.1155");
  await sec(p).locator("table", { hasText: "TRADECASE.QA.1155" }).waitFor({ timeout: 30000 });
  await sec(p).locator("article", { hasText: "AFTER" }).first().waitFor({ timeout: 30000 });
  res.timings["useful_" + w] = Date.now() - t0;
  const t = await sec(p).innerText();
  assert(/рейса склада № 33660/.test(t) && /Это план/.test(t) && /адрес не настроен/.test(t) && /время в пути не рассчитано/.test(t), t);
  assert(/карта не строится без координат/.test(t), "no fake map");
  ok(w, "LIVE native route context: stop order/address from current basis, depot unconfigured and duration unverified stated", { ms: res.timings["useful_" + w] });
  const row = await sec(p).locator("article", { hasText: "AFTER" }).first().innerText();
  assert(/Заказано\s*100/.test(row) && /Выехало\s*100/.test(row) && !/нет данных/.test(row), row);
  const href = await sec(p).locator("[data-help-id='tradecase.coverage.order']").first().getAttribute("href");
  assert(/tc_tab=ORDER&tc_open=AFTER/.test(href), href);
  ok(w, "FIXTURE(real read-model output) coverage row: ordered/reserved/picked/departed in base units, order link");
  assert(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "page overflow");
  await sec(p).screenshot({ path: path.join(SHOTS, `route-coverage-${w}.png`) });
  // Поздний ответ прежнего рейса не появляется в новом.
  fx.lateTrip = "R1.1155";
  await p.click("[data-help-id='tradecase.card.close']").catch(() => {});
  await openTrip(p, "R1.1156"); fx.lateTrip = null;
  await sec(p).locator("article", { hasText: "TRANSIT" }).first().waitFor({ timeout: 30000 });
  await p.waitForTimeout(2800);
  assert.equal(await sec(p).locator("article", { hasText: "AFTER" }).count(), 0, "late R1.1155 coverage leaked into R1.1156");
  ok(w, "FIXTURE late response of previous trip does not replace current trip");
  await ctx.close();
}

async function negatives(b, w, h) {
  fx = { route403: true, cover403: true };
  let s = await open(b, w, h, "R1.1155");
  await sec(s.p).locator(".tc-err", { hasText: "транспортного маршрута" }).waitFor({ timeout: 30000 });
  await sec(s.p).locator(".tc-err").nth(1).waitFor({ timeout: 30000 });
  assert.equal(await sec(s.p).locator("table").count(), 0);
  ok(w, "FIXTURE 403 on route and coverage: no data shown, explicit reasons");
  await s.ctx.close();
  fx = { unbound: true };
  s = await open(b, w, h, "R1.1155");
  await sec(s.p).locator(".tc-note", { hasText: "не привязан к рейсу склада" }).waitFor({ timeout: 30000 });
  ok(w, "FIXTURE unbound trip: route unknown (no native route read)");
  await s.ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try {
    for (const [w, h] of [[1440, 1000], [390, 844]]) { await main(b, w, h); await negatives(b, w, h); }
    assert.deepEqual(res.errors, []); assert.deepEqual(res.liveWrites, []);
    res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  res.asset = (await (await fetch(BASE)).text()).match(/assets\/index-[^"]+\.js/)?.[0];
  res.counts = { checks: res.checks.length, http: res.http.length, liveWrites: res.liveWrites.length, jsErrors: res.errors.length };
  fs.writeFileSync(path.join(OUT, "c0145-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, JSON.stringify(res.counts), JSON.stringify(res.timings));
  await b.close(); process.exit(res.status === "PASS" ? 0 : 1);
})();
