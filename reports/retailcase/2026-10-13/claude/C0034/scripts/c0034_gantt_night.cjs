// C-0034: шкала 00–24 на существующей диаграмме Ганта. 1) Реальный GET (без подмены) — ночной рейс 33564 открывает карточку и preflight;
// 2) модель (подставлена только в тесте): интервал через полночь, начатый накануне, без даты, целиком вне суток. Реальных POST нет.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const H = { "access-control-allow-origin": "*", "content-type": "application/json" };
const op = (id, code, s, e) => ({ op_id: id, tt_id: 900001, operation_code: code, ord: id, duration_min: 30, plan_start: s, plan_end: e, fact_start: null, fact_end: null, delta_min: null, note: null });
const model = [{ vehicle_id: 1, vehicle_num: "МОДЕЛЬ-НОЧЬ", vehicle_type: "тест", operations: [
  op(1, "LOADING", "2026-10-14 23:50", "2026-10-15 00:20"), op(2, "DRIVE", "2026-10-15 03:10", "2026-10-15 05:00"),
  op(3, "UNLOAD", "2026-10-15 23:30", "2026-10-16 00:40"), op(4, "DRIVE_BACK", "2026-10-16 02:00", "2026-10-16 03:00"), op(5, "REST", null, null)] }];
(async () => {
  const b = await chromium.launch(); const res = { posts: [] };
  const ctx = async (viewport) => { const c = await b.newContext({ viewport, serviceWorkers: "block" }); const p = await c.newPage();
    p.on("request", (r) => { if (r.method() !== "GET" && r.url().includes("/api/")) res.posts.push(r.method() + " " + r.url()); }); return p; };
  // 1. Реальные данные, дата рейса 33564.
  const p = await ctx({ width: 1440, height: 1000 });
  await p.goto("http://127.0.0.1:3000/?page=gantt"); await p.fill(".gantt-date-input", "2026-10-14");
  await p.waitForSelector("svg rect[aria-label]", { timeout: 60000 });
  res.real = { axis: await p.locator(".gantt-chart-wrap svg text").evaluateAll((n) => [n[0].textContent, n[n.length - 1].textContent]),
    chartW: await p.locator(".gantt-chart-wrap svg").getAttribute("width"), bars: await p.locator("svg rect[aria-label]").count(),
    firstBar: await p.locator("svg rect[aria-label]").first().getAttribute("aria-label"), scrollLeft: await p.locator(".gantt-chart-wrap").evaluate((n) => n.scrollLeft),
    offAxis: await p.locator(".gantt-offaxis details").count(), note: await p.locator(".gantt-offaxis-note").textContent() };
  await p.locator(".gantt-chart-wrap").evaluate((n) => { n.scrollLeft = 0; });
  await p.screenshot({ path: `${OUT}/g1_real_night_desktop.png` });
  await p.locator("svg rect[aria-label]").first().click(); await p.waitForSelector(".gantt-card-actions", { timeout: 15000 });
  res.real.card = await p.locator(".gantt-card-title").first().textContent();
  res.real.cardOps = (await p.locator(".gantt-card-op").allInnerTexts()).slice(0, 3).map((t) => t.replace(/\s+/g, " "));
  res.real.preflight = await p.getByRole("button", { name: /Показать расчётный маршрут/ }).count();
  res.real.oldWindowsButton = await p.getByRole("button", { name: /Оценить прибытие и разгрузку/ }).count();
  // Открытая карточка с реальным расчётным маршрутом (GET): содержимое внутри карточки, без перекрытия подложкой (C-0041).
  await p.locator('select[aria-label="Часовой пояс плановых дат"]').selectOption("Europe/Moscow");
  await p.getByRole("button", { name: /Показать расчётный маршрут/ }).click(); await p.waitForSelector(".trs-table", { timeout: 30000 });
  res.real.cardLayout = await p.evaluate(() => { const c = document.querySelector(".gantt-card").getBoundingClientRect(), t = document.querySelector(".trs").getBoundingClientRect(), card = document.querySelector(".gantt-card");
    const hit = (x, y) => document.elementFromPoint(x, y)?.closest(".gantt-card") !== null;
    return { cardInViewport: c.top >= 0 && c.bottom <= innerHeight && c.left >= 0 && c.right <= innerWidth, trsInsideCard: t.left >= c.left && t.right <= c.right,
      cardScrolls: card.scrollHeight > card.clientHeight, horizontalOverflow: card.scrollWidth - card.clientWidth, trsTopOnCard: hit(t.left + 4, Math.max(t.top + 4, c.top + 4)) }; });
  await p.screenshot({ path: `${OUT}/g2_real_card.png` });
  await p.locator(".trs").scrollIntoViewIfNeeded(); await p.screenshot({ path: `${OUT}/g2b_real_card_route.png` });
  // 2. Модель на 15.10 (не сегодня): переход «►» с 14.10, начальная прокрутка к первой операции суток.
  const q = await ctx({ width: 1440, height: 1000 });
  await q.route("**/api/admin/transport/vehicles/gantt**", (r) => r.fulfill({ status: 200, headers: H, body: JSON.stringify(r.request().url().includes("2026-10-15") ? model : []) }));
  await q.goto("http://127.0.0.1:3000/?page=gantt"); await q.fill(".gantt-date-input", "2026-10-14"); await q.click(".gantt-nav-btn >> nth=1");
  await q.waitForSelector("svg rect[aria-label]", { timeout: 30000 });
  res.model = { date: await q.inputValue(".gantt-date-input"), bars: await q.locator("svg rect[aria-label]").evaluateAll((n) => n.map((x) => x.getAttribute("aria-label"))),
    markers: await q.locator(".gantt-cont").count(), scrollLeft: await q.locator(".gantt-chart-wrap").evaluate((n) => n.scrollLeft),
    summary: await q.locator(".gantt-offaxis summary").textContent(), offAxis: await q.locator(".gantt-offaxis li").allInnerTexts() };
  await q.screenshot({ path: `${OUT}/g3_model_midnight.png` });
  await q.locator(".gantt-offaxis li button").first().click(); await q.waitForSelector(".gantt-card-title", { timeout: 10000 });
  res.model.cardFromList = await q.locator(".gantt-card-title").first().textContent();
  res.model.cardTimes = (await q.locator(".gantt-card-op").allInnerTexts()).map((t) => t.replace(/\s+/g, " "));
  // 3. Mobile, реальные данные.
  const m = await ctx({ width: 390, height: 844 });
  await m.goto("http://127.0.0.1:3000/?page=gantt"); await m.fill(".gantt-date-input", "2026-10-14"); await m.waitForSelector("svg rect[aria-label]", { timeout: 60000 });
  await m.locator(".gantt-chart-wrap").evaluate((n) => { n.scrollLeft = 0; });
  res.mobile = { pageOverflow: await m.evaluate(() => document.documentElement.scrollWidth - innerWidth), chartScrollable: await m.locator(".gantt-chart-wrap").evaluate((n) => n.scrollWidth - n.clientWidth) };
  await m.screenshot({ path: `${OUT}/g4_real_mobile.png` });
  await m.locator("svg rect[aria-label]").first().click(); await m.waitForSelector(".gantt-card-actions", { timeout: 15000 });
  res.mobile.card = await m.evaluate(() => { const c = document.querySelector(".gantt-card").getBoundingClientRect(); return { left: c.left, right: c.right, top: c.top, bottom: c.bottom, vw: innerWidth, vh: innerHeight }; });
  await m.screenshot({ path: `${OUT}/g5_real_mobile_card.png` });
  fs.writeFileSync(`${OUT}/../c0034_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
