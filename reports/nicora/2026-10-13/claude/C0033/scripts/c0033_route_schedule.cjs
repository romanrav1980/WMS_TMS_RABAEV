// C-0033: расчётный маршрут сервера в preflight. Реальный read-only ответ /delivery-windows для 33564,
// затем модели ответа (подставлены только в этом тесте): строгий пропуск, несколько окон, неизвестный статус.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const H = { "access-control-allow-origin": "*", "content-type": "application/json" };
const model = (over) => ({ status: "WINDOW_VIOLATION", time_zone: "Europe/Moscow", departure_at: "2026-10-14T08:00:00+03:00", return_at: "2026-10-14T16:40:00+03:00", drive_min: "210",
  depot_address: "База 9807", policy_id: "REV55_ROUTE_V6_120_15_540_ROAD24H", estimate_basis: "NATIVE_DRIVE_REST_WAIT_UNLOAD", legal_compliance_verified: false, destination_time_zones_verified: true,
  issues: [{ code: "DELIVERY_HARD_WINDOW_MISSED", address: "Магазин А" }], warnings: [{ code: "DELIVERY_SOFT_WINDOW_MISSED", address: "Магазин Б" }],
  stops: [
    { address: "Магазин А", st_numbers: ["ST-1"], window_from: "2026-10-14T09:00:00+03:00", window_to: "2026-10-14T10:00:00+03:00", arrival_at: "2026-10-14T10:20:00+03:00", service_start_at: "2026-10-14T10:20:00+03:00", service_finish_at: "2026-10-14T10:50:00+03:00", wait_min: "0", late_min: "20", unload_norm_min: "30", window_strict: 1, issues: ["DELIVERY_HARD_WINDOW_MISSED"], window_source: "ST_MATERIALIZED" },
    { address: "Магазин Б", st_numbers: ["ST-2", "ST-3"], window_from: "2026-10-14T14:00:00+03:00", window_to: "2026-10-14T18:00:00+03:00", window_source: "ST_AND_STORE_WEEKLY", profile_version: 3, store_window_mode: "WEEKLY", store_time_zone: "Europe/Moscow",
      configured_weekly_windows: [{ weekday: 3, from_minute: 480, to_minute: 780 }, { weekday: 3, from_minute: 840, to_minute: 1080 }],
      arrival_at: "2026-10-14T13:10:00+03:00", service_start_at: "2026-10-14T14:00:00+03:00", service_finish_at: "2026-10-14T14:30:00+03:00", wait_min: "50", late_min: "0", unload_norm_min: "30", window_strict: 0, issues: [] }],
  source_hash: "HASH-1", segments: [{ code: "DRIVE", start_at: "2026-10-14T08:00:00+03:00", finish_at: "2026-10-14T10:00:00+03:00" }, { code: "REST", start_at: "2026-10-14T10:00:00+03:00", finish_at: "2026-10-14T10:15:00+03:00" },
    { code: "UNLOAD", start_at: "2026-10-14T10:20:00+03:00", finish_at: "2026-10-14T10:50:00+03:00", address: "Магазин А" }, { code: "WAIT", start_at: "2026-10-14T13:10:00+03:00", finish_at: "2026-10-14T14:00:00+03:00", address: "Магазин Б" }], ...over });
