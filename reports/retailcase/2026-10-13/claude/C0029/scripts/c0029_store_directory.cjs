// C-0029: страница «Магазины». Поиск/карточка — реальный API; профиль: реальный GET (не установлен),
// затем сценарии «установленного» профиля на подставленных ответах (DDL ещё не применён), без записи в базу.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const ADDR = "Own264 synthetic registered store 288ec8b68a";
(async () => {
  const b = await chromium.launch(); const res = {};
  const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage(); const puts = [];
  await p.goto("http://127.0.0.1:5190/store-directory.html"); await p.click("#loginFillAdmin"); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit());
  await p.waitForFunction(() => /Показано|Ничего/.test(document.getElementById("sdSearchNote").textContent), null, { timeout: 30000 });
  res.nav = await p.locator('a[href="store-directory.html"]').count();
  await p.fill("#sdQuery", "own264"); await p.waitForFunction(() => document.querySelectorAll(".sd-item").length === 1, null, { timeout: 15000 });
  await p.locator(".sd-item").first().click(); await p.waitForFunction(() => /Профиль/.test(document.getElementById("sdProfile").textContent), null, { timeout: 20000 });
  res.real = { card: (await p.locator("#sdCard").innerText()).replace(/\s+/g, " ").slice(0, 400), profile: (await p.locator("#sdProfile .sd-note").first().textContent()), saveDisabled: await p.isDisabled("#sdSave") };
  await p.screenshot({ path: `${OUT}/s1_store_card_real.png`, fullPage: true });
  // Подставленный «установленный» профиль версии 2 и PUT: сначала обрыв, затем успешный ответ.
  let mode = "abort";
  await p.route("**/api/master-data/stores/profile**", async (route) => {
    const req = route.request();
    if (req.method() === "GET") return route.fulfill({ json: { store_addr: ADDR, installed: true, configured: true, version: 2, updated_by: "mock", updated_at: "2026-10-14T12:00:00",
      profile: { receiving_window_mode: "UNCONFIGURED", timezone_region: null, backroom_flag: true, backroom_pallets: 6, backroom_rolls: null, unattended_drop_flag: null, storage_temp_class: "AMBIENT", ramp_flag: null, ramp_height_mm: null, max_vehicle_outer_height_mm: 4000, max_vehicle_outer_length_mm: null, default_unload_method: "PALLET", loader_required: false, access_note: null }, windows: [] } });
    const body = JSON.parse(req.postData()); puts.push(body);
    if (mode === "abort") return route.abort("failed");
    return route.fulfill({ json: { store_addr: body.store_addr, installed: true, configured: true, version: body.expected_version + 1, operation_id: body.operation_id, stock_changed: false, profile: {}, windows: body.windows } });
  });
  await p.locator(".sd-item").first().click(); await p.waitForFunction(() => /Версия профиля 2/.test(document.getElementById("sdProfile").textContent), null, { timeout: 15000 });
  await p.check('input[name=mode][value=WEEKLY]');
  await p.locator('[data-day="1"] [data-add]').click(); await p.locator('[data-day="1"] [data-role=from]').fill("08:00"); await p.locator('[data-day="1"] [data-role=to]').fill("13:00");
  await p.locator('[data-day="1"] [data-add]').click(); await p.locator('[data-day="1"] .sd-interval').nth(1).locator("[data-role=from]").fill("14:00"); await p.locator('[data-day="1"] .sd-interval').nth(1).locator("[data-role=to]").fill("24:00");
  await p.fill('input[name=reason]', "MOCK C0029 weekly windows");
  await p.click("#sdSave"); await p.waitForTimeout(300);
  res.zoneRequired = { status: await p.textContent("#sdProfileStatus"), puts: puts.length };
  await p.fill('input[name=timezone_region]', "Europe/Moscow"); await p.click("#sdSave"); await p.waitForTimeout(800);
  res.unknown = { status: await p.textContent("#sdProfileStatus"), retryVisible: await p.isVisible("#sdRetry"), formLocked: await p.isDisabled('input[name=timezone_region]'), puts: puts.length,
    body: puts[0] && { mode: puts[0].receiving_window_mode, tz: puts[0].timezone_region, windows: puts[0].windows, expected: puts[0].expected_version, outer: puts[0].max_vehicle_outer_height_mm } };
  await p.screenshot({ path: `${OUT}/s2_profile_unknown.png`, fullPage: true });
  mode = "ok"; await p.click("#sdRetry"); await p.waitForFunction(() => /Профиль сохранён/.test(document.getElementById("sdProfileStatus").textContent), null, { timeout: 15000 });
  res.retry = { status: await p.textContent("#sdProfileStatus"), sameBody: JSON.stringify(puts[0]) === JSON.stringify(puts[1]), puts: puts.length };
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  await m.route("**/api/master-data/stores/profile**", (route) => route.fulfill({ json: { store_addr: ADDR, installed: true, configured: false, version: 0, profile: { receiving_window_mode: "WEEKLY", timezone_region: "Europe/Moscow" }, windows: [{ weekday: 1, from_minute: 480, to_minute: 1200 }] } }));
  await m.goto("http://127.0.0.1:5190/store-directory.html?addr=" + encodeURIComponent(ADDR)); await m.click("#loginFillAdmin"); await m.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit());
  await m.waitForFunction(() => /Профиль не заполнен/.test(document.getElementById("sdProfile").textContent), null, { timeout: 20000 });
  res.mobile = { overflow: await m.evaluate(() => document.documentElement.scrollWidth - innerWidth), closedDays: await m.locator(".sd-closed").count() };
  await m.locator("#sdProfile").screenshot({ path: `${OUT}/s3_profile_mobile.png` });
  fs.writeFileSync(`${OUT}/../c0029_store_directory.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
