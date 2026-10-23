// C-0130: рабочее место СНС/BLC. ЖИВОЕ: вход admin (SessionGate) и GET TRADECASE склада 193511607 через Vite dev 3021
// (исходники C-0130; собранный 3000 требует пересборки). FIXTURE (перехват): 403, запоздавший ответ прежнего склада.
// Изменяющих запросов нет; пароль не печатается.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0130_BASE || "http://127.0.0.1:3021/";
const WH = "193511607";
const res = { base: BASE, http: [], writes: [], errors: [], runs: {}, checks: [] };

async function start(b, w, h, query) {
  const p = await (await b.newContext({ viewport: { width: w, height: h } })).newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  p.on("request", r => { if (r.url().includes(":8088/api/") && !["GET", "OPTIONS"].includes(r.method())) res.writes.push(r.method() + " " + r.url()); });
  p.on("response", r => { if (r.url().includes("/api/tradecase/")) res.http.push(w + " " + r.status() + " " + r.url().replace(/^.*\/api\//, "/api/")); });
  const t0 = Date.now();
  await p.goto(BASE + "?page=tradecase" + query);
  await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  return { p, t0 };
}
const rows = p => p.locator(".tc-body .tc-table tbody tr").count();
const untitled = p => p.evaluate(() => [...document.querySelectorAll(".tc button, .tc a[role=button]")].filter(e => !(e.title || e.querySelector("title")) || !e.dataset.helpId).map(e => e.outerHTML.slice(0, 80)));

async function main(b, w, h) {
  const { p, t0 } = await start(b, w, h, "&tc_wh=" + WH + "&tc_tab=ORDER");
  await p.waitForSelector(".tc-body .tc-table tbody tr", { timeout: 30000 }); const r = { usefulMs: Date.now() - t0 };
  r.site = await p.locator(".tc-site").innerText(); assert(/SAP_QA/.test(r.site));
  // Названия: вкладки «Товары» и «Собственники», затем заказ O1.
  for (const tab of ["SKU", "OWNER", "RECIPIENT"]) { await chooseTabUI(p, tab); await p.waitForSelector(".tc-body .tc-table tbody tr"); r["rows_" + tab] = await rows(p); }
  await chooseTabUI(p, "ORDER"); await p.waitForSelector(".tc-body .tc-table tbody tr"); r.rows_ORDER = await rows(p);
  await p.locator(".tc-table tbody tr", { hasText: "O1" }).getByRole("button", { name: "Открыть" }).click(); await p.waitForSelector(".tc-card .tc-fields");
  r.order = await p.locator(".tc-card").innerText(); assert(/Product A \(A\)/.test(r.order) && /SNS \(SNS\) → BLC \(BLC\)/.test(r.order) && /Основание принято/.test(r.order), r.order);
  r.url = new URL(p.url()).search; assert(/tc_open=O1/.test(r.url));
  r.untitled = await untitled(p); assert.deepEqual(r.untitled, []);
  r.overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(r.overflow <= 0, "overflow " + r.overflow);
  await p.screenshot({ path: path.join(OUT, `d1_order_${w}.png`), fullPage: false });
  // Рейс → связанный заказ.
  await chooseTabUI(p, "TRIP"); await p.waitForSelector(".tc-body .tc-table tbody tr"); r.rows_TRIP = await rows(p);
  await p.locator(".tc-body .tc-table tbody tr").first().getByRole("button", { name: "Открыть" }).click(); await p.waitForSelector(".tc-card .tc-list");
  r.trip = await p.locator(".tc-card").innerText(); assert(/точки маршрута в этой версии не передаются/.test(r.trip));
  await p.locator(".tc-card").getByRole("button", { name: "Открыть заказ" }).first().click(); await p.waitForFunction(() => new URLSearchParams(location.search).get("tc_tab") === "ORDER");
  await p.waitForSelector(".tc-card .tc-fields"); r.relatedOrder = new URL(p.url()).search; res.checks.push("trip_to_related_order_" + w);
  // Обмен: страница по курсору, отказ (если есть), состояния ответа.
  await chooseTabUI(p, "MESSAGES"); await p.waitForSelector(".tc-body .tc-table tbody tr"); r.rows_MESSAGES = await rows(p);
  const rejected = p.locator(".tc-table tbody tr", { hasText: "Отклонено" }); r.rejectedOnPage = await rejected.count();
  await (r.rejectedOnPage ? rejected.first() : p.locator(".tc-body .tc-table tbody tr").first()).getByRole("button", { name: "Открыть" }).click();
  await p.waitForSelector(".tc-card .tc-fields"); r.message = await p.locator(".tc-card").innerText();
  assert(/в очереди на отправку/.test(r.message) && /внешний ответ не получен/.test(r.message) && /не начато/.test(r.message), r.message);
  if (r.rejectedOnPage) assert(/Причина отказа/.test(r.message));
  await p.screenshot({ path: path.join(OUT, `d2_message_${w}.png`), fullPage: false });
  if (await p.locator("[data-help-id='tradecase.next']").count()) {
    const first = await p.locator(".tc-body .tc-table tbody tr").first().innerText();
    await p.click("[data-help-id='tradecase.next']"); await p.waitForFunction(() => new URLSearchParams(location.search).has("tc_after"));
    await p.waitForSelector(".tc-body .tc-table tbody tr"); r.page2First = (await p.locator(".tc-body .tc-table tbody tr").first().innerText()).slice(0, 60);
    assert.notEqual(r.page2First, first.slice(0, 60)); await p.click("[data-help-id='tradecase.prev']"); await p.waitForFunction(() => !new URLSearchParams(location.search).has("tc_after"));
    res.checks.push("cursor_next_prev_" + w);
  }
  // Возврат: уходим в другой раздел и возвращаемся — склад/вкладка сохранены.
  await p.click("[data-help-id='tradecase.back']"); await p.waitForTimeout(500);
  if (await p.locator(".platform-menu-toggle").isVisible()) await p.click(".platform-menu-toggle");
  await p.click("[data-help-id='shell.tradecase']"); await p.waitForSelector(".tc-body .tc-table tbody tr");
  r.restored = new URL(p.url()).search; assert(/tc_wh=193511607/.test(r.restored) && /tc_tab=MESSAGES/.test(r.restored)); res.checks.push("return_restores_context_" + w);
  // Смена склада без площадки: отказ, прежние строки и карточка убраны.
  await p.fill(".tc-head input", "1"); await p.waitForSelector(".tc-site .tc-err"); await p.waitForTimeout(800);
  r.foreign = { site: await p.locator(".tc-site").innerText(), rows: await rows(p), card: await p.locator(".tc-card").count() };
  assert(/не найдены/.test(r.foreign.site) && r.foreign.rows === 0 && r.foreign.card === 0); res.checks.push("warehouse_without_site_clears_" + w);
  res.runs[w] = r; await p.context().close();
}

async function fixtures(b) {
  // 403 (fixture): данные склада не показываются.
  let { p } = await start(b, 1440, 900, "&tc_wh=" + WH + "&tc_tab=ORDER");
  await p.route(u => u.href.includes("/api/tradecase/"), r => r.request().method() === "OPTIONS" ? r.continue()
    : r.fulfill({ status: 403, json: { detail: { code: "TRADECASE_ACCESS_DENIED" } }, headers: { "access-control-allow-origin": "*" } }));
  await p.waitForSelector(".tc-body .tc-table tbody tr", { timeout: 30000 }).catch(() => {});
  await p.click("[data-help-id='tradecase.refresh']"); await p.waitForSelector(".tc-site .tc-err");
  res.fixture403 = { site: await p.locator(".tc-site").innerText(), rows: await rows(p) }; assert(/Нет права/.test(res.fixture403.site) && res.fixture403.rows === 0);
  res.checks.push("fixture_403_clears"); await p.context().close();
  // Запоздавший ответ прежнего склада (fixture: реальный ответ задержан на 3 с) не попадает на экран нового склада.
  ({ p } = await start(b, 1440, 900, "&tc_tab=ORDER"));
  await p.waitForSelector(".tc-head input");
  await p.route(u => u.href.includes("/warehouses/" + WH + "/documents/ORDER"), async r => { await new Promise(x => setTimeout(x, 3000)); r.continue(); });
  await p.fill(".tc-head input", WH); await p.waitForTimeout(300); await p.fill(".tc-head input", "1"); await p.waitForTimeout(4000);
  res.fixtureLate = { rows: await rows(p), url: new URL(p.url()).search }; assert.equal(res.fixtureLate.rows, 0); res.checks.push("fixture_late_response_ignored");
  await p.context().close();
  // Курсор на реальных данных: тест переписывает limit=50 → 5 в запросе сообщений, ответы — живые (GET).
  ({ p } = await start(b, 1440, 900, "&tc_wh=" + WH + "&tc_tab=MESSAGES"));
  await p.route(u => u.href.includes("/warehouses/" + WH + "/messages?"), r => r.continue({ url: r.request().url().replace("limit=50", "limit=5") }));
  await p.waitForSelector(".tc-body .tc-table tbody tr", { timeout: 30000 });
  const page1 = await p.locator(".tc-body .tc-table tbody tr").allInnerTexts();
  const next = p.waitForResponse(r => r.url().includes("/messages?") && r.url().includes("after="));
  await p.click("[data-help-id='tradecase.next']"); const body2 = await (await next).json(); await p.waitForTimeout(300);
  const page2 = await p.locator(".tc-body .tc-table tbody tr").allInnerTexts();
  await p.reload(); await p.fill("input[autocomplete=username]", "admin").catch(() => {}); 
  if (await p.locator("input[type=password]").count()) { await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  await p.waitForSelector(".tc-body .tc-table tbody tr", { timeout: 30000 }); const reloaded = await p.locator(".tc-body .tc-table tbody tr").allInnerTexts();
  const first = p.waitForResponse(r => r.url().includes("/messages?") && !r.url().includes("after="));
  await p.click("[data-help-id='tradecase.first']"); await first; await p.waitForTimeout(300);
  const back = await p.locator(".tc-body .tc-table tbody tr").allInnerTexts();
  res.cursor = { page1: page1.length, page2: page2.length, page2Events: body2.items.map(i => i.event_id.slice(0, 8)), reloadKeepsPage2: reloaded.join() === page2.join(), firstAgain: back.join() === page1.join() };
  assert(res.cursor.page1 === 5 && res.cursor.page2 > 0 && res.cursor.reloadKeepsPage2 && res.cursor.firstAgain, JSON.stringify(res.cursor));
  res.checks.push("cursor_next_reload_first_live_limit5"); await p.context().close();
}

(async () => {
  const b = await chromium.launch();
  await main(b, 1440, 1000); await main(b, 390, 844); await fixtures(b);
  assert.deepEqual(res.writes, []); assert.deepEqual(res.errors, []); res.status = "PASS";
  fs.writeFileSync(path.join(__dirname, "..", "c0130_result.json"), JSON.stringify(res, null, 1));
  console.log(JSON.stringify({ status: res.status, checks: res.checks, useful: Object.fromEntries(Object.entries(res.runs).map(([w, r]) => [w, r.usefulMs])), rejected: res.runs[1440]?.rejectedOnPage, http: res.http.length }, null, 1));
  await b.close();
})().catch(e => { console.error(e.message); console.error(JSON.stringify({ checks: res.checks, errors: res.errors, writes: res.writes }).slice(0, 2000)); process.exit(1); });

async function chooseTabUI(p, id) { const mobile=p.locator("[data-help-id=\"tradecase.mobile-tab\"]"); if(p.viewportSize().width<=600) await mobile.selectOption(id); else await p.click(`[data-help-id='tradecase.tab.${id}']`); }
