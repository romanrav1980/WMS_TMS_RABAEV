// C-0139: рейс → исполнение, привязка, выкуп после сборки и в пути. ЖИВОЕ: вход admin и GET склада 215590763 (исполнение R1.1155,
// native-рейс 33660, груз в пути T7.LOAD.1155, коды CASE). FIXTURE (перехват): ответы POST binding/buyouts, режим основания
// (AFTER_PICK→IN_TRANSIT), составы с резервом/удержанием/BLC/МРЦ «200.00», 403 и задержка исполнения. Ни один POST не доходит до сервера.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0139_BASE || "http://127.0.0.1:3021/", WH = "215590763";
const res = { http: [], posts: [], liveWrites: [], errors: [], checks: [], timings: {} };
let mode = [], transitMode = null, fixCase = false, execMode = null;
const cors = { "access-control-allow-origin": "*" };
const unit = (i, o) => ({ physical_unit_key: i.toString(16).padStart(64, "0"), sku_id: "A", owner_id: "SNS", mrc: "200", expiry_date: "2030-01-01", pallet_identifier: "CASE-FIX",
  cell: "T6W554eebf3", mark_state: "VALID", base_quantity: "1", base_uom: "EA", hard_reserved: false, buyout_hold: false, allocation_enabled: false, ...o });

