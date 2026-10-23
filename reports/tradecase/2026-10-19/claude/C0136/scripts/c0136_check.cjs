// C-0136: выкупы и разделение СНС/BLC. ЖИВОЕ: вход admin и GET склада 211559882 (выкупы, основания, все страницы кодов паллеты).
// FIXTURE (перехват в браузере): ответы POST /buyouts (200, обрыв, replay, 409), GET карточки созданного UI-выкупа, 403, задержка ответа,
// изменение buyout_mode для проверки недоступности. Ни один POST не доходит до сервера. Пароль не печатается.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0136_BASE || "http://127.0.0.1:3021/", WH = "211559882", PALLET = "690000000993299668";
const KEY = "tradecase.buyout:http://127.0.0.1:8088:admin:" + WH;
const res = { http: [], posts: [], liveWrites: [], errors: [], checks: [] };
let mode = [], sortMode = [], afterPick = false, late = false;
const cors = { "access-control-allow-origin": "*" };
const fakeBuyout = b => ({ buyout_id: b.buyout_id, warehouse_id: +WH, basis_order_id: b.basis_order_id, basis_line_id: b.basis_line_id, basis_version: b.expected_basis_version,
  sku_id: "A", mrc: "200", source_owner_id: "SNS", target_owner_id: "BLC", buyout_mode: "BEFORE_PICK", skm_id: "TC03.SKM", external_document_id: null, status: "PENDING", version: 1,
  requested_units: b.unit_keys.length, confirmed_units: 0, rejected_units: 0, pending_units: b.unit_keys.length, requires_sorting: true, requires_transit_reconciliation: false,
  composition_checked: true, created_at: "2026-10-19T12:00:00+03:00", request_accepted: true });
let lastBody = null;

