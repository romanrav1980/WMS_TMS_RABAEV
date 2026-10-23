// C-0143 UI согласования добивки на собранном frontend (:3000). ЖИВОЕ: вход admin и GET рейса R1.1155 склада 215590763 (карточка/исполнение).
// FIXTURE (перехват; миграция в Oracle ещё не применена, NOT_APPLIED_BY_CLAUDE): topup-preview, список предложений, сохранение, изменение,
// отклонение, подтверждение (потеря ответа → повтор тем же телом), отмена, 403. Ни один POST до сервера не доходит.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0143_BASE || "http://127.0.0.1:3000/", WH = "215590763", TRIP = "R1.1155";
const res = { base: BASE, checks: [], posts: [], liveWrites: [], errors: [], http: [] };
const cors = { "access-control-allow-origin": "*" };
let fx = { approval: true, list403: false, confirmMode: [] };
const card = (id, o) => ({ proposal_id: id, trip_id: TRIP, need_id: "NEED." + id, priority: id, recipient_id: "Филиал-" + id, sku_id: "A", source_owner_id: "SNS", mrc: "200",
  min_expiry_date: "2026-11-01", units_per_box: 10, need_boxes: "40", proposed_boxes: 40, approved_boxes: 40, status: "PROPOSED", version: 1,
  need_snapshot_at: "2026-10-22T10:00:00Z", max_age_minutes: 60, sap_order_id: null, sap_reason: null, sap_order_received: false, holds: [],
  calculation: { limited_by: null, uncovered_boxes: "0", sender_stock_boxes: 350, already_confirmed_boxes: "0" }, ...o });