async function start(b, w, h, q) {
  const p = await (await b.newContext({ viewport: { width: w, height: h } })).newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  p.on("response", r => { if (/\/api\/(tradecase|admin\/transport)\//.test(r.url())) res.http.push(w + " " + r.request().method() + " " + r.status() + " " + r.url().replace(/^.*\/api\//, "/api/").slice(0, 110)); });
  await p.route(u => u.href.includes(":8088/api/"), async r => {
    const req = r.request(), m = req.method(), u = req.url();
    if (m === "OPTIONS") return r.continue();
    if (m === "GET") {
      if (execMode === "403" && u.includes("/execution")) return r.fulfill({ status: 403, json: { detail: { code: "ACCESS_DENIED" } }, headers: cors });
      if (execMode === "late" && u.includes("/execution")) await new Promise(x => setTimeout(x, 3000));
      if (transitMode && u.includes("/documents/ORDER/TC6.FIN.AFTER")) { const j = await (await r.fetch()).json(); j.payload.buyout_mode = transitMode; return r.fulfill({ json: j, headers: cors }); }
      if (fixCase === "late" && u.includes("pallet_identifier=CASE-FIX")) await new Promise(x => setTimeout(x, 900));
      if (fixCase && u.includes("pallet_identifier=CASE-FIX")) return r.fulfill({ json: { warehouse_id: +WH, has_more: false, next_after: null,
        owner_scope_filtered: fixCase === "hidden", items: [unit(1, { hard_reserved: true }), unit(2, { hard_reserved: true, mrc: "200.00" }), unit(3, { buyout_hold: true }), unit(4, { owner_id: "BLC" }), unit(5, { mrc: "201" })] }, headers: cors });
      if (fixCase && u.includes("/stock/transit")) { const after = new URL(u).searchParams.get("after");
        const t = o => unit(o.i, { cell: null, location_kind: "VEHICLE_TRANSIT", last_warehouse_cell: "T6W554eebf3", pallet_identifier: "CASELOT:FIX", ...o });
        return r.fulfill({ json: after ? { warehouse_id: +WH, has_more: false, next_after: null, items: [t({ i: 13, mrc: "200.00" }), t({ i: 14, owner_id: "BLC" })] }
          : { warehouse_id: +WH, has_more: true, next_after: "p2", items: [t({ i: 11 }), t({ i: 12, buyout_hold: true })] }, headers: cors }); }
      return r.continue();
    }
    const body = JSON.parse(req.postData()), md = mode.shift() || "abort", kind = u.endsWith("/binding") ? "binding" : u.endsWith("/buyouts") ? "buyout" : null;
    if (!kind) { res.liveWrites.push(m + " " + u); return r.abort(); }
    res.posts.push({ kind, mode: md, body });
    if (md === "abort") return r.abort("connectionreset");
    if (md.startsWith("409:")) return r.fulfill({ status: 409, json: { detail: { code: md.slice(4) } }, headers: cors });
    return r.fulfill({ json: kind === "binding" ? { native_task_id: body.native_task_id, binding_version: 2, replayed: md === "replay" }
      : { buyout_id: body.buyout_id, status: "PENDING", requested_units: body.unit_keys.length }, headers: cors });
  });
  await p.goto(BASE + "?page=tradecase" + q);
  if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  return p;
}
const rows = p => p.locator(".tc-body .tc-table tbody tr");
async function openDoc(p, tab, id) { await chooseTabUI(p, tab); await rows(p).first().waitFor({ timeout: 30000 });
  await p.locator(".tc-body .tc-table tbody tr", { hasText: id }).first().getByRole("button", { name: "Открыть" }).click(); await p.waitForSelector(".tc-card .tc-fields"); }

async function live(b, w, h) {
  const p = await start(b, w, h, "&tc_wh=" + WH + "&tc_tab=TRIP"); const r = {};
  const t0 = Date.now(); await openDoc(p, "TRIP", "R1.1155"); await p.waitForSelector(".tc-card .tc-bind .tc-fields"); r.execMs = Date.now() - t0;
  r.exec = await p.locator(".tc-card .tc-bind").first().innerText();
  assert(/№ 33660/.test(r.exec) && /транспортный документ готов/.test(r.exec) && /не означает доставку/.test(r.exec) && /T7\.LOAD\.1155/.test(r.exec) && /выехал/.test(r.exec), r.exec);
  r.link = await p.locator("[data-help-id='tradecase.trip.open']").getAttribute("href"); assert(/\/wms-admin\/transport-loading\.html\?trip_id=33660$/.test(r.link), r.link);
  await p.click("[data-help-id='tradecase.trip.rebind']"); await p.fill("[data-help-id='tradecase.trip.native']", "33660"); await p.press("[data-help-id='tradecase.trip.native']", "Enter");
  await p.waitForSelector(".tc-bindform .tc-review"); r.native = await p.locator(".tc-bindform .tc-review").innerText();
  assert(/TC7QA1155/.test(r.native) && !/не совпадает/.test(r.native), r.native);
  await p.screenshot({ path: path.join(OUT, `t1_trip_${w}.png`) });
  // В пути — полностью живое чтение (C-0140): основание TC7.FIN.TRANSIT, рейс R1.1156, погрузка T7.LOAD.1156 уже 40 BLC → для SNS→BLC подходящих 0.
  await openDoc(p, "ORDER", "TC7.FIN.TRANSIT"); await p.locator("[data-help-id='tradecase.buyout.create']").first().click();
  await p.selectOption("[data-help-id='tradecase.buyout.demand']", { label: "TRANSIT / строка 1: 40" });
  await p.selectOption("[data-help-id='tradecase.buyout.trip']", "R1.1156"); await p.waitForSelector("[data-help-id='tradecase.buyout.loadop']");
  await p.selectOption("[data-help-id='tradecase.buyout.loadop']", "T7.LOAD.1156"); const t1 = Date.now(); await p.click("[data-help-id='tradecase.transit.load']");
  await p.waitForSelector(".tc-review", { timeout: 30000 }); r.transitMs = Date.now() - t1; r.transit = await p.locator(".tc-review").innerText();
  assert(/Кодов в погрузке: 40/.test(r.transit) && /\): 0\./.test(r.transit), r.transit);
  r.untitled = await p.evaluate(() => [...document.querySelectorAll(".tc button, .tc a[role=button], .tc select")].filter(e => !(e.title || e.querySelector("title")) || !e.dataset.helpId).map(e => e.outerHTML.slice(0, 80)));
  assert.deepEqual(r.untitled, []); r.overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(r.overflow <= 0, "overflow " + r.overflow);
  await p.screenshot({ path: path.join(OUT, `t2_transit_live_${w}.png`) });
  res["live" + w] = r; res.timings["exec" + w] = r.execMs; res.timings["transit40_" + w] = r.transitMs;
  res.checks.push("live_trip_execution_link_native_check_transit_blc_excluded_" + w); await p.context().close();
}

async function fixtures(b) {
  const p = await start(b, 1440, 1000, "&tc_wh=" + WH + "&tc_tab=TRIP");
  await p.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith("tradecase.")).forEach(k => localStorage.removeItem(k)));
  // (1) Привязка: обрыв → сохранено → повтор тем же телом → перечитано исполнение.
  await openDoc(p, "TRIP", "R1.1155"); await p.click("[data-help-id='tradecase.trip.rebind']"); await p.fill("[data-help-id='tradecase.trip.native']", "33660"); await p.press("[data-help-id='tradecase.trip.native']", "Enter");
  await p.waitForSelector("[data-help-id='tradecase.trip.bind']"); mode = ["abort", "replay"]; await p.locator("[data-help-id='tradecase.trip.bind']").dblclick();
  await p.waitForSelector(".tc-msg.warn >> text=Результат неизвестен"); await p.click("[data-help-id='tradecase.retry']"); await p.waitForSelector(".tc-card .tc-bind [data-help-id='tradecase.trip.rebind']");
  const bp = res.posts.filter(x => x.kind === "binding"); assert.equal(bp.length, 2); assert.deepEqual(bp[0].body, bp[1].body);
  assert.deepEqual({ n: bp[0].body.native_task_id, t: bp[0].body.expected_trip_version, v: bp[0].body.expected_binding_version }, { n: 33660, t: 1, v: 1 }); res.checks.push("binding_unknown_exact_retry_then_fresh_execution");
  // (2) После сборки: исходный заказ + CASE; резерв допустим, удержание/BLC/МРЦ 201 исключены, «200.00» = «200».
  fixCase = true; await openDoc(p, "ORDER", "TC6.FIN.AFTER"); await p.locator("[data-help-id='tradecase.buyout.create']").first().click();
  await p.fill("[data-help-id='tradecase.buyout.scan']", "CASE-FIX");
  assert(await p.locator("button[data-help-id='tradecase.buyout.load']").isDisabled()); // без исходного заказа чтение недоступно
  await p.selectOption("[data-help-id='tradecase.buyout.demand']", { label: "AFTER / строка 1: 100" }); await p.press("[data-help-id='tradecase.buyout.scan']", "Enter");
  // Root: scoped partial composition cannot be approved; an old scan cannot refill a changed field.
  fixCase = "hidden"; await p.press("[data-help-id='tradecase.buyout.scan']", "Enter");
  await p.waitForSelector(".tc-err >> text=Часть состава скрыта"); assert.equal(await p.locator(".tc-review").count(), 0); res.checks.push("root_hidden_owner_composition_blocks_buyout");
  fixCase = "late"; await p.press("[data-help-id='tradecase.buyout.scan']", "Enter"); await p.waitForTimeout(100);
  await p.fill("[data-help-id='tradecase.buyout.scan']", "CASE-OTHER"); await p.waitForTimeout(1200); assert.equal(await p.locator(".tc-review").count(), 0); res.checks.push("root_old_composition_ignored_after_scan_change");
  fixCase = true; await p.fill("[data-help-id='tradecase.buyout.scan']", "CASE-FIX"); await p.press("[data-help-id='tradecase.buyout.scan']", "Enter");
  await p.waitForSelector(".tc-review"); res.afterReview = await p.locator(".tc-review").innerText(); assert(/\): 2\./.test(res.afterReview) && /исходный заказ AFTER\/1/.test(res.afterReview), res.afterReview);
  mode = ["ok"]; await p.click("[data-help-id='tradecase.buyout.send']"); await p.waitForFunction(() => new URLSearchParams(location.search).get("tc_tab") === "BUYOUTS");
  const a = res.posts.at(-1).body; assert.deepEqual([a.demand_order_id, a.demand_line_id, a.load_operation_id, a.unit_keys.length], ["AFTER", "1", undefined, 2]); res.checks.push("after_pick_demand_case_hard_allowed_hold_blc_mrc_normalized");
  // (3) В пути: две страницы груза, удержание и BLC исключены, «200.00» подходит; место — «в пути», без последнего адреса склада.
  await openDoc(p, "ORDER", "TC7.FIN.TRANSIT"); await p.locator("[data-help-id='tradecase.buyout.create']").first().click();
  await p.selectOption("[data-help-id='tradecase.buyout.demand']", { label: "TRANSIT / строка 1: 40" }); await p.selectOption("[data-help-id='tradecase.buyout.trip']", "R1.1155");
  await p.waitForSelector("[data-help-id='tradecase.buyout.loadop']"); await p.selectOption("[data-help-id='tradecase.buyout.loadop']", "T7.LOAD.1155"); await p.click("[data-help-id='tradecase.transit.load']");
  await p.waitForSelector(".tc-review"); res.transitReview = await p.locator(".tc-review").innerText();
  assert(/Кодов в погрузке: 4/.test(res.transitReview) && /\): 2\./.test(res.transitReview) && /в пути: погрузка T7\.LOAD\.1155/.test(res.transitReview) && !/T6W554eebf3/.test(res.transitReview.replace(/Ключи выбранных кодов[\s\S]*/, "")), res.transitReview);
  await p.screenshot({ path: path.join(OUT, "t3_transit_fixture_1440.png") });
  mode = ["409:OPERATION_CONTENT_CONFLICT"]; await p.click("[data-help-id='tradecase.buyout.send']"); await p.waitForSelector(".tc-msg.bad >> text=команда сохранена");
  const tb = res.posts.at(-1).body; assert.deepEqual([tb.demand_order_id, tb.demand_line_id, tb.load_operation_id, tb.unit_keys.length], ["TRANSIT", "1", "T7.LOAD.1155", 2]);
  assert(await p.locator("[data-help-id='tradecase.retry']").count() === 1); fixCase = false; res.checks.push("in_transit_full_pages_blc_hold_excluded_vehicle_place_conflict_kept");
  await p.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith("tradecase.")).forEach(k => localStorage.removeItem(k)));
  // (4) 403 исполнения убирает данные; (5) поздний ответ исполнения не попадает в карточку другого документа.
  execMode = "403"; await openDoc(p, "TRIP", "R1.1155"); await p.waitForSelector(".tc-card .tc-bind .tc-err"); assert.equal(await p.locator(".tc-card .tc-bind .tc-fields").count(), 0); res.checks.push("execution_403_clears");
  execMode = "late"; await p.click("[data-help-id='tradecase.refresh']"); await p.waitForTimeout(200); await openDoc(p, "ORDER", "AFTER"); await p.waitForTimeout(3500);
  assert.equal(await p.locator(".tc-card >> text=Фактическое исполнение рейса").count(), 0); execMode = null; res.checks.push("late_execution_ignored");
  await p.context().close();
}

