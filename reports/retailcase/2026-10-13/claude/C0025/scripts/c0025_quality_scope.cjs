// C-0025: выбор области правила контроля из справочников. Чтение — реальный API;
// POST сохранения перехватывается и обрывается (неизвестный результат) — реальной записи нет.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch(); const res = { reads: [] };
  const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage(); let posts = 0;
  const t0 = {}; p.on("request", (r) => { t0[r.url()] = Date.now(); if (r.method() === "POST" && r.url().includes("quality-policies")) posts++; });
  p.on("response", (r) => { if (/master-data\/stores|admin\/warehouses|quality-policies/.test(r.url()) && r.request().method() === "GET") res.reads.push({ path: r.url().replace(/^.*\/api/, "/api").slice(0, 110), status: r.status(), ms: Date.now() - (t0[r.url()] || Date.now()) }); });
  await p.goto("http://127.0.0.1:5190/quality-policy.html"); await p.click("#loginFillAdmin"); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit());
  await p.waitForFunction(() => /Складов в справочнике|недоступен|Нет права/.test(document.getElementById("qsWareNote").textContent), null, { timeout: 30000 });
  res.wareNote = await p.textContent("#qsWareNote");
  await p.fill("#qsWareFind", "9807"); res.wareOptions = await p.locator("#qsWareList option").count();
  await p.selectOption("#qsWareList", "9807"); res.afterWare = { ware: await p.inputValue("#qsWare"), scope: await p.textContent("#qsScope") };
  await p.evaluate(() => { document.getElementById("qsStatus").textContent = ""; }); await p.click("#qsRead"); await p.waitForFunction(() => /прочитано|не|ошиб/i.test(document.getElementById("qsStatus").textContent), null, { timeout: 30000 });
  res.readAll = { version: await p.textContent("#qsVersion"), saveEnabled: await p.isEnabled("#qsSave") };
  // конкретный магазин: поиск, выбор клавиатурой
  await p.check('input[name=qsStoreMode][value=ONE]'); res.afterOneMode = { addr: await p.inputValue("#qsAddr"), saveEnabled: await p.isEnabled("#qsSave"), version: await p.textContent("#qsVersion") };
  await p.fill("#qsStoreFind", "own264"); await p.waitForFunction(() => document.getElementById("qsStoreList").options.length > 0, null, { timeout: 15000 });
  await p.press("#qsStoreFind", "ArrowDown"); await p.keyboard.press("Home"); await p.keyboard.press("Enter");
  await p.waitForFunction(() => /Код ERP|Карточка|не найден/.test(document.getElementById("qsStoreCard").textContent), null, { timeout: 15000 });
  res.picked = { addr: await p.inputValue("#qsAddr"), card: await p.textContent("#qsStoreCard"), scope: await p.textContent("#qsScope"), saveEnabled: await p.isEnabled("#qsSave"), version: await p.textContent("#qsVersion") };
  await p.evaluate(() => { document.getElementById("qsStatus").textContent = ""; }); await p.click("#qsRead"); await p.waitForFunction(() => /прочитано|не|ошиб/i.test(document.getElementById("qsStatus").textContent), null, { timeout: 30000 });
  res.readStore = { version: await p.textContent("#qsVersion"), saveEnabled: await p.isEnabled("#qsSave") };
  await p.screenshot({ path: `${OUT}/q1_scope_store_desktop.png`, fullPage: true });
  // смена склада сбрасывает прочитанную версию
  await p.fill("#qsWareFind", ""); const other = await p.locator("#qsWareList option").nth(2).getAttribute("value"); await p.selectOption("#qsWareList", other);
  res.afterWareChange = { ware: await p.inputValue("#qsWare"), version: await p.textContent("#qsVersion"), saveEnabled: await p.isEnabled("#qsSave") };
  // неизвестный ответ: POST обрывается, команда сохраняется с исходной областью и блокирует выбор
  await p.selectOption("#qsWareList", "9807"); await p.evaluate(() => { document.getElementById("qsStatus").textContent = ""; }); await p.click("#qsRead"); await p.waitForFunction(() => /прочитано|не|ошиб/i.test(document.getElementById("qsStatus").textContent), null, { timeout: 30000 });
  await p.route("**/api/inventory/quality-policies/**", (route) => route.request().method() === "POST" ? route.abort("failed") : route.continue());
  await p.fill("#qsReason", "MOCK C0025 unknown result check"); await p.click("#qsSave"); await p.waitForTimeout(800);
  res.unknown = { status: await p.textContent("#qsStatus"), retryVisible: await p.isVisible("#qsRetry"), wareDisabled: await p.isDisabled("#qsWareList"), storeFindDisabled: await p.isDisabled("#qsStoreFind"), searchBtnDisabled: await p.isDisabled("#qsStoreSearch"), posts,
    stored: await p.evaluate(() => { const k = Object.keys(localStorage).find((x) => x.includes("qualityPolicy")); return k ? JSON.parse(localStorage.getItem(k)) : null; }) };
  await p.screenshot({ path: `${OUT}/q2_unknown_result.png` });
  await p.reload(); await p.click("#loginFillAdmin").catch(() => {}); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit()).catch(() => {});
  await p.waitForTimeout(1500);
  res.afterReload = { ware: await p.inputValue("#qsWare"), addr: await p.inputValue("#qsAddr"), scope: await p.textContent("#qsScope"), status: await p.textContent("#qsStatus"), retryVisible: await p.isVisible("#qsRetry") };
  await p.evaluate(() => { for (const k of Object.keys(localStorage)) if (k.includes("qualityPolicy")) localStorage.removeItem(k); });
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  await m.goto("http://127.0.0.1:5190/quality-policy.html"); await m.click("#loginFillAdmin"); await m.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit());
  await m.waitForFunction(() => /Складов в справочнике/.test(document.getElementById("qsWareNote").textContent), null, { timeout: 30000 });
  await m.check('input[name=qsStoreMode][value=ONE]'); await m.fill("#qsStoreFind", "Пермь"); await m.waitForTimeout(1200);
  res.mobile = { overflow: await m.evaluate(() => document.documentElement.scrollWidth - innerWidth), found: await m.locator("#qsStoreList option").count(), note: await m.textContent("#qsStoreNote") };
  await m.locator(".qs-scope").screenshot({ path: `${OUT}/q3_scope_mobile.png` });
  fs.writeFileSync(`${OUT}/../c0025_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
