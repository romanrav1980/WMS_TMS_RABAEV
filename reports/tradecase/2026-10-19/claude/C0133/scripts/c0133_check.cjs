// C-0133: запас и привязка прихода СНС/BLC. ЖИВОЕ: вход admin и GET склада 225837931 (Vite dev 3021 с исходниками C-0133).
// FIXTURE (перехват в браузере): ответы POST /stock/bind (200, потеря связи, 403), 403 чтения. Ни один POST не доходит до сервера.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0133_BASE || "http://127.0.0.1:3021/", WH = "225837931", PALLET = "690000000545105591";
const KEY = "tradecase.bind:http://127.0.0.1:8088:admin:" + WH;
const res = { http: [], posts: [], liveWrites: [], errors: [], checks: [] };
let bindMode = [];

async function start(b, w, h, q) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  p.on("response", r => { if (r.url().includes("/api/tradecase/")) res.http.push(w + " " + r.request().method() + " " + r.status() + " " + r.url().replace(/^.*\/api\//, "/api/")); });
  await p.route(u => u.href.includes(":8088/api/"), async r => {
    const m = r.request().method();
    if (m === "GET" || m === "OPTIONS") return r.continue();
    if (!r.request().url().endsWith("/stock/bind")) { res.liveWrites.push(m + " " + r.request().url()); return r.abort(); }
    const mode = bindMode.shift() || "abort", body = JSON.parse(r.request().postData()); res.posts.push({ mode, body });
    const cors = { "access-control-allow-origin": "*" };
    if (mode === "abort") return r.abort("connectionreset");
    if (mode === "403") return r.fulfill({ status: 403, json: { detail: { code: "TRADE_OWNER_ACCESS_DENIED" } }, headers: cors });
    await new Promise(x => setTimeout(x, 400));
    return r.fulfill({ json: { warehouse_id: +WH, operation_id: body.operation_id, stock_changed: false, replayed: mode === "replay", supply_id: body.supply_id, owner_id: "SNS",
      bound_units: 250, pallet_identifier: body.scanned_pallet, mark_state: "PENDING", attributes_bound: true, outbox_id: 1 }, headers: cors });
  });
  await p.goto(BASE + "?page=tradecase" + q);
  if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  return p;
}
const tab = async (p, t) => { await chooseTabUI(p, t); await p.waitForSelector(".tc-body .tc-table tbody tr", { timeout: 30000 }); };
const openSupply = async p => { await tab(p, "SUPPLY"); await p.locator(".tc-body .tc-table tbody tr").first().getByRole("button", { name: "Открыть" }).click(); await p.waitForSelector(".tc-bind"); };
const stored = p => p.evaluate(k => localStorage.getItem(k), KEY);

async function live(b, w, h) {
  const p = await start(b, w, h, "&tc_wh=" + WH + "&tc_tab=SKU"); const r = {};
  await p.waitForSelector(".tc-body .tc-table tbody tr", { timeout: 30000 }); await tab(p, "OWNER");
  // На 390 схема скрыта стилем root (C-0132) — там «Запас» открывается вкладкой.
  if (await p.locator("[data-help-id='tradecase.flow.stock']").isVisible()) await p.click("[data-help-id='tradecase.flow.stock']"); else await chooseTabUI(p, "STOCK");
  await p.waitForSelector(".tc-body .tc-table tbody tr");
  r.tabAfterFlow = new URL(p.url()).searchParams.get("tc_tab"); assert.equal(r.tabAfterFlow, "STOCK");
  r.stock = await p.locator(".tc-body section").first().innerText();
  assert(r.stock.includes(PALLET) && /QA tobacco leaf units \(A\)/.test(r.stock) && /SNS \(SNS\)/.test(r.stock) && /250 шт./.test(r.stock) && /Итого на этой странице: 250 шт./.test(r.stock) && /не общий остаток/.test(r.stock), r.stock);
  r.codes = await p.locator(".tc-body .tc-table tbody tr").first().locator(".tc-chip").allInnerTexts(); assert.deepEqual(r.codes, ["3", "246", "1"]);
  await p.screenshot({ path: path.join(OUT, `s1_stock_${w}.png`) });
  await openSupply(p); r.supply = await p.locator(".tc-card").innerText();
  assert(r.supply.includes(PALLET) && /кодов маркировки/.test(r.supply) && !/29040545105599f1a0001/.test(r.supply.replace(/Технические сведения[\s\S]*/, "")), "codes hidden");
  r.untitled = await p.evaluate(() => [...document.querySelectorAll(".tc button, .tc a[role=button]")].filter(e => !(e.title || e.querySelector("title")) || !e.dataset.helpId).map(e => e.outerHTML.slice(0, 80)));
  assert.deepEqual(r.untitled, []); r.overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(r.overflow <= 0);
  await p.screenshot({ path: path.join(OUT, `s2_supply_${w}.png`) });
  // Смена склада: запас прежнего склада убран.
  await tab(p, "STOCK"); await p.fill(".tc-head input", "1"); await p.waitForSelector(".tc-site .tc-err"); await p.waitForTimeout(600);
  r.afterSwitchRows = await p.locator(".tc-body .tc-table tbody tr").count(); assert.equal(r.afterSwitchRows, 0);
  res["live" + w] = r; res.checks.push("live_stock_supply_names_flow_switch_" + w); await p.context().close();
}

async function bindFlows(b) {
  const p = await start(b, 1440, 1000, "&tc_wh=" + WH + "&tc_tab=SUPPLY");
  await p.evaluate(k => { localStorage.removeItem(k); }, KEY); await p.waitForSelector(".tc-body .tc-table tbody tr", { timeout: 30000 }); await openSupply(p);
  const input = p.locator(".tc-bind input");
  // (1) Enter сканера → проверка данных → отмена.
  await input.fill(PALLET); await input.press("Enter"); await p.waitForSelector(".tc-review");
  res.review = await p.locator(".tc-review").innerText(); assert(res.review.includes(PALLET) && /не принимает товар физически/.test(res.review));
  await p.screenshot({ path: path.join(OUT, "s3_review_1440.png") });
  await p.getByRole("button", { name: "Отмена" }).click(); assert.equal(await p.locator(".tc-bind input").count(), 1); assert.equal(res.posts.length, 0);
  // (2) Кнопка «Проверить» → «Привязать» двойным кликом → один POST (fixture 200) → намерение очищено.
  bindMode = ["ok"]; await p.locator(".tc-bind input").fill(PALLET); await p.click("[data-help-id='tradecase.review']");
  await p.locator("[data-help-id='tradecase.bind']").dblclick(); await p.waitForSelector(".tc-msg.ok");
  assert.equal(res.posts.length, 1); assert.equal(await stored(p), null); res.checks.push("scan_enter_and_button_double_click_single_post");
  // (3) Потеря связи → сохранено, форма заблокирована → перезагрузка → повтор тем же телом (replayed).
  bindMode = ["abort"]; await p.locator(".tc-bind input").fill(PALLET); await p.locator(".tc-bind input").press("Enter"); await p.click("[data-help-id='tradecase.bind']");
  await p.waitForSelector(".tc-msg.warn >> text=Результат неизвестен"); const s1 = JSON.parse(await stored(p)); assert(s1.sent && s1.body.operation_id.startsWith("TC.BIND.UI:"));
  assert.equal(await p.locator(".tc-bind input").count(), 0);
  await p.reload(); if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  await p.waitForSelector("[data-help-id='tradecase.retry']", { timeout: 30000 });
  bindMode = ["replay"]; await p.click("[data-help-id='tradecase.retry']"); await p.waitForSelector(".tc-msg.ok >> text=Повтор");
  assert.deepEqual(res.posts.at(-1).body, res.posts.at(-2).body); assert.equal(await stored(p), null); res.checks.push("unknown_saved_locked_reload_exact_retry_replayed");
  // (4) 403 на первой отправке — отказ, команда снята. (5) 403 после потери связи — команда сохранена.
  bindMode = ["403"]; await p.locator(".tc-bind input").fill(PALLET); await p.locator(".tc-bind input").press("Enter"); await p.click("[data-help-id='tradecase.bind']");
  await p.waitForSelector(".tc-msg.bad >> text=нет права на собственника"); assert.equal(await stored(p), null);
  bindMode = ["abort", "403"]; await p.locator(".tc-bind input").fill(PALLET); await p.locator(".tc-bind input").press("Enter"); await p.click("[data-help-id='tradecase.bind']");
  await p.waitForSelector("[data-help-id='tradecase.retry']"); await p.click("[data-help-id='tradecase.retry']"); await p.waitForSelector(".tc-msg.bad >> text=команда сохранена");
  assert.notEqual(await stored(p), null); res.checks.push("fixture_403_first_clears_after_unknown_kept");
  await p.evaluate(k => localStorage.removeItem(k), KEY);
  // (6) Намерение другого пользователя не воспроизводится. (7) Повреждённая запись блокирует новую привязку.
  await p.evaluate(wh => localStorage.setItem("tradecase.bind:http://127.0.0.1:8088:someone:" + wh, JSON.stringify({ sent: true, body: { operation_id: "TC.BIND.UI:aaaaaaaa-0000", supply_id: "SUPPLY", expected_supply_version: 1, scanned_pallet: "X" } })), WH);
  await p.click("[data-help-id='tradecase.refresh']"); await p.waitForSelector(".tc-bind input"); res.checks.push("other_user_intent_ignored");
  await p.evaluate(k => localStorage.setItem(k, "{broken"), KEY); await p.click("[aria-label='Закрыть карточку']"); await p.locator(".tc-body .tc-table tbody tr").first().getByRole("button", { name: "Открыть" }).click();
  await p.waitForSelector(".tc-bind.bad"); assert.equal(await p.locator(".tc-bind input").count(), 0); assert.equal(await stored(p), "{broken");
  await p.evaluate(k => localStorage.removeItem(k), KEY); res.checks.push("corrupt_intent_blocks_not_overwritten");
  await p.context().close();
  // (8) 403 чтения (fixture): данные запаса убраны.
  const q = await start(b, 390, 844, "&tc_wh=" + WH + "&tc_tab=STOCK"); await q.waitForSelector(".tc-body .tc-table tbody tr", { timeout: 30000 });
  await q.route(u => u.href.includes("/api/tradecase/"), r => r.request().method() === "OPTIONS" ? r.continue() : r.fulfill({ status: 403, json: { detail: { code: "TRADECASE_ACCESS_DENIED" } }, headers: { "access-control-allow-origin": "*" } }));
  await q.click("[data-help-id='tradecase.refresh']"); await q.waitForSelector(".tc-site .tc-err"); await q.waitForTimeout(500);
  assert.equal(await q.locator(".tc-body .tc-table tbody tr").count(), 0); res.checks.push("fixture_read_403_clears"); await q.context().close();
}

(async () => {
  const b = await chromium.launch();
  await live(b, 1440, 1000); await live(b, 390, 844); await bindFlows(b);
  assert.deepEqual(res.liveWrites, []); assert.deepEqual(res.errors, []); res.status = "PASS";
  res.labels = { live: "admin login + GET 225837931", fixture: "POST /stock/bind answers and read 403 intercepted in browser; no POST reached server" };
  fs.writeFileSync(path.join(__dirname, "..", "c0133_result.json"), JSON.stringify(res, null, 1));
  console.log(JSON.stringify({ status: res.status, checks: res.checks, posts: res.posts.map(x => x.mode), gets: res.http.length }, null, 1)); await b.close();
})().catch(e => { console.error(e.message); console.error(JSON.stringify({ checks: res.checks, errors: res.errors, posts: res.posts.map(x => x.mode), liveWrites: res.liveWrites })); process.exit(1); });

async function chooseTabUI(p, id) { const mobile=p.locator("[data-help-id=\"tradecase.mobile-tab\"]"); if(p.viewportSize().width<=600) await mobile.selectOption(id); else await p.click(`[data-help-id='tradecase.tab.${id}']`); }
