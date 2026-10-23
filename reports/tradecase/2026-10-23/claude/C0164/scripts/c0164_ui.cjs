// C-0164 «Подтверждение состава заказов» во вкладке «Обмен» (dev :3021) при 1440 и 390.
// ЖИВОЕ (GET): вход и страница обмена склада 210564699. FIXTURE: GET order-compositions и POST report (native NOT_APPLIED, маршрут
// на :8088 ещё не загружен), 403 списка. Это подставные ответы, не исход сервера. Других не-GET нет.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0164_BASE || "http://127.0.0.1:3021/", WH = 210564699;
const res = { base: BASE, checks: [], writes: [], errors: [], posts: [] };
const cors = { "access-control-allow-origin": "*" };
let fx = {};
const row = (id, status, extra = {}) => ({ warehouse_id: WH, order_id: id, order_version: 1, assembly_closed: true, live_carriers: 2, status, ...extra });
const sent = { composition_no: 1, carriers: 2, units: 5, codes: 5, source_id: "TC03.SAP", skm_id: "TC03.SKM", sap_status: "WAITING", sap_reason: null, skm_status: "WAITING", skm_reason: null, change_reason: null };

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (u.includes("/order-compositions?") && m === "GET") {
    if (fx.denied) return r.fulfill({ status: 403, headers: cors, json: { detail: { code: "TRADECASE_ACCESS_DENIED" } } });
    return r.fulfill({ status: 200, headers: cors, json: { warehouse_id: WH, has_more: false, items: [
      row("O.OPEN", "ASSEMBLY_OPEN", { assembly_closed: false, live_carriers: 1 }), row("O.NEW", "NOT_REPORTED"),
      row("O.WAIT", "WAITING", { ...sent, sap_status: "ACCEPTED" }),
      row("O.REJ", "REJECTED", { ...sent, sap_status: "ACCEPTED", skm_status: "REJECTED", skm_reason: "CODE_NOT_IN_CIRCULATION" }),
      row("O.CHG", "CHANGED", { ...sent, change_reason: "SKM_CHANGED" }),
      row("O/OK", "CONFIRMED", { ...sent, sap_status: "ACCEPTED", skm_status: "ACCEPTED" })] } });
  }
  if (u.endsWith("/order-compositions/report") && m === "POST") { res.posts.push(req.postDataJSON()); return r.fulfill({ status: 200, headers: cors, json: row("O.NEW", "WAITING", sent) }); }
  if (u.includes("/supply-transfers") && m === "GET") return r.fulfill({ status: 200, headers: cors, json: { warehouse_id: WH, has_more: false, items: [] } });
  if (m !== "GET" && !u.includes("/auth/")) { res.writes.push(m + " " + u); return r.abort(); }
  return r.continue();
}
const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };

async function width(b, w, h) {
  fx = {}; res.posts = [];
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await ctx.route(u => u.href.includes(":8088/api/"), route);
  const open = async () => {
    await p.goto(`${BASE}?page=tradecase&tc_wh=${WH}&tc_tab=MESSAGES`);
    const login = p.locator("input[type=password]");
    await Promise.race([login.waitFor({ timeout: 30000 }), panel.waitFor({ timeout: 30000 })]);
    if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
    await panel.getByText("O.OPEN").waitFor({ timeout: 45000 });
  };
  const panel = p.locator("[aria-label='Подтверждение состава заказов']");
  await open(); ok(w, "LIVE exchange tab opens with the composition panel");
  const t = await panel.innerText();
  assert(/сборка не закрыта/.test(t) && /сборка закрыта, состав не отправлен/.test(t) && /SAP TC03\.SAP: принял · СКМ TC03\.SKM: ждём ответа/.test(t)
    && /СКМ TC03\.SKM: отклонил \(CODE_NOT_IN_CIRCULATION\)/.test(t) && /сменилась действующая СКМ: отправьте состав заново/.test(t) && /состав подтверждён/.test(t), t);
  ok(w, "FIXTURE: open assembly, closed-not-reported, waiting SKM, SKM rejection, SKM change, confirmed — each system separately");
  assert(await panel.locator("li", { hasText: "O.OPEN" }).getByRole("button", { name: "Отправить состав" }).count() === 0
    && await panel.locator("li", { hasText: "O.WAIT" }).getByRole("button", { name: "Отправить состав" }).count() === 0);
  ok(w, "no report button while assembly is open or the answer is awaited");
  await panel.locator("li", { hasText: "O.NEW" }).getByRole("button", { name: "Отправить состав" }).click();
  await panel.getByText("Состав заказа O.NEW отправлен на подтверждение.").waitFor();
  assert.deepStrictEqual(res.posts, [{ warehouse_id: WH, order_id: "O.NEW" }]); ok(w, "FIXTURE report posts the order once");
  await panel.locator("li", { hasText: "O/OK" }).getByRole("button", { name: "Открыть заказ" }).click();
  await p.waitForFunction(() => /tc_tab=ORDER/.test(location.search) && new URLSearchParams(location.search).get("tc_open") === "O/OK", null, { timeout: 15000 });
  ok(w, "open order goes to the existing ORDER document in place");
  await open();
  const bad = await panel.locator("button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every panel button has title and help id");
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(over <= 1, "overflow " + over); ok(w, "no horizontal page scroll");
  const href = await panel.locator("a[href*='help/tradecase-documents.html']").first().getAttribute("href");
  const help = await ctx.request.get(new URL(href, BASE).href); assert.equal(help.status(), 200); assert((await help.text()).includes('id="composition-ack"')); ok(w, "static help link answers 200 with the composition section");
  await panel.screenshot({ path: path.join(SHOTS, `composition-ack-${w}.png`) });
  fx.denied = true; await panel.getByRole("button", { name: "Обновить" }).click();
  await panel.getByText("Состояние не прочитано").waitFor(); assert(await panel.locator("li").count() === 0); ok(w, "FIXTURE 403 clears the list (no stale rows)");
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 1000); await width(b, 390, 844); assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.writes, []); res.status = "PASS"; }
  catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0164-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, "checks");
  process.exit(res.status === "PASS" ? 0 : 1);
})();