// Root T08: live Oracle/API arithmetic preview, never dispatch approval or actual stock.
async function capacityLive(b, width, height) {
 const fixture = JSON.parse(fs.readFileSync("C:/projects/TMS/runtime/test-evidence/tradecase/2026-10-19/T08/capacity-fixture.json", "utf8"));
 const p = await start(b, width, height, "&tc_wh=" + fixture.a.warehouse_id + "&tc_tab=TRIP");
 await openDoc(p, "TRIP", "TC8.R1"); await p.fill("[data-help-id='tradecase.capacity.sku']", "A");
 await p.fill("[data-help-id='tradecase.capacity.quantity']", "60"); const started = Date.now(); await p.click("[data-help-id='tradecase.capacity.calculate']");
 await p.waitForSelector(".tc-capacity-result"); const text = await p.locator(".tc-capacity-result").innerText();
 assert(/40/.test(text) && /20/.test(text) && /6000/.test(text) && /60/.test(text), text);
 assert.equal(await p.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
 const href = await p.locator(".tc-capacity a").first().getAttribute("href"); assert(href.endsWith("#capacity"), href);
 res.timings["capacity"+width] = Date.now()-started;
 await p.screenshot({path:path.join(OUT, "root_capacity_"+width+".png")});
 await p.fill("[data-help-id='tradecase.capacity.quantity']", "80"); assert.equal(await p.locator(".tc-capacity-result").count(), 0);
 res.checks.push("root_live_capacity_600_plus40_remainder20_"+width); await p.context().close();
}

(async () => {
  const b = await chromium.launch();
  await live(b, 1440, 1000); await live(b, 390, 844); await fixtures(b); await capacityLive(b,1440,1000); await capacityLive(b,390,844);
  assert.deepEqual(res.liveWrites, []); assert.deepEqual(res.errors, []); res.status = "PASS";
  res.labels = { live: "admin login + GET 215590763 (execution, native trip 33660, transit T7.LOAD.1155, documents)", fixture: "POST binding/buyouts answers, basis mode IN_TRANSIT, CASE/transit compositions, 403, delay — intercepted" };
  res.apiVolume = { gets: res.http.filter(x => / GET /.test(x)).length };
  fs.writeFileSync(path.join(__dirname, "..", "c0139_result.json"), JSON.stringify(res, null, 1));
  console.log(JSON.stringify({ status: res.status, checks: res.checks, posts: res.posts.map(x => x.kind + ":" + x.mode), timings: res.timings, gets: res.apiVolume.gets }, null, 1)); await b.close();
})().catch(e => { console.error(e.message); console.error(JSON.stringify({ checks: res.checks, errors: res.errors, posts: res.posts.map(x => x.kind + ":" + x.mode), liveWrites: res.liveWrites })); process.exit(1); });

async function chooseTabUI(p, id) { const mobile=p.locator("[data-help-id=\"tradecase.mobile-tab\"]"); if(p.viewportSize().width<=600) await mobile.selectOption(id); else await p.click(`[data-help-id='tradecase.tab.${id}']`); }