async function start(b, w, h, q) {
  const p = await (await b.newContext({ viewport: { width: w, height: h } })).newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  p.on("response", r => { if (r.url().includes("/api/tradecase/")) res.http.push(w + " " + r.request().method() + " " + r.status() + " " + r.url().replace(/^.*\/api\//, "/api/").slice(0, 120)); });
  await p.route(u => u.href.includes(":8088/api/"), async r => {
    const req = r.request(), m = req.method(), u = req.url();
    if (m === "OPTIONS") return r.continue();
    if (m === "GET") {
      if (/\/buyouts\/UI\./.test(u)) return u.includes("/units") ? r.fulfill({ json: { warehouse_id: +WH, items: [], has_more: false, next_after: null }, headers: cors }) : r.fulfill({ json: fakeBuyout(lastBody), headers: cors });
      if (afterPick && u.includes("/documents/ORDER/C2")) { const resp = await r.fetch(); const j = await resp.json(); j.payload.buyout_mode = "AFTER_PICK"; return r.fulfill({ json: j, headers: cors }); }
      if (late && u.includes("/warehouses/" + WH + "/buyouts?")) { await new Promise(x => setTimeout(x, 3000)); }
      return r.continue();
    }
    if (u.endsWith("/stock/sort")) {
      const body = JSON.parse(req.postData()), md = sortMode.shift() || "abort"; res.posts.push({ mode: "sort:" + md, body });
      if (md === "abort") return r.abort("connectionreset");
      return r.fulfill({ json: { operation_id: body.operation_id, status: "APPLIED", source_uid: body.source_pallet, uid: "PART:fixtureFixtureFixtureFixtureFixtureFixtureFi", from_cell: body.source_cell,
        cell: body.target_cell, base_quantity: String(body.scans.length), base_uom: "EA", regulatory_composition_status: "PENDING", outbox_id: 1 }, headers: cors });
    }
    if (!u.endsWith("/buyouts")) { res.liveWrites.push(m + " " + u); return r.abort(); }
    const body = JSON.parse(req.postData()), md = mode.shift() || "abort"; res.posts.push({ mode: md, body }); lastBody = body;
    if (md === "abort") return r.abort("connectionreset");
    if (md.startsWith("409:")) return r.fulfill({ status: 409, json: { detail: { code: md.slice(4) } }, headers: cors });
    await new Promise(x => setTimeout(x, 300));
    return r.fulfill({ json: { ...fakeBuyout(body), replayed: md === "replay" }, headers: cors });
  });
  await p.goto(BASE + "?page=tradecase" + q);
  if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  return p;
}
const rows = p => p.locator(".tc-body .tc-table tbody tr");
const stored = p => p.evaluate(k => localStorage.getItem(k), KEY);
async function openOrder(p, id) { await chooseTabUI(p, "ORDER"); await rows(p).first().waitFor(); await p.locator(".tc-body .tc-table tbody tr", { hasText: id }).first().getByRole("button", { name: "Открыть" }).click(); await p.waitForSelector(".tc-card .tc-fields"); }
async function prepare(p, n) {
  await p.locator("[data-help-id='tradecase.buyout.create']").first().click();
  await p.fill("[data-help-id='tradecase.buyout.scan']", PALLET); await p.press("[data-help-id='tradecase.buyout.scan']", "Enter");
  await p.waitForSelector(".tc-review", { timeout: 30000 }); await p.fill("[data-help-id='tradecase.buyout.count']", String(n));
}

async function live(b, w, h) {
  const p = await start(b, w, h, "&tc_wh=" + WH + "&tc_tab=BUYOUTS"); const r = {};
  await rows(p).first().waitFor({ timeout: 30000 }); r.list = await p.locator(".tc-body section").first().innerText();
  assert(/TC5R\.17cd4aae\.C2/.test(r.list) && /в карточке/.test(r.list) && /(ответ СКМ не получен|Есть ожидающие коды)/.test(r.list), r.list); // текст состояния уточнил root (C-0138)
  const pend = p.waitForRequest(q => q.url().includes("pending_only=true")); await p.check("[data-help-id='tradecase.pending']"); await pend; await rows(p).first().waitFor(); r.pendingUrl = new URL(p.url()).searchParams.get("tc_pending");
  await p.locator(".tc-table tbody tr", { hasText: "TC5R.17cd4aae.C2" }).getByRole("button", { name: "Открыть" }).click(); await p.waitForSelector(".tc-card .tc-fields");
  await p.waitForSelector(".tc-card h4 + .tc-scroll table tbody tr", { timeout: 30000 }); r.card = await p.locator(".tc-card").innerText();
  // Значение requires_sorting живое и меняется по мере разделения root — проверяем, что состав проверен и показан явно.
  r.sorting = (r.card.match(/Разделение паллеты\s*(нужно[^\n]*|не нужно|не проверено[^\n]*)/) || [])[1];
  assert(r.sorting && !/не проверено/.test(r.sorting) && /запрос в очереди склада не означает отправку провайдеру/.test(r.card), r.card.slice(0, 900));
  await p.screenshot({ path: path.join(OUT, `b1_buyout_${w}.png`) });
  await openOrder(p, "C1"); await prepare(p, 5); r.review = await p.locator(".tc-review").innerText();
  assert(/Кодов на месте: \d+/.test(r.review) && /Будет запрошен выкуп 5 кодов/.test(r.review), r.review);
  r.untitled = await p.evaluate(() => [...document.querySelectorAll(".tc button, .tc a[role=button]")].filter(e => !(e.title || e.querySelector("title")) || !e.dataset.helpId).map(e => e.outerHTML.slice(0, 80)));
  assert.deepEqual(r.untitled, []); r.overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(r.overflow <= 0, "overflow " + r.overflow);
  await p.screenshot({ path: path.join(OUT, `b2_create_${w}.png`) });
  // Разделение: форма, сканы по Enter, дубль, счётчик, подтверждение; отправка недоступна до API_READY.
  await chooseTabUI(p, "SORT"); await p.waitForSelector(".tc-sort");
  await p.fill("[data-help-id='tradecase.sort.source']", PALLET); await p.fill("[data-help-id='tradecase.sort.from']", "T3S17cd4aae"); await p.fill("[data-help-id='tradecase.sort.to']", "FIXTURE-SORT-1");
  for (const c of ["CODE-1", "CODE-2", "CODE-1", "CODE-3"]) { await p.fill("[data-help-id='tradecase.sort.scan']", c); await p.press("[data-help-id='tradecase.sort.scan']", "Enter"); }
  r.sortCount = await p.locator(".tc-sort .tc-note b").innerText(); assert.equal(r.sortCount, "3");
  await p.click("[data-help-id='tradecase.sort.remove']"); assert.equal(await p.locator(".tc-sort .tc-note b").innerText(), "2");
  await p.check("[data-help-id='tradecase.sort.confirm']");
  r.sortButton = await p.locator("[data-help-id='tradecase.sort.send']").evaluate(e => ({ disabled: e.disabled, title: e.title, text: e.textContent }));
  assert(!r.sortButton.disabled && !/не подключена/.test(r.sortButton.title), JSON.stringify(r.sortButton)); r.sortOverflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(r.sortOverflow <= 0);
  await p.screenshot({ path: path.join(OUT, `b3_sort_${w}.png`) });
  res["live" + w] = r; res.checks.push("live_buyouts_detail_create_review_sort_form_" + w); await p.context().close();
}

async function commands(b) {
  const p = await start(b, 1440, 1000, "&tc_wh=" + WH + "&tc_tab=ORDER"); await p.evaluate(k => localStorage.removeItem(k), KEY);
  await rows(p).first().waitFor({ timeout: 30000 });
  // (1) Двойной клик → один POST (fixture 200) → открыта свежая карточка выкупа.
  mode = ["ok"]; await openOrder(p, "C1"); await prepare(p, 3); await p.locator("[data-help-id='tradecase.buyout.send']").dblclick();
  await p.waitForFunction(() => new URLSearchParams(location.search).get("tc_tab") === "BUYOUTS"); await p.waitForSelector(".tc-card .tc-fields");
  assert.equal(res.posts.length, 1); assert.equal(res.posts[0].body.unit_keys.length, 3); assert(res.posts[0].body.operation_id.startsWith("TC.BUYOUT.UI:")); assert.equal(await stored(p), null);
  res.checks.push("double_click_single_post_then_fresh_detail");
  // (2) Обрыв → сохранено и заблокировано → перезагрузка → повтор тем же телом (replay).
  mode = ["abort"]; await openOrder(p, "C1"); await prepare(p, 2); await p.click("[data-help-id='tradecase.buyout.send']");
  await p.waitForSelector(".tc-msg.warn >> text=Результат неизвестен"); assert(JSON.parse(await stored(p)).sent);
  await p.reload(); if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  await openOrder(p, "C1"); await p.locator("[data-help-id='tradecase.buyout.create']").first().click(); await p.waitForSelector("[data-help-id='tradecase.retry']");
  mode = ["replay"]; await p.click("[data-help-id='tradecase.retry']"); await p.waitForFunction(() => new URLSearchParams(location.search).get("tc_tab") === "BUYOUTS");
  assert.deepEqual(res.posts.at(-1).body, res.posts.at(-2).body); assert.equal(await stored(p), null); res.checks.push("unknown_saved_reload_exact_retry_replay");
  // (3) OPERATION_CONTENT_CONFLICT — команда сохраняется (новая вместо неизвестной не создаётся). (4) подтверждённый 409 — снята.
  mode = ["409:OPERATION_CONTENT_CONFLICT"]; await openOrder(p, "C1"); await prepare(p, 1); await p.click("[data-help-id='tradecase.buyout.send']");
  await p.waitForSelector(".tc-msg.bad >> text=команда сохранена"); assert.notEqual(await stored(p), null); await p.evaluate(k => localStorage.removeItem(k), KEY);
  mode = ["409:TRADE_BUYOUT_UNIT_ALREADY_HELD"]; await openOrder(p, "C1"); await prepare(p, 1); await p.click("[data-help-id='tradecase.buyout.send']");
  await p.waitForSelector(".tc-msg.bad >> text=уже удержана другим выкупом"); assert.equal(await stored(p), null); res.checks.push("content_conflict_kept_confirmed_409_cleared");
  // (5) Намерение другого пользователя не воспроизводится. (6) AFTER_PICK недоступен (fixture режима).
  await p.evaluate(wh => localStorage.setItem("tradecase.buyout:http://127.0.0.1:8088:someone:" + wh, JSON.stringify({ sent: true, body: { operation_id: "TC.BUYOUT.UI:aaaaaaaa-1", buyout_id: "X", basis_order_id: "C1", basis_line_id: "1", expected_basis_version: 1, unit_keys: ["a".repeat(64)] } })), WH);
  await openOrder(p, "C1"); await p.locator("[data-help-id='tradecase.buyout.create']").first().click(); await p.waitForSelector("[data-help-id='tradecase.buyout.scan']"); res.checks.push("other_user_intent_ignored");
  afterPick = true; await openOrder(p, "C2"); await p.locator("[data-help-id='tradecase.buyout.create']").first().click(); // С C-0139 режим «после сборки» включён: он требует исходный заказ, без него чтение кодов недоступно.
  await p.waitForSelector("[data-help-id='tradecase.buyout.demand']"); await p.fill("[data-help-id='tradecase.buyout.scan']", "X");
  assert(await p.locator("button[data-help-id='tradecase.buyout.load']").isDisabled()); afterPick = false; res.checks.push("after_pick_requires_demand");
  // (6b) Разделение (fixture POST): обрыв → сохранено → повтор тем же телом → новый идентификатор из ответа и следующий шаг.
  const SK = "tradecase.sort:http://127.0.0.1:8088:admin:" + WH; await p.evaluate(k => localStorage.removeItem(k), SK);
  await chooseTabUI(p, "SORT"); await p.waitForSelector(".tc-sort");
  await p.fill("[data-help-id='tradecase.sort.source']", PALLET); await p.fill("[data-help-id='tradecase.sort.from']", "T3S17cd4aae"); await p.fill("[data-help-id='tradecase.sort.to']", "FIXTURE-SORT-1");
  for (const c of ["CODE-1", "CODE-2"]) { await p.fill("[data-help-id='tradecase.sort.scan']", c); await p.press("[data-help-id='tradecase.sort.scan']", "Enter"); }
  await p.check("[data-help-id='tradecase.sort.confirm']"); sortMode = ["abort", "ok"];
  await p.locator("[data-help-id='tradecase.sort.send']").dblclick(); await p.waitForSelector(".tc-sort .tc-msg.warn >> text=Результат неизвестен");
  assert(JSON.parse(await p.evaluate(k => localStorage.getItem(k), SK)).sent); assert.equal(await p.locator("[data-help-id='tradecase.sort.source']").count(), 0);
  await p.click("[data-help-id='tradecase.retry']"); await p.waitForSelector(".tc-sort .tc-msg.ok >> text=Новый идентификатор паллеты");
  res.sortResult = await p.locator(".tc-sort .tc-msg.ok").first().innerText(); assert(/PART:fixture/.test(res.sortResult) && /не новая SSCC/.test(res.sortResult) && /ожидает подтверждения/.test(res.sortResult));
  const sp = res.posts.filter(x => x.mode.startsWith("sort:")); assert.equal(sp.length, 2); assert.deepEqual(sp[0].body, sp[1].body);
  assert.deepEqual(sp[0].body.scans, [{ system_code: "CRPT", profile_code: "TOBACCO", code: "CODE-1" }, { system_code: "CRPT", profile_code: "TOBACCO", code: "CODE-2" }]);
  assert.equal(await p.evaluate(k => localStorage.getItem(k), SK), null);
  assert.equal(await p.locator(".tc-sort .tc-note b").innerText(), "0"); assert.equal(await p.isChecked("[data-help-id='tradecase.sort.confirm']"), false);
  res.checks.push("sort_double_click_unknown_exact_retry_uid_next_step_form_cleared");
  await p.screenshot({ path: path.join(OUT, "b4_sort_result_1440.png") });
  await p.context().close();
  // (7) 403 списка выкупов (fixture) убирает данные. (8) Поздний ответ прежнего склада не появляется на новом.
  const q = await start(b, 390, 844, "&tc_wh=" + WH + "&tc_tab=BUYOUTS"); await rows(q).first().waitFor({ timeout: 30000 });
  await q.route(u => u.href.includes("/buyouts?"), r => r.request().method() === "OPTIONS" ? r.continue() : r.fulfill({ status: 403, json: { detail: { code: "ACCESS_DENIED" } }, headers: cors }));
  await q.click("[data-help-id='tradecase.refresh']"); await q.waitForSelector(".tc-body .tc-err"); assert.equal(await rows(q).count(), 0); res.checks.push("fixture_403_clears");
  await q.unroute(u => u.href.includes("/buyouts?")); late = true;
  await q.fill(".tc-head input", "225837931"); await q.fill(".tc-head input", WH); await q.waitForTimeout(200); await q.fill(".tc-head input", "225837931"); await q.waitForTimeout(3800);
  const text = await q.locator(".tc-body").innerText(); late = false; assert(!/TC5R\.17cd4aae/.test(text), "stale buyouts shown"); res.checks.push("late_response_ignored");
  await q.context().close();
}

(async () => {
  const b = await chromium.launch();
  await live(b, 1440, 1000); await live(b, 390, 844); await commands(b);
  assert.deepEqual(res.liveWrites, []); assert.deepEqual(res.errors, []); res.status = "PASS";
  res.labels = { live: "admin login + GET 211559882 (buyouts, documents, all stock unit pages)", fixture: "POST /buyouts answers, GET of UI-created buyout, 403, delay, AFTER_PICK payload change — intercepted in browser" };
  fs.writeFileSync(path.join(__dirname, "..", "c0136_result.json"), JSON.stringify(res, null, 1));
  console.log(JSON.stringify({ status: res.status, checks: res.checks, posts: res.posts.map(x => x.mode), gets: res.http.filter(x => / GET /.test(x)).length }, null, 1)); await b.close();
})().catch(e => { console.error(e.message); console.error(JSON.stringify({ checks: res.checks, errors: res.errors, posts: res.posts.map(x => x.mode), liveWrites: res.liveWrites })); process.exit(1); });

async function chooseTabUI(p, id) { const mobile=p.locator("[data-help-id=\"tradecase.mobile-tab\"]"); if(p.viewportSize().width<=600) await mobile.selectOption(id); else await p.click(`[data-help-id='tradecase.tab.${id}']`); }
