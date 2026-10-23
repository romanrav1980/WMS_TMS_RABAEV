// C-0161 «добивка после начала погрузки» на экране рейса (dev :3021) при 1440 и 390.
// ЖИВОЕ (GET): вход, документы склада 220793322 и настоящий рейс R1.1168 (уже выехал).
// FIXTURE: расчёт добивки POST …/topup-preview — (1) частичная погрузка: результат с местами и упаковкой; (2) 409 нескольких точек;
// (3) 409 рейс выехал. Это подставные ответы Python до restart/apply, не исход сервера. Других не-GET нет.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0161_BASE || "http://127.0.0.1:3021/", WH = 220793322, TRIP = "R1.1168";
const res = { base: BASE, checks: [], writes: [], errors: [], posts: [] };
const cors = { "access-control-allow-origin": "*" };
let fx = "partial";

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (m === "POST" && u.includes("/topup-preview")) {
    res.posts.push(req.postData());
    if (fx === "partial") return r.fulfill({ status: 200, headers: cors, json: { proposed_boxes: 12, loading_started: true,
      loaded: { places: 3, overhead_kg: "41.5", overhead_m3: "0.62" },
      items: [{ priority: 1, proposed_boxes: 12, uncovered_boxes: "8", need: { document_id: "N1", recipient_title: "C1", sku_title: "A", additional_boxes: "20" } }] } });
    return r.fulfill({ status: 409, headers: cors, json: { detail: { code: fx === "route" ? "TOPUP_AFTER_LOAD_ROUTE_ORDER_UNVERIFIED" : "TOPUP_TRIP_DEPARTED" } } });
  }
  if (m !== "GET" && !u.includes("/auth/")) { res.writes.push(m + " " + u); return r.abort(); }
  return r.continue();
}
const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };

async function width(b, w, h) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await ctx.route(u => u.href.includes(":8088/api/"), route);
  await p.goto(`${BASE}?page=tradecase&tc_wh=${WH}&tc_tab=TRIP&tc_open=${encodeURIComponent(TRIP)}`);
  const login = p.locator("input[type=password]"), panel = p.locator("[aria-label='Распределение места под добивку']");
  await Promise.race([login.waitFor({ timeout: 30000 }), panel.waitFor({ timeout: 30000 })]);
  if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
  await panel.waitFor({ timeout: 45000 }); ok(w, "LIVE trip R1.1168 opens with the top-up panel");
  const calc = async kind => {
    fx = kind;
    await panel.getByRole("button", { name: "Распределить место" }).click();
  };
  await panel.getByLabel("Или номер снимка").fill("N1"); await panel.getByRole("button", { name: "Добавить потребность" }).click();
  await panel.getByLabel("Допустимый возраст данных, мин").fill("60");
  await calc("partial"); await panel.getByText("Часть основного груза уже в машине: мест 3").waitFor();
  const t = await panel.innerText(); assert(/учтены один раз/.test(t) && /\+41\.5 кг/.test(t) && /Паллетоместа и порядок укладки не проверялись/.test(t), t);
  ok(w, "FIXTURE partial load: result says main counted once, packaging +kg/+m³, floor not checked");
  await calc("route"); await panel.getByText("порядок выгрузки не подтверждён данными").waitFor(); ok(w, "FIXTURE several stops: readable refusal");
  await calc("departed"); await panel.getByText("Рейс уже выехал").waitFor(); ok(w, "FIXTURE departed: readable refusal");
  const bad = await panel.locator("button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every top-up button has title and help id");
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(over <= 1, "overflow " + over); ok(w, "no horizontal page scroll");
  const href = await panel.locator("a[href*='help/tradecase-documents.html']").first().getAttribute("href");
  const help = await ctx.request.get(new URL(href, BASE).href); assert.equal(help.status(), 200);
  assert((await help.text()).includes("Если погрузка уже началась")); ok(w, "static help link answers 200 and has the after-loading section");
  await panel.screenshot({ path: path.join(SHOTS, `topup-after-load-${w}.png`) });
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 1000); await width(b, 390, 844); assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.writes, []); res.status = "PASS"; }
  catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0161-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, "checks");
  process.exit(res.status === "PASS" ? 0 : 1);
})();