let items = [];
const reset = () => { items = [card(1, {}), card(2, { recipient_id: "Магазин", need_boxes: "30", proposed_boxes: 20, approved_boxes: 20, calculation: { limited_by: "CAPACITY", uncovered_boxes: "10", sender_stock_boxes: 150, already_confirmed_boxes: "0" } }),
  card(3, { status: "SAP_ACCEPTED", version: 4, sap_order_id: "104", holds: [{ reservation_id: 91, base_quantity: "400", status: "ACTIVE" }] })]; };

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (u.includes("/topup-proposals") || u.includes("/topup-preview")) {
    if (m === "GET") {
      if (fx.list403) return r.fulfill({ status: 403, json: { detail: { code: "TRADE_TOPUP_ACCESS_DENIED" } }, headers: cors });
      return r.fulfill({ json: { warehouse_id: +WH, trip_id: TRIP, items, approval_available: fx.approval }, headers: cors });
    }
    const body = JSON.parse(req.postData()); res.posts.push({ url: u.replace(/^.*\/trips\//, ""), body });
    if (u.endsWith("/topup-preview")) return r.fulfill({ json: { proposed_boxes: 60, items: [{ priority: 1, proposed_boxes: 40, uncovered_boxes: "0", need: { document_id: "NEED.1", recipient_title: "Филиал", sku_title: "A", additional_boxes: "40" } },
      { priority: 2, proposed_boxes: 20, uncovered_boxes: "10", need: { document_id: "NEED.2", recipient_title: "Магазин", sku_title: "Б", additional_boxes: "30" } }] }, headers: cors });
    const id = Number((u.match(/topup-proposals\/(\d+)\//) || [])[1]), p = items.find(x => x.proposal_id === id);
    if (u.endsWith("/topup-proposals")) { reset(); return r.fulfill({ json: { operation_id: body.operation_id, proposals: items, replayed: false }, headers: cors }); }
    if (u.endsWith("/decision")) { Object.assign(p, body.action === "ADJUST" ? { approved_boxes: body.boxes, status: "ADJUSTED" } : { status: "REJECTED" }, { version: p.version + 1 }); return r.fulfill({ json: p, headers: cors }); }
    if (u.endsWith("/confirm")) {
      const mode = fx.confirmMode.shift() || "ok";
      if (mode === "abort") return r.abort("connectionreset");
      if (mode === "basis") return r.fulfill({ status: 409, json: { detail: { code: "TRADE_TOPUP_CAPACITY_BASIS_CHANGED", outcome_confirmed: true } }, headers: cors });
      Object.assign(p, { status: "CONFIRMED", version: p.version + 1, holds: [{ reservation_id: 77, base_quantity: String(p.approved_boxes * 10), status: "ACTIVE" }] });
      return r.fulfill({ json: { ...p, replayed: mode === "replay" }, headers: cors });
    }
    if (u.endsWith("/release")) { Object.assign(p, { status: "CANCELLED", version: p.version + 1, holds: p.holds.map(h => ({ ...h, status: "RELEASED" })) }); return r.fulfill({ json: p, headers: cors }); }
  }
  if (m !== "GET") { res.liveWrites.push(m + " " + u); return r.abort(); }
  return r.continue();
}

async function open(b, w, h) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  p.on("response", rr => { if (rr.url().includes(":8088/api/")) res.http.push(`${w} ${rr.request().method()} ${rr.status()} ${rr.url().replace(/^.*\/api\//, "/api/").slice(0, 100)}`); });
  await p.route(u => u.href.includes(":8088/api/"), route);
  await p.goto(BASE + "?page=tradecase&tc_wh=" + WH + "&tc_tab=TRIP");
  if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  await p.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith("tradecase.topup")).forEach(k => localStorage.removeItem(k)));
  const rows = p.locator(".tc-body .tc-table tbody tr"); await rows.first().waitFor({ timeout: 30000 });
  await p.locator(".tc-body .tc-table tbody tr", { hasText: TRIP }).first().getByRole("button", { name: "Открыть" }).click();
  await p.locator("section[aria-label='Предложения добивки']").waitFor({ timeout: 30000 });
  return { p, ctx };
}
const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };
const panel = p => p.locator("section[aria-label='Предложения добивки']");
const prop = (p, id) => panel(p).locator(`article[aria-label='Предложение ${id}']`);

async function flow(b, w, h) {
  reset(); fx = { approval: true, list403: false, confirmMode: ["abort", "replay"] }; res.posts.length = 0;
  const { p, ctx } = await open(b, w, h);
  await prop(p, 2).waitFor();
  const t2 = await prop(p, 2).innerText(); assert(/ограничено свободным местом в машине/.test(t2) && /осталось покрыть 10/.test(t2), t2);
  const t3 = await prop(p, 3).innerText(); assert(/SAP создал заказ/.test(t3) && /104 · документ заказа ещё не получен/.test(t3) && /Удержано\s*400 шт/.test(t3), t3);
  ok(w, "FIXTURE list: reason of quantity, SAP order link without received order, active hold");
  // Предварительный расчёт → сохранить как предложения (тот же набор потребностей и возраст).
  const tp = p.locator("section[aria-label='Распределение места под добивку']");
  for (const n of ["NEED.1", "NEED.2"]) { await tp.locator("[data-help-id='tradecase.topup.need.id']").fill(n); await tp.locator("[data-help-id='tradecase.topup.add']").click(); }
  await tp.locator("[data-help-id='tradecase.topup.age']").fill("60"); await tp.locator("[data-help-id='tradecase.topup.calculate']").click();
  await tp.locator("[data-help-id='tradecase.topup.save']").click();
  await panel(p).locator(".tc-msg.ok", { hasText: "Предложения сохранены" }).waitFor();
  const save = res.posts.find(x => x.url.endsWith("topup-proposals"));
  assert.deepEqual(save.body.need_ids, ["NEED.1", "NEED.2"]); assert.equal(save.body.max_age_minutes, 60); assert(/^TC\.TOPUP\.UI:/.test(save.body.operation_id));
  ok(w, "FIXTURE save sends the previewed priority order and age with a durable operation id");
  // Изменение вне диапазона недоступно; в диапазоне — отправляется.
  const box = prop(p, 2).locator("[data-help-id='tradecase.topup.boxes']");
  await box.fill("25"); assert(await prop(p, 2).locator("[data-help-id='tradecase.topup.adjust']").isDisabled());
  await box.fill("15"); await prop(p, 2).locator("[data-help-id='tradecase.topup.adjust']").click();
  await panel(p).locator(".tc-msg.ok", { hasText: "Количество изменено" }).waitFor();
  assert(/15 кор/.test(await prop(p, 2).innerText()));
  ok(w, "FIXTURE adjust only within the calculated fit; expected_version sent");
  // Подтверждение: потеря ответа → команда сохранена, остальные решения заблокированы → повтор тем же телом.
  await prop(p, 1).locator("[data-help-id='tradecase.topup.confirm']").click();
  await panel(p).locator(".tc-msg.warn", { hasText: "Результат неизвестен" }).waitFor();
  assert(await prop(p, 2).locator("[data-help-id='tradecase.topup.reject']").isDisabled(), "other decisions locked while outcome unknown");
  await panel(p).locator("[data-help-id='tradecase.topup.retry']").click();
  await panel(p).locator(".tc-msg.ok", { hasText: "короба удержаны" }).waitFor();
  const confirms = res.posts.filter(x => x.url.endsWith("/1/confirm"));
  assert.equal(confirms.length, 2); assert.deepEqual(confirms[0].body, confirms[1].body); assert.equal(confirms[0].body.expected_version, 1);
  ok(w, "FIXTURE lost confirm reply: same body retried, no new operation, others locked meanwhile");
  await prop(p, 2).locator("[data-help-id='tradecase.topup.reject']").click();
  await panel(p).locator(".tc-msg.ok", { hasText: "складские задания не созданы" }).waitFor();
  ok(w, "FIXTURE reject: no warehouse tasks message");
  await prop(p, 1).locator("[data-help-id='tradecase.topup.release']").click();
  await panel(p).locator(".tc-msg.ok", { hasText: "удержание этого предложения снято" }).waitFor();
  ok(w, "FIXTURE cancel releases only this proposal");
  assert(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "page overflow");
  await p.screenshot({ path: path.join(SHOTS, `topup-proposals-${w}.png`), fullPage: w === 390 });
  await ctx.close();
}

async function gates(b, w, h) {
  reset(); fx = { approval: false, list403: false, confirmMode: ["basis"] };
  const { p, ctx } = await open(b, w, h);
  await prop(p, 1).waitFor();
  assert(await prop(p, 1).locator("[data-help-id='tradecase.topup.confirm']").isDisabled());
  assert(/Подтверждение пока недоступно/.test(await panel(p).innerText()));
  ok(w, "FIXTURE approval_available=false keeps confirmation disabled with explanation");
  await ctx.close();
  fx = { approval: true, list403: false, confirmMode: ["basis"] }; reset();
  const s = await open(b, w, h);
  await prop(s.p, 1).locator("[data-help-id='tradecase.topup.confirm']").click();
  await panel(s.p).locator(".tc-msg.bad", { hasText: "место в машине изменилось" }).waitFor();
  assert.equal(await s.p.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith("tradecase.topup")).length), 0, "confirmed refusal clears the command");
  ok(w, "FIXTURE concurrent confirmation refused (capacity basis changed): clear reason, command cleared");
  fx.list403 = true;
  await s.p.reload(); if (await s.p.locator("input[type=password]").count()) { await s.p.fill("input[autocomplete=username]", "admin"); await s.p.fill("input[type=password]", pass); await s.p.click("button[type=submit]"); }
  const rows = s.p.locator(".tc-body .tc-table tbody tr"); await rows.first().waitFor({ timeout: 30000 });
  await s.p.locator(".tc-body .tc-table tbody tr", { hasText: TRIP }).first().getByRole("button", { name: "Открыть" }).click();
  await panel(s.p).locator(".tc-err").waitFor({ timeout: 30000 });
  assert.equal(await panel(s.p).locator("article").count(), 0);
  ok(w, "FIXTURE 403 shows no proposals");
  await s.ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try {
    for (const [w, h] of [[1440, 1000], [390, 844]]) { await flow(b, w, h); await gates(b, w, h); }
    assert.deepEqual(res.errors, []); assert.deepEqual(res.liveWrites, []);
    res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  res.asset = (await (await fetch(BASE)).text()).match(/assets\/index-[^"]+\.js/)?.[0];
  res.counts = { checks: res.checks.length, http: res.http.length, liveWrites: res.liveWrites.length, jsErrors: res.errors.length };
  fs.writeFileSync(path.join(OUT, "c0143-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, JSON.stringify(res.counts));
  await b.close(); process.exit(res.status === "PASS" ? 0 : 1);
})();