(async () => {
  const b = await chromium.launch(); const res = {};
  async function page(viewport) {
    const p = await (await b.newContext({ viewport, serviceWorkers: "block" })).newPage();
    await p.route("**/api/admin/transport/vehicles/gantt**", async (route) => { const real = await (await route.fetch()).json();
      const shift = (t) => t && t.replace(/ 0(\d):/, (m, h) => " " + String(8 + Number(h)).padStart(2, "0") + ":");
      route.fulfill({ status: 200, headers: H, body: JSON.stringify(real.map((v) => ({ ...v, operations: v.operations.map((o) => ({ ...o, plan_start: shift(o.plan_start), plan_end: shift(o.plan_end) })) }))) }); });
    await p.goto("http://127.0.0.1:3000/?page=gantt"); await p.waitForSelector("svg rect[style*=pointer]", { timeout: 60000 });
    await p.locator("svg rect[style*=pointer]").first().click(); await p.waitForSelector(".gantt-card-actions", { timeout: 15000 });
    return p;
  }
  const zone = (p, z) => p.locator('select[aria-label="Часовой пояс плановых дат"]').selectOption(z);
  const show = (p) => p.getByRole("button", { name: /Показать расчётный маршрут/ }).click();
  const text = async (p) => (await p.locator(".trs").innerText()).replace(/\s+/g, " ");
  const p = await page({ width: 1440, height: 1000 });
  // 1. Реальный read-only ответ.
  await zone(p, "Europe/Moscow"); await show(p); await p.waitForSelector(".trs-status", { timeout: 30000 }); res.real = (await text(p)).slice(0, 700);
  await p.locator(".trs").screenshot({ path: `${OUT}/r1_real_33564.png` });
  // 2. Смена пояса сбрасывает результат.
  await zone(p, "UTC"); res.afterZoneChange = { hasReport: await p.locator(".trs-table").count() };
  // 3. Модель: строгий пропуск + несколько окон недельного источника; запоздавший старый ответ не перекрывает новый.
  let delay = 0, body = model({}), ctxCalls = 0;
  p.on("request", (r) => { if (r.url().includes("/time-context")) ctxCalls++; });
  await p.route("**/delivery-windows**", async (route) => { const d = delay, bd = body; if (d) await new Promise((x) => setTimeout(x, d)); route.fulfill({ status: 200, headers: H, body: JSON.stringify(bd) }); });
  await zone(p, "Europe/Moscow"); await show(p); await p.waitForSelector(".trs-table", { timeout: 15000 });
  res.model = { status: await p.textContent(".trs-status"), rows: await p.locator(".trs-table tbody tr").count(), weeklyB: await p.locator(".trs-table tbody tr").nth(1).locator(".trs-weekly").textContent(), ctxCalls,
    hardText: await p.locator(".trs-table tbody tr").nth(0).locator("td").nth(1).innerText(), weeklyText: await p.locator(".trs-table tbody tr").nth(1).locator("td").nth(1).innerText(),
    issueCode: await p.locator(".trs-bad-block code").first().textContent(), warning: (await p.locator(".trs-warn-block").innerText()).replace(/\s+/g, " ").slice(0, 120) };
  await p.locator(".trs summary", { hasText: "Лента" }).click(); res.timeline = await p.locator(".trs-timeline li").allInnerTexts();
  await p.locator(".trs").screenshot({ path: `${OUT}/r2_model_windows_desktop.png` });
  // Старый ответ без полей настроенной недели: справка не показывается, ошибки нет.
  body = model({ stops: model({}).stops.map(({ profile_version, store_window_mode, store_time_zone, configured_weekly_windows, ...x }) => x) }); await show(p);
  await p.waitForSelector(".trs-table", { timeout: 15000 }); res.oldResponse = { weeklyShown: await p.locator(".trs-weekly").count(), rows: await p.locator(".trs-table tbody tr").count() }; body = model({});
  delay = 3000; body = model({ status: "STALE_SHOULD_NOT_SHOW" }); await show(p); await p.waitForTimeout(300);
  delay = 0; await zone(p, "UTC"); body = model({ status: "MYSTERY_STATUS", time_zone: "UTC", issues: [], warnings: [] }); await show(p); await p.waitForTimeout(3500);
  res.staleAndUnknown = { status: await p.textContent(".trs-status"), tz: await p.locator(".trs-facts dd").first().textContent() };
  // 4. Мобильная ширина.
  const m = await page({ width: 390, height: 844 });
  await m.route("**/delivery-windows**", (route) => route.fulfill({ status: 200, headers: H, body: JSON.stringify(model({})) }));
  await zone(m, "Europe/Moscow"); await show(m); await m.waitForSelector(".trs-table", { timeout: 15000 });
  res.mobile = { overflow: await m.evaluate(() => document.documentElement.scrollWidth - innerWidth), tableScroll: await m.locator(".trs-table-wrap").evaluate((n) => n.scrollWidth - n.clientWidth) };
  await m.locator(".trs").screenshot({ path: `${OUT}/r3_model_mobile.png` });
  fs.writeFileSync(`${OUT}/../c0033_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
